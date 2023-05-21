from django.contrib import admin
from .models import Profile, Posts, Facts, Comments, Chat

# Register your models here.

admin.site.register([Profile, Posts, Facts, Comments, Chat])
