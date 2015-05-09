from django.contrib import admin

# Register your models here.
from .models import Post, Resource, Resource_map, Project, Developer, DevProj_mapping

admin.site.register(Post)
admin.site.register(Resource_map)
admin.site.register(Resource)
admin.site.register(Project)
admin.site.register(Developer)
admin.site.register(DevProj_mapping)
