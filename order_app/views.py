from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from restaurant_app.models import Food, Restaurant
from .models import Order, OrderItem, Payment


def temporary_cart(request):
    if request.user.is_authenticated:
        orders = Order.objects.filter(user=request.user, status='pending')
        return render(request, 'order_info/temporary_cart.html', {'orders': orders})
    return redirect('UserApp:home')


def orders_history(request):
    if request.user.is_authenticated:
        orders = Order.objects.filter(
            Q(user=request.user) & (Q(status='delivered') | Q(status='preparing') | Q(status='delivering')))
        return render(request, 'order_info/orders_history.html', {'orders': orders})
    return redirect('UserApp:home')


@login_required
@csrf_exempt
def submit_food_order(request):
    if request.method == 'POST':
        restaurant_id = request.POST.get('restaurant_id')
        if not restaurant_id:
            return JsonResponse({'status': 'fail', 'message': 'Restaurant ID not provided.'}, status=400)

        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
        except Restaurant.DoesNotExist:
            return JsonResponse({'status': 'fail', 'message': 'Invalid Restaurant ID.'}, status=400)

        selected_foods = {}
        for key, value in request.POST.items():
            if key.startswith('food_'):
                try:
                    food_id = int(key.split('_')[1])
                    quantity = int(value)
                    if quantity >= 0:
                        selected_foods[food_id] = quantity
                except (ValueError, IndexError):
                    continue

        try:
            order, created = Order.objects.get_or_create(user=request.user, restaurant=restaurant, status='pending')
        except Order.MultipleObjectsReturned:
            return JsonResponse({'status': 'fail', 'message': 'Multiple pending orders found.'}, status=500)

        for food_id, quantity in selected_foods.items():
            try:
                food = Food.objects.get(id=food_id)
            except Food.DoesNotExist:
                continue

            if quantity > 0:
                OrderItem.objects.update_or_create(order=order, food=food, defaults={'quantity': quantity})
            else:
                OrderItem.objects.filter(order=order, food=food).delete()

        request.session['order_id'] = order.id
        return JsonResponse({'status': 'success', 'message': 'Order submitted successfully.'}, status=200)
    else:
        return JsonResponse({'status': 'fail', 'message': 'Invalid request method.'}, status=400)


@login_required
def checkout(request):
    if 'order_id' not in request.session:
        messages.error(request, "No active order found.")
        return redirect('UserApp:home')

    try:
        order = Order.objects.get(id=request.session['order_id'], user=request.user)
    except Order.DoesNotExist:
        messages.error(request, "Order not found.")
        return redirect('UserApp:home')

    unavailable_items = [item for item in order.items.all() if item.food.status == 'U']
    if unavailable_items:
        messages.warning(request, "Some items in your order are unavailable and have been removed.")
        for item in unavailable_items:
            item.delete()
        order.save()

    if len(order.items.all()) < 1:
        restaurant_id = order.restaurant.id
        restaurant_name = order.restaurant.name
        order.delete()
        messages.error(request, "Empty Order")
        return redirect('RestaurantApp:restaurant_menu', rid=restaurant_id, name=restaurant_name)

    if not order.restaurant.is_open():
        messages.error(request, "The restaurant is currently closed. Please try again later.")
        return redirect('UserApp:home')

    return render(request, 'order_info/checkout.html', {'order': order})


def pay(request):
    if 'order_id' not in request.session:
        messages.error(request, "Invalid order")
        return redirect('UserApp:home')

    try:
        order = Order.objects.get(id=request.session['order_id'], user=request.user)
    except Order.DoesNotExist:
        messages.error(request, "Order not found.")
        return redirect('UserApp:home')

    # tr_id = 2121211
    # Payment.objects.create(user=request.user, order=order, amount=order.get_total_cost(),
    #                        status='paid', transaction_id=tr_id)

    order.status = 'preparing'
    order.save()
    return redirect('OrderApp:orders_history')
