import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from .models import Restaurant, Food
from user_app.models import User, Opinion
from order_app.models import Order


def restaurant_menu(request, rid: int, name: str):
    restaurant = Restaurant.objects.get(id=rid, name=name.replace('-', ' '))
    if not restaurant.is_open():
        return render(request, 'restaurant/closed.html', {'restaurant': restaurant})

    foods = Food.objects.filter(restaurant=restaurant, status='available')
    if request.user.is_authenticated:
        try:
            selected_items = Order.objects.get(user=request.user, restaurant=restaurant,
                                               status='pending').food_quantity()
        except Order.DoesNotExist:
            selected_items = None
    else:
        selected_items = None

    opinions = Opinion.objects.filter(restaurant=restaurant, status='confirmed')
    avg_rate = Opinion.get_average_rating(restaurant)
    context = {'restaurant': restaurant, 'foods': foods, 'selected_items': selected_items,
               'user': request.user, 'opinions': opinions, 'avg_rate': avg_rate}
    return render(request, 'restaurant/menu.html', context)


def restaurant_profile(request):
    user: User = request.user
    if user.is_authenticated:
        if user.role == 'R':
            restaurant = Restaurant.objects.get(manager=user)
            if request.method == 'POST':
                new_hours = {
                    "Monday": {"open": request.POST.get("Monday_open"),
                               "close": request.POST.get("Monday_close")},
                    "Tuesday": {"open": request.POST.get("Tuesday_open"),
                                "close": request.POST.get("Tuesday_close")},
                    "Wednesday": {"open": request.POST.get("Wednesday_open"),
                                  "close": request.POST.get("Wednesday_close")},
                    "Thursday": {"open": request.POST.get("Thursday_open"),
                                 "close": request.POST.get("Thursday_close")},
                    "Friday": {"open": request.POST.get("Friday_open"),
                               "close": request.POST.get("Friday_close")},
                    "Saturday": {"open": request.POST.get("Saturday_open"),
                                 "close": request.POST.get("Saturday_close")},
                    "Sunday": {"open": request.POST.get("Sunday_open"),
                               "close": request.POST.get("Sunday_close")}
                }
                for day, hours in new_hours.items():
                    open_time = hours.get("open")
                    close_time = hours.get("close")
                    if open_time and close_time:
                        open_hour, open_minute = map(int, open_time.split(":"))
                        close_hour, close_minute = map(int, close_time.split(":"))
                        if (close_hour < open_hour) or (close_hour == open_hour and close_minute <= open_minute):
                            messages.error(request, 'Invalid hours')
                            return redirect('RestaurantApp:restaurant_profile')

                restaurant.update_opening_hours(new_hours)
                restaurant.save()
                return redirect('RestaurantApp:restaurant_profile')

            foods = restaurant.foods.all()
            return render(request, 'restaurant/restaurant_profile.html', {'restaurant': restaurant, 'foods': foods})
    return redirect('UserApp:home')


def add_food(request):
    user: User = request.user
    if user.is_authenticated:
        if user.role == 'R':
            restaurant = Restaurant.objects.get(manager=user)
            if request.method == 'POST':
                name = request.POST.get('food_name')
                description = request.POST.get('food_description')
                category = request.POST.get('food_category')
                price = request.POST.get('food_price')
                status = request.POST.get('food_status')
                image = request.FILES.get('food_image')

                food = Food.objects.create(
                    restaurant=restaurant, name=name, description=description,
                    category=category, price=price, status=status, image=image
                )
                food.save()
                return redirect('RestaurantApp:restaurant_profile')
            else:
                return render(request, 'food/add_food.html',
                              {'status': Food.STATUS_CHOICES, 'categories': Food.CATEGORY_CHOICES})
    return redirect('UserApp:home')


def edit_food(request, fid):
    user: User = request.user
    if user.is_authenticated:
        if user.role == 'R':
            restaurant = Restaurant.objects.get(manager=user)
            food = restaurant.foods.get(id=fid)
            if request.method == 'POST':
                name = request.POST.get('new_name')
                description = request.POST.get('new_description')
                category = request.POST.get('new_category')
                price = request.POST.get('new_price')
                status = request.POST.get('new_status')
                image = request.FILES.get('new_image')

                if name:
                    food.name = name
                if description:
                    food.description = description
                if category:
                    food.category = category
                if price:
                    food.price = price
                if status:
                    food.status = status
                if image:
                    food.image = image

                food.save()

                return redirect('RestaurantApp:restaurant_profile')
            else:
                return render(request, 'food/edit_food.html',
                              {'status': Food.STATUS_CHOICES, 'categories': Food.CATEGORY_CHOICES, 'food': food})
    return redirect('UserApp:home')


def delete_food(request, fid):
    user: User = request.user
    if user.is_authenticated:
        if user.role == 'R':
            restaurant = Restaurant.objects.get(manager=user)
            food = restaurant.foods.get(id=fid)
            food.delete()
    return redirect('RestaurantApp:restaurant_profile')


def active_orders(request):
    user: User = request.user
    if user.is_authenticated:
        if user.role == 'R':
            restaurant = Restaurant.objects.get(manager=user)
            orders = Order.objects.filter(restaurant=restaurant, status='preparing')
            context = {'orders': orders, 'restaurant': restaurant}
            return render(request, 'restaurant/active_orders.html', context)
    return redirect('UserApp:home')


@csrf_exempt
def mark_as_delivering(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        order_id = data.get("order_id")
        try:
            order = Order.objects.get(id=order_id)
            order.status = 'delivered'
            order.save()
            return JsonResponse({'success': True})
        except Order.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Order not found'})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request'})
