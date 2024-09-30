from django.db import models
from django.conf import settings
from restaurant_app.models import Restaurant, Food


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'), ('preparing', 'Preparing'), ('delivering', 'Delivering'), ('delivered', 'Delivered')
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='order')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='order')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return f'Order {self.id}'

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())

    def show_items(self):
        return [{'food': item.food, 'quantity': item.quantity} for item in self.items.all()]

    def food_quantity(self):
        return {item.food.id: item.quantity for item in self.items.all()}


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    food = models.ForeignKey(Food, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return str(self.id)

    def get_cost(self):
        return self.food.price * self.quantity


class Payment(models.Model):
    STATUS_CHOICES = (
        ('canceled', 'Canceled'), ('paid', 'Paid'), ('unknown', 'Unknown')
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payment')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='unknown')
    created = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=20, unique=True)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return str(self.id)
