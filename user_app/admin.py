from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('id', 'username', 'first_name', 'last_name', 'phone_number', 'role')
    list_filter = ('role',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone_number', 'address')}),
        ('Permissions', {'fields': ('role',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'first_name', 'last_name', 'phone_number', 'address', 'password1', 'password2')
        }),
        ('Permissions', {'fields': ('role',)}),
    )
    ordering = ('id',)
    search_fields = ('username', 'phone_number')


@admin.register(UserRequest)
class UserRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'applicant', 'restaurant_name', 'request_date', 'status')
    list_filter = ('status',)
    search_fields = ('applicant__phone_number', 'restaurant_name')


@admin.register(Opinion)
class OpinionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'restaurant', 'rating', 'comment', 'status')
    list_filter = ('status',)
    search_fields = ('user_phone_number', 'restaurant_name')
