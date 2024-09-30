from django.urls import path
from . import views

app_name = 'OrderApp'
urlpatterns = [
    path('cart/', views.temporary_cart, name='temporary_cart'),
    path('order-history/', views.orders_history, name='orders_history'),
    path('submit-food-order/', views.submit_food_order, name='submit_food_order'),
    path('checkout/', views.checkout, name='checkout'),
    path('pay/', views.pay, name='pay'),
]
