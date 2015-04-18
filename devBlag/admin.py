from django.contrib import admin

# Register your models here.
from .models import Post, Resource, Resources

admin.site.register(Post)
admin.site.register(Resource)
admin.site.register(Resources)
