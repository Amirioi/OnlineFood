from django.urls import path
from . import views

app_name = 'RestaurantApp'
urlpatterns = [
    path('<int:rid>/<str:name>/menu/', views.restaurant_menu, name='restaurant_menu'),
    path('profile/', views.restaurant_profile, name='restaurant_profile'),
    path('add-food/', views.add_food, name='add_food'),
    path('edit-food/<int:fid>/', views.edit_food, name='edit_food'),
    path('delete-food/<int:fid>/', views.delete_food, name='delete_food'),
    path('active-orders/', views.active_orders, name='active_orders'),
    path('mark_as_delivering/', views.mark_as_delivering, name='mark_as_delivering'),
]
