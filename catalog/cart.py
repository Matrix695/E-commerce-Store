from decimal import Decimal
from .models import Product


def get_cart(request):
    stored = request.session.get("cart", {})
    products = Product.objects.filter(id__in=stored.keys(), available=True)
    lines = []
    for product in products:
        quantity = max(1, min(int(stored.get(str(product.pk), 1)), 99))
        lines.append({"product": product, "quantity": quantity, "line_total": product.price * quantity})
    return lines


def cart_total(lines):
    return sum((line["line_total"] for line in lines), Decimal("0.00"))
