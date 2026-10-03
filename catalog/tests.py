from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import CustomerProfile, Order, OrderItem, Product


class AuthenticationFlowTests(TestCase):
    def test_login_register_button_is_next_to_bag_outside_navigation(self):
        response = self.client.get(reverse("home"))
        content = response.content.decode()
        nav = content.split('<nav class="site-nav"', 1)[1].split("</nav>", 1)[0]
        header_actions = content.split('<div class="header-actions">', 1)[1].split("</div>", 1)[0]

        self.assertNotIn("Login/Register", nav)
        self.assertIn('href="/accounts/login/">Login/Register</a>', header_actions)
        self.assertIn('href="/cart/"', header_actions)

    def test_registration_form_places_contact_number_after_email(self):
        response = self.client.get(reverse("register"))

        self.assertEqual(
            list(response.context["form"].fields),
            ["username", "email", "contact_number", "password1", "password2"],
        )

    def test_registration_creates_user_with_hashed_password_and_logs_them_in(self):
        response = self.client.post(reverse("register"), {
            "username": "new-customer",
            "email": "new@example.com",
            "contact_number": "+1 555 010 2040",
            "password1": "A-strong-password-123",
            "password2": "A-strong-password-123",
        })

        user = User.objects.get(username="new-customer")
        self.assertRedirects(response, reverse("home"))
        self.assertTrue(user.check_password("A-strong-password-123"))
        self.assertNotEqual(user.password, "A-strong-password-123")
        self.assertEqual(user.customer_profile.contact_number, "+1 555 010 2040")
        self.assertEqual(self.client.session["_auth_user_id"], str(user.pk))

    def test_registration_requires_contact_number(self):
        response = self.client.post(reverse("register"), {
            "username": "no-phone",
            "email": "no-phone@example.com",
            "password1": "A-strong-password-123",
            "password2": "A-strong-password-123",
        })

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="no-phone").exists())
        self.assertContains(response, "This field is required.")

    def test_login_rejects_wrong_password_and_accepts_email_or_contact_number(self):
        user = User.objects.create_user(
            username="returning-customer",
            email="returning@example.com",
            password="Correct-password-456",
        )
        CustomerProfile.objects.create(user=user, contact_number="+1 555 010 2041")

        response = self.client.post(reverse("login"), {
            "username": user.email,
            "password": "incorrect-password",
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please enter a correct email address or contact number and password.")
        self.assertNotIn("_auth_user_id", self.client.session)

        response = self.client.post(reverse("login"), {
            "username": user.email,
            "password": "Correct-password-456",
        })

        self.assertRedirects(response, reverse("home"))
        self.assertEqual(self.client.session["_auth_user_id"], str(user.pk))

        self.client.post(reverse("logout"))
        response = self.client.post(reverse("login"), {
            "username": "+1 555 010 2041",
            "password": "Correct-password-456",
        })
        self.assertRedirects(response, reverse("home"))
        self.assertEqual(self.client.session["_auth_user_id"], str(user.pk))

    def test_login_does_not_accept_username_as_identifier(self):
        User.objects.create_user(
            username="username-only",
            email="customer@example.com",
            password="Correct-password-456",
        )

        response = self.client.post(reverse("login"), {
            "username": "username-only",
            "password": "Correct-password-456",
        })

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_registration_rejects_duplicate_email(self):
        User.objects.create_user(username="existing", email="taken@example.com", password="Strong-pass-123")

        response = self.client.post(reverse("register"), {
            "username": "new-customer",
            "email": "TAKEN@example.com",
            "contact_number": "+1 555 010 2042",
            "password1": "A-strong-password-123",
            "password2": "A-strong-password-123",
        })

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="new-customer").exists())


class StoreFlowTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Test Bowl", slug="test-bowl", category="Table", description="A good bowl.",
            price="24.00", image_url="https://example.com/bowl.jpg", image_alt="Test bowl",
        )

    def test_add_to_bag_persists_in_session(self):
        response = self.client.post(reverse("cart_add", args=[self.product.pk]), {"quantity": 2, "next": reverse("cart")})
        self.assertRedirects(response, reverse("cart"))
        self.assertEqual(self.client.session["cart"], {str(self.product.pk): 2})
        self.assertContains(self.client.get(reverse("cart")), "₹48")

    def test_home_search_filters_products_by_name_and_preserves_query(self):
        other_product = Product.objects.create(
            name="Linen Throw", slug="linen-throw", category="Textiles", description="A soft throw.",
            price="38.00", image_url="https://example.com/throw.jpg",
        )

        response = self.client.get(reverse("home"), {"q": "linen"})

        self.assertContains(response, other_product.name)
        self.assertNotContains(response, self.product.name)
        self.assertContains(response, 'id="product-search" name="q" type="search" placeholder="Search products" value="linen"')
        self.assertLess(
            response.content.index(b'class="header-search-form"'),
            response.content.index(b"<main>"),
        )

    def test_ajax_add_to_bag_returns_updated_cart_count(self):
        response = self.client.post(
            reverse("cart_add", args=[self.product.pk]),
            {"quantity": 2},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            "success": True,
            "message": f"{self.product.name} added to your bag.",
            "cart_count": 2,
            "checkout_url": "/checkout/",
        })
        home_response = self.client.get(reverse("home"))
        self.assertContains(home_response, 'class="bag-notification"')
        self.assertNotContains(home_response, f"{self.product.name} added to your bag.")

    def test_ajax_cart_remove_returns_updated_count_and_total(self):
        remaining_product = Product.objects.create(
            name="Other Bowl", slug="other-bowl", category="Table", description="Another bowl.",
            price="19.00", image_url="https://example.com/other.jpg", image_alt="Other bowl",
        )
        self.client.post(reverse("cart_add", args=[self.product.pk]), {"quantity": 2})
        self.client.post(reverse("cart_add", args=[remaining_product.pk]), {"quantity": 1})

        response = self.client.post(
            reverse("cart_remove", args=[self.product.pk]),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            "success": True,
            "cart_count": 1,
            "total": "19.00",
            "is_empty": False,
        })
        self.assertEqual(self.client.session["cart"], {str(remaining_product.pk): 1})

        response = self.client.post(
            reverse("cart_remove", args=[remaining_product.pk]),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertJSONEqual(response.content, {
            "success": True,
            "cart_count": 0,
            "total": "0.00",
            "is_empty": True,
        })
        self.assertEqual(self.client.session["cart"], {})

    def test_each_product_card_has_a_checkout_link(self):
        Product.objects.create(
            name="Other Bowl", slug="other-bowl", category="Table", description="Another bowl.",
            price="19.00", image_url="https://example.com/other.jpg", image_alt="Other bowl",
        )

        response = self.client.get(reverse("home"))

        self.assertEqual(response.content.decode().count('class="checkout-inline"'), 2)

    def test_checkout_creates_order_and_clears_bag(self):
        self.client.post(reverse("cart_add", args=[self.product.pk]), {"quantity": 2})
        response = self.client.post(reverse("checkout"), {
            "name": "Taylor Example", "email": "taylor@example.com", "address": "12 Market Street",
            "city": "Portland", "postal_code": "97201",
        })
        order = Order.objects.get()
        self.assertRedirects(response, reverse("order_confirmation", args=[order.pk]))
        self.assertEqual(order.items.get().quantity, 2)
        self.assertEqual(order.total, 48)
        self.assertEqual(self.client.session["cart"], {})
        self.assertEqual(self.client.session["order_ids"], [order.pk])

    def test_order_history_shows_owned_items_and_delivery_progress(self):
        order = Order.objects.create(
            name="Taylor Example", email="taylor@example.com", address="12 Market Street",
            city="Portland", postal_code="97201", status="shipped",
        )
        OrderItem.objects.create(
            order=order, product=self.product, product_name=self.product.name,
            unit_price=self.product.price, quantity=2,
        )
        unrelated_order = Order.objects.create(
            name="Other Customer", email="other@example.com", address="1 Other Street",
            city="Portland", postal_code="97201",
        )
        session = self.client.session
        session["order_ids"] = [order.pk]
        session.save()

        response = self.client.get(reverse("order_history"))

        self.assertContains(response, "Test Bowl")
        self.assertContains(response, "Shipped")
        self.assertContains(response, "Processing")
        self.assertNotContains(response, f"Order #{unrelated_order.pk}")

    def test_pending_order_can_be_cancelled_from_order_history(self):
        order = Order.objects.create(
            name="Taylor Example", email="taylor@example.com", address="12 Market Street",
            city="Portland", postal_code="97201",
        )
        session = self.client.session
        session["order_ids"] = [order.pk]
        session.save()

        response = self.client.post(reverse("order_cancel", args=[order.pk]))

        self.assertRedirects(response, reverse("order_history"))
        order.refresh_from_db()
        self.assertEqual(order.status, "cancelled")
        self.assertContains(self.client.get(reverse("order_history")), "Cancelled")

    def test_shipped_order_cannot_be_cancelled(self):
        order = Order.objects.create(
            name="Taylor Example", email="taylor@example.com", address="12 Market Street",
            city="Portland", postal_code="97201", status="shipped",
        )
        session = self.client.session
        session["order_ids"] = [order.pk]
        session.save()

        response = self.client.post(reverse("order_cancel", args=[order.pk]))

        self.assertRedirects(response, reverse("order_history"))
        order.refresh_from_db()
        self.assertEqual(order.status, "shipped")

    def test_order_not_owned_by_session_cannot_be_cancelled(self):
        order = Order.objects.create(
            name="Other Customer", email="other@example.com", address="1 Other Street",
            city="Portland", postal_code="97201",
        )

        response = self.client.post(reverse("order_cancel", args=[order.pk]))

        self.assertEqual(response.status_code, 404)
        order.refresh_from_db()
        self.assertEqual(order.status, "pending")

    def test_like_product_adds_to_favorites_session(self):
        response = self.client.post(reverse("favorite_toggle", args=[self.product.pk]), {"next": reverse("home")})

        self.assertEqual(self.client.session["favorites"], [self.product.pk])
        self.assertRedirects(response, reverse("home"))

    def test_ajax_favorite_toggle_returns_updated_state_and_count(self):
        response = self.client.post(
            reverse("favorite_toggle", args=[self.product.pk]),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            "success": True,
            "is_favorite": True,
            "favorite_count": 1,
        })
        self.assertEqual(self.client.session["favorites"], [self.product.pk])

        response = self.client.post(
            reverse("favorite_toggle", args=[self.product.pk]),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertJSONEqual(response.content, {
            "success": True,
            "is_favorite": False,
            "favorite_count": 0,
        })
        self.assertEqual(self.client.session["favorites"], [])

    def test_liked_nav_hides_zero_count_and_shows_positive_count(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, 'href="/favorites/">Liked</a>')

        self.client.post(reverse("favorite_toggle", args=[self.product.pk]), {"next": reverse("home")})
        response = self.client.get(reverse("home"))

        self.assertContains(response, 'href="/favorites/">Liked <span class="bag-count favorite-count">1</span></a>')

    def test_home_links_to_separate_liked_page(self):
        response = self.client.get(reverse("home"))

        self.assertContains(response, 'href="/favorites/">Liked</a>')
        self.assertNotContains(response, 'class="liked-section"')

    def test_favorites_page_shows_only_liked_products(self):
        other_product = Product.objects.create(
            name="Other Bowl", slug="other-bowl", category="Table", description="Another bowl.",
            price="19.00", image_url="https://example.com/other.jpg", image_alt="Other bowl",
        )
        session = self.client.session
        session["favorites"] = [self.product.pk]
        session.save()

        response = self.client.get(reverse("favorites"))

        self.assertContains(response, "Test Bowl")
        self.assertContains(response, 'class="checkout-inline"')
        self.assertNotContains(response, "Other Bowl")

    def test_product_detail_has_checkout_action(self):
        response = self.client.get(reverse("product_detail", args=[self.product.slug]))

        self.assertContains(response, 'class="checkout-inline"')
