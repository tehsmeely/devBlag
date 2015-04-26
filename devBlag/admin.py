from django.contrib import admin

# Register your models here.
from .models import Post, Resource, Resource_map, Project

admin.site.register(Post)
admin.site.register(Resource_map)
admin.site.register(Resource)
admin.site.register(Project)