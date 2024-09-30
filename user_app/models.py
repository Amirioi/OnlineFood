from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Permission
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.conf import settings
from restaurant_app.models import Restaurant
from order_app.models import Order
from django.dispatch import receiver


def request_restaurant_document_path(instance, filename):
    return f'user_requests/{instance.applicant.id}/{filename}'


def request_restaurant_image_path(instance, filename):
    return f'user_requests/{instance.applicant.id}/{filename}'


class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, password, first_name, last_name, address):
        if not phone_number:
            raise ValueError('The Phone Number field must be set')
        if not first_name:
            raise ValueError('The First Name field must be set')
        if not last_name:
            raise ValueError('The Last Name field must be set')
        if not address:
            raise ValueError('The Address field must be set')
        if not password:
            raise ValueError('The Password field must be set')

        user = self.model(
            phone_number=phone_number, username=phone_number,
            first_name=first_name, last_name=last_name,
            address=address,
        )
        user.set_password(password)
        user.role = 'C'
        user.is_superuser = False
        user.save(using=self._db)
        return user

    def create_superuser(self, username, phone_number, password=None, **extra_fields):
        user = self.model(phone_number=phone_number, username=username, **extra_fields)
        user.set_password(password)
        user.role = 'A'
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (('A', 'Admin'), ('C', 'Customer'), ('R', 'RestaurantManager'))
    phone_regex = RegexValidator(
        regex=r"09\d{9}",
        message="Phone number must be entered in the format: '09125436798'. Up to 11 digits allowed."
    )
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=11, unique=True, validators=[phone_regex])
    username = models.CharField(max_length=255, unique=True)
    address = models.TextField()
    role = models.CharField(max_length=1, choices=ROLE_CHOICES, default='C')
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['phone_number']

    def save(self, *args, **kwargs):
        if self.role != 'A':
            self.username = self.phone_number
        if self.pk:  # Check if user is being updated
            old_user = User.objects.get(pk=self.pk)
            if self.role != old_user.role:
                self.update_permissions()
        super().save(*args, **kwargs)

    def update_permissions(self):
        role_permissions = {
            'A': Permission.objects.filter(content_type__app_label='auth'),
            'C': [],
            'R': [],
        }

        self.user_permissions.clear()

        if self.role == 'A':
            self.user_permissions.add(*role_permissions['A'])
            self.is_superuser = True
        else:
            self.username = self.phone_number
            self.is_superuser = False
            for perm_code in role_permissions.get(self.role, []):
                perm = Permission.objects.get(codename=perm_code)
                self.user_permissions.add(perm)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def is_staff(self):
        return self.role == 'A'


class UserRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'), ('confirmed', 'Confirmed'),
        ('unconfirmed', 'Unconfirmed'), ('finished', 'Finished')
    )
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                  related_name='applications', limit_choices_to={'role': 'C'})
    restaurant_name = models.CharField(max_length=255)
    address = models.TextField()
    request_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    image = models.ImageField(upload_to=request_restaurant_image_path, null=True, blank=True)
    documents = models.FileField(upload_to=request_restaurant_document_path, null=True, blank=True)

    def __str__(self):
        return f'user request {self.id}'

    class Meta:
        ordering = ('-request_date',)


@receiver(post_save, sender=UserRequest)
def handle_user_request_confirmation(sender, instance, **kwargs):
    if instance.status == 'confirmed':
        user = instance.applicant
        user.role = 'R'
        user.save()
        restaurant = Restaurant.objects.create(
            name=instance.restaurant_name,
            manager=user,
            address=instance.address,
        )
        restaurant.save()


class Opinion(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'), ('confirmed', 'Confirmed'), ('unconfirmed', 'Unconfirmed')
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Opinion by {self.user} on {self.restaurant}"

    @classmethod
    def get_average_rating(cls, restaurant):
        opinions = cls.objects.filter(restaurant=restaurant, status='confirmed')
        average_rating = opinions.aggregate(models.Avg('rating'))['rating__avg']
        return average_rating
