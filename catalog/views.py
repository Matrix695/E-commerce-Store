from django.contrib import messages
from django.contrib.auth import login
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from .cart import cart_total, get_cart
from .forms import CheckoutForm, UserRegistrationForm
from .models import CustomerProfile, Order, OrderItem, Product


def register(request):
    if request.user.is_authenticated:
        return redirect("home")
    form = UserRegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            user = form.save()
            CustomerProfile.objects.create(
                user=user,
                contact_number=form.cleaned_data["contact_number"],
            )
        login(request, user)
        messages.success(request, "Your account has been created.")
        return redirect("home")
    return render(request, "accounts/register.html", {"form": form})


def home(request):
    products = Product.objects.filter(available=True)
    category = request.GET.get("category", "")
    query = request.GET.get("q", "").strip()
    if category:
        products = products.filter(category=category)
    if query:
        products = products.filter(name__icontains=query) | products.filter(description__icontains=query)
    favorite_ids = [int(pid) for pid in request.session.get("favorites", [])]
    return render(request, "catalog/home.html", {
        "products": products,
        "categories": Product.CATEGORY_CHOICES,
        "active_category": category,
        "query": query,
        "featured": Product.objects.filter(available=True, featured=True).first(),
        "favorite_ids": favorite_ids,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    related = Product.objects.filter(available=True, category=product.category).exclude(pk=product.pk)[:3]
    return render(request, "catalog/product_detail.html", {"product": product, "related": related})


def cart_view(request):
    lines = get_cart(request)
    return render(request, "catalog/cart.html", {"lines": lines, "total": cart_total(lines)})


def cart_add(request, product_id):
    if request.method != "POST":
        return redirect("home")
    product = get_object_or_404(Product, pk=product_id, available=True)
    cart = request.session.get("cart", {})
    key = str(product.pk)
    cart[key] = min(int(cart.get(key, 0)) + int(request.POST.get("quantity", 1)), 99)
    request.session["cart"] = cart
    cart_count = sum(int(quantity) for quantity in cart.values())
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({
            "success": True,
            "message": f"{product.name} added to your bag.",
            "cart_count": cart_count,
            "checkout_url": "/checkout/",
        })
    messages.success(request, f"{product.name} added to your bag.")
    return redirect(request.POST.get("next") or "cart")


def cart_update(request, product_id):
    if request.method == "POST":
        cart = request.session.get("cart", {})
        quantity = int(request.POST.get("quantity", 1))
        if quantity < 1:
            cart.pop(str(product_id), None)
        elif str(product_id) in cart:
            cart[str(product_id)] = min(quantity, 99)
        request.session["cart"] = cart
    return redirect("cart")


def cart_remove(request, product_id):
    if request.method == "POST":
        cart = request.session.get("cart", {})
        cart.pop(str(product_id), None)
        request.session["cart"] = cart
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            lines = get_cart(request)
            return JsonResponse({
                "success": True,
                "cart_count": sum(line["quantity"] for line in lines),
                "total": cart_total(lines),
                "is_empty": not lines,
            })
    return redirect("cart")


def checkout(request):
    lines = get_cart(request)
    if not lines:
        return redirect("cart")
    form = CheckoutForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            order = Order.objects.create(**form.cleaned_data)
            OrderItem.objects.bulk_create([
                OrderItem(order=order, product=line["product"], product_name=line["product"].name,
                          unit_price=line["product"].price, quantity=line["quantity"])
                for line in lines
            ])
        order_ids = request.session.get("order_ids", [])
        request.session["order_ids"] = [*order_ids, order.pk]
        request.session["cart"] = {}
        return redirect("order_confirmation", order_id=order.pk)
    return render(request, "catalog/checkout.html", {"form": form, "lines": lines, "total": cart_total(lines)})


def order_confirmation(request, order_id):
    order = get_object_or_404(Order.objects.prefetch_related("items"), pk=order_id)
    return render(request, "catalog/order_confirmation.html", {"order": order})


def favorite_toggle(request, product_id):
    if request.method != "POST":
        return redirect("home")
    product = get_object_or_404(Product, pk=product_id, available=True)
    favorite_ids = [int(pid) for pid in request.session.get("favorites", [])]
    is_favorite = product.pk not in favorite_ids
    if is_favorite:
        favorite_ids.append(product.pk)
    else:
        favorite_ids.remove(product.pk)
    request.session["favorites"] = favorite_ids
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({
            "success": True,
            "is_favorite": is_favorite,
            "favorite_count": len(favorite_ids),
        })
    if is_favorite:
        messages.success(request, f"{product.name} added to liked items.")
    else:
        messages.info(request, f"{product.name} removed from liked items.")
    return redirect(request.POST.get("next") or "favorites")


def favorites(request):
    favorite_ids = [int(pid) for pid in request.session.get("favorites", [])]
    product_map = {product.pk: product for product in Product.objects.filter(pk__in=favorite_ids, available=True)}
    liked_products = [product_map[pid] for pid in favorite_ids if pid in product_map]
    return render(request, "catalog/favorites.html", {"liked_products": liked_products})


def order_history(request):
    order_ids = request.session.get("order_ids", [])
    orders = Order.objects.filter(pk__in=order_ids).prefetch_related("items").order_by("-created_at")
    progress_steps = ["pending", "processing", "shipped", "complete"]
    for order in orders:
        order.can_cancel = order.status in {"pending", "processing"}
        order.progress_index = progress_steps.index(order.status) if order.status in progress_steps else None
    return render(request, "catalog/order_history.html", {
        "orders": orders,
        "progress_steps": progress_steps,
    })


def order_cancel(request, order_id):
    if request.method != "POST":
        return redirect("order_history")
    order_ids = request.session.get("order_ids", [])
    order = get_object_or_404(Order, pk=order_id, pk__in=order_ids)
    if order.status not in {"pending", "processing"}:
        messages.error(request, "This order can no longer be cancelled.")
        return redirect("order_history")
    order.status = "cancelled"
    order.save(update_fields=["status"])
    messages.success(request, f"Order #{order.pk} has been cancelled.")
    return redirect("order_history")
