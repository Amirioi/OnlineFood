from django.contrib import admin
from .models import Restaurant, Food


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'manager')
    search_fields = ('name', 'manager')


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'restaurant', 'price', 'status')
    search_fields = ('name', 'restaurant')
    list_filter = ('status', )
