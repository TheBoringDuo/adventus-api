import imp
from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin
from api.models import Country, City, Restaurant, Hotel

# Register your models here.

admin.site.register(User, UserAdmin)
admin.site.register(Country)
admin.site.register(Restaurant)
admin.site.register(City)
admin.site.register(Hotel)


