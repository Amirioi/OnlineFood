from django.db import models
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from datetime import datetime


def default_opening_hours():
    return {
        "Monday": {"open": "00:00", "close": "23:59"},
        "Tuesday": {"open": "00:00", "close": "23:59"},
        "Wednesday": {"open": "00:00", "close": "23:59"},
        "Thursday": {"open": "00:00", "close": "23:59"},
        "Friday": {"open": "00:00", "close": "23:59"},
        "Saturday": {"open": "00:00", "close": "23:59"},
        "Sunday": {"open": "00:00", "close": "23:59"}
    }


def food_image_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"food_{instance}.{ext}"
    return f'restaurants/{instance.restaurant}/food_images/{filename}'


def restaurant_document_path(instance, filename):
    return f'restaurants/{instance}/documents/{filename}'


def restaurant_image_path(instance, filename):
    return f'restaurants/{instance}/{filename}'


class Restaurant(models.Model):
    name = models.CharField(max_length=255)
    manager = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='restaurant', limit_choices_to={'role': 'R'}
    )
    address = models.TextField()
    date_joined = models.DateTimeField(default=timezone.now)
    opening_hours = models.JSONField(default=default_opening_hours)
    image = models.ImageField(upload_to=restaurant_image_path, null=True, blank=True)
    documents = models.FileField(upload_to=restaurant_document_path, blank=True, null=True)

    def show_opening_hours(self):
        return self.opening_hours

    def update_opening_hours(self, new_hours):
        for day, hours in new_hours.items():
            if day not in self.opening_hours:
                raise ValueError(f"Invalid day '{day}'.")
            self.opening_hours[day] = hours
        self.save()

    def get_absolute_url(self):
        return reverse('RestaurantApp:restaurant_menu', args=[self.id, self.name.replace(' ', '-')])

    def is_open(self):
        now = timezone.now()
        current_day = now.strftime('%A')
        current_time = now.time()

        opening_hours = self.opening_hours.get(current_day)
        if not opening_hours:
            return False

        open_time = datetime.strptime(opening_hours['open'], '%H:%M').time()
        close_time = datetime.strptime(opening_hours['close'], '%H:%M').time()

        return open_time <= current_time <= close_time

    def __str__(self):
        return self.name


class Food(models.Model):
    STATUS_CHOICES = (('available', 'Available'), ('unavailable', 'Unavailable'))
    CATEGORY_CHOICES = (
        ('pizza', 'Pizza'), ('sandwich', 'Sandwich'), ('pasta', 'Pasta'), ('burger', 'Burger'),
        ('salad', 'Salad'), ('drink', 'Drink'), ('other', 'Other')
    )
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='foods')
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=8, decimal_places=0)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES)
    created = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to=food_image_path, null=True, blank=True)

    def __str__(self):
        return self.name
