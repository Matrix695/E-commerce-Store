from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from .forms import CustomerAuthenticationForm
from . import views

urlpatterns = [
    path("accounts/register/", views.register, name="register"),
    path("accounts/login/", LoginView.as_view(
        template_name="accounts/login.html",
        authentication_form=CustomerAuthenticationForm,
        redirect_authenticated_user=True,
    ), name="login"),
    path("accounts/logout/", LogoutView.as_view(), name="logout"),
    path("products/suggestions/", views.product_suggestions, name="product_suggestions"),
    path("", views.home, name="home"),
    path("product/<slug:slug>/", views.product_detail, name="product_detail"),
    path("cart/", views.cart_view, name="cart"),
    path("cart/add/<int:product_id>/", views.cart_add, name="cart_add"),
    path("cart/update/<int:product_id>/", views.cart_update, name="cart_update"),
    path("cart/remove/<int:product_id>/", views.cart_remove, name="cart_remove"),
    path("favorites/", views.favorites, name="favorites"),
    path("favorites/toggle/<int:product_id>/", views.favorite_toggle, name="favorite_toggle"),
    path("checkout/", views.checkout, name="checkout"),
    path("orders/", views.order_history, name="order_history"),
    path("orders/<int:order_id>/cancel/", views.order_cancel, name="order_cancel"),
    path("orders/<int:order_id>/", views.order_confirmation, name="order_confirmation"),
]
