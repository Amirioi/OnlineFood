from django.urls import path
from . import views


app_name = 'UserApp'
urlpatterns = [
    path('', views.home, name='home'),
    path('registration/', views.registration, name='registration'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.user_profile, name='profile'),
    path('new_request/', views.restaurant_registration, name='restaurant_registration'),
    path('requests/', views.user_restaurant_requests, name='user_restaurant_requests'),
    path('new_opinion/<int:oid>/', views.new_opinion, name='new_opinion'),
    path('search/', views.search, name='search'),
]
