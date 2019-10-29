from django.contrib import admin
from accounts.models import UserProfile

from .models import *


# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Account)
admin.site.register(Transaction)