from decimal import Decimal
from django.db import models
from django.urls import reverse


class Product(models.Model):
    CATEGORY_CHOICES = [("Objects", "Objects"), ("Textiles", "Textiles"), ("Lighting", "Lighting"), ("Table", "Table")]
    name = models.CharField(max_length=140)
    slug = models.SlugField(unique=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image_url = models.URLField()
    image_alt = models.CharField(max_length=180, blank=True)
    featured = models.BooleanField(default=False)
    available = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("product_detail", args=[self.slug])


class Order(models.Model):
    STATUS_CHOICES = [("pending", "Pending"), ("processing", "Processing"), ("shipped", "Shipped"), ("complete", "Complete"), ("cancelled", "Cancelled")]
    name = models.CharField(max_length=120)
    email = models.EmailField()
    address = models.CharField(max_length=220)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    def __str__(self):
        return f"Order #{self.pk}"

    @property
    def total(self):
        return sum((item.line_total for item in self.items.all()), Decimal("0.00"))


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    product_name = models.CharField(max_length=140)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField()

    @property
    def line_total(self):
        return self.unit_price * self.quantity
