from django.contrib import admin
from .models import Order, OrderItem, Payment


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'food', 'quantity')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "food":
            if 'object_id' in request.resolver_match.kwargs:
                order_id = request.resolver_match.kwargs['object_id']
                order = Order.objects.get(id=order_id)
                kwargs["queryset"] = order.restaurant.foods.filter(status='available')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'restaurant', 'status', 'get_total_cost']
    list_filter = ['status']
    search_fields = ['id', 'user__username']
    inlines = [OrderItemInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'order', 'amount', 'status']
    list_filter = ['status']
    search_fields = ['id', 'user__username']
