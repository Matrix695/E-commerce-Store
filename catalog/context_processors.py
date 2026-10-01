from .cart import get_cart


def cart_summary(request):
    cart = get_cart(request)
    return {"cart_count": sum(line["quantity"] for line in cart)}


def favorites_summary(request):
    favorite_ids = request.session.get("favorites", [])
    return {"favorite_count": len(favorite_ids), "favorite_ids": [int(pid) for pid in favorite_ids]}
