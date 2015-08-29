from django.contrib import admin

# Register your models here.
from .models import \
Post, Resource_image, Resource_code, Resource_download, Project, Developer

admin.site.register(Post)

admin.site.register(Project)
admin.site.register(Developer)

admin.site.register(Resource_image)
admin.site.register(Resource_code)
admin.site.register(Resource_download)
