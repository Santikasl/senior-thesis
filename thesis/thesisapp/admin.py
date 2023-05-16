from django.contrib import admin
from .models import Profile, Posts, Facts, Comments

# Register your models here.

admin.site.register(Profile)
admin.site.register(Posts)
admin.site.register(Facts)
admin.site.register(Comments)
