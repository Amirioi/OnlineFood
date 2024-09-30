from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, UserRequest, Opinion
from restaurant_app.models import Restaurant
from order_app.models import Order


def home(request):
    restaurants = Restaurant.objects.all()[:5]
    return render(request, 'home.html', {'user': request.user, 'restaurants': restaurants})


def registration(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        address = request.POST.get('address')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if not phone_number:
            messages.error(request, "Phone Number required")
        elif User.objects.filter(phone_number=phone_number).exists():
            messages.error(request, "Phone Number already exists")
        elif password1 != password2:
            messages.error(request, "Passwords do not match")
        else:
            User.objects.create_user(
                phone_number=phone_number, password=password1,
                first_name=first_name, last_name=last_name, address=address
            )
            return redirect('UserApp:login')

    return render(request, 'registration/registration.html')


def user_login(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        user = authenticate(request, username=phone_number, password=password)
        if user:
            login(request, user)
            return redirect('UserApp:home')
        messages.error(request, 'Invalid username or password.')
    return render(request, 'registration/login.html')


def user_logout(request):
    logout(request)
    return redirect(request.META.get('HTTP_REFERER', 'UserApp:home'))


def user_profile(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            new_first_name = request.POST.get('new_first_name')
            new_last_name = request.POST.get('new_last_name')
            new_address = request.POST.get('new_address')

            if new_first_name:
                request.user.first_name = new_first_name
            if new_last_name:
                request.user.last_name = new_last_name
            if new_address:
                request.user.address = new_address
            request.user.save()
            return redirect('UserApp:profile')

        return render(request, 'user_profile.html', {'user': request.user})
    return redirect('UserApp:home')


def user_restaurant_requests(request):
    user: User = request.user
    if request.user.is_authenticated and user.role == 'C':
        applications = UserRequest.objects.filter(applicant=request.user)
        return render(request, 'user_restaurant_requests.html', {'user': request.user, 'applications': applications})
    return redirect('UserApp:home')


@login_required
def restaurant_registration(request):
    user: User = request.user

    if UserRequest.objects.filter(applicant=user, status='pending').exists():
        messages.error(request, "You have a request under review")
        return redirect('UserApp:user_restaurant_requests')

    if user.role != 'C':
        return redirect('UserApp:profile')

    if request.method == 'POST':
        restaurant_name = request.POST.get('restaurant_name')
        address = request.POST.get('address')
        document = request.FILES.get('pdf_document')
        image = request.FILES.get('image_profile')

        if not restaurant_name or not address:
            messages.error(request, "Invalid input")
        elif not user.first_name or not user.last_name:
            messages.error(request, "Your user information is not complete")
        else:
            UserRequest.objects.create(
                applicant=user,
                restaurant_name=restaurant_name,
                address=address,
                image=image,
                documents=document,
            )
            messages.success(request, "Your request has been successfully registered")
            return redirect('UserApp:user_restaurant_requests')

    return render(request, 'restaurant/restaurant_registration.html')


@login_required
def new_opinion(request, oid):
    user: User = request.user
    try:
        order = Order.objects.get(id=oid)
    except Order.DoesNotExist:
        return redirect('OrderApp:orders_history')
    restaurant = order.restaurant

    if order.user == user and order.status == 'delivered':
        statuses = ['pending', 'confirmed']
        if Opinion.objects.filter(user=user, order=order, status__in=statuses).exists():
            opinion_status = Opinion.objects.get(user=user, order=order).status
            messages.error(request, f"Already have opinion status: {opinion_status}")
            return redirect('OrderApp:orders_history')
        if request.method == 'POST':
            rating = int(request.POST.get('rating'))
            comment = request.POST.get('comment', '')
            if 0 <= rating <= 5:
                Opinion.objects.create(
                    user=request.user, restaurant=restaurant, order=order,
                    rating=rating, comment=comment
                )
                messages.success(request, 'opinion submitted successfully')
                return redirect('OrderApp:orders_history')
            messages.error(request, 'rate should be between 0 - 5')
            return redirect('UserApp:new_opinion', oid)
        else:
            context = {}
            return render(request, 'new_opinion.html', context)


def search(request):
    if request.method == 'POST':
        query = request.POST.get('query')
        restaurants = Restaurant.objects.filter(name__contains=query)
        return render(request, 'restaurants_list.html', {'restaurants': restaurants})
    return redirect('UserApp:home')
