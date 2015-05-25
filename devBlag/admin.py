from django.contrib import admin

# Register your models here.
from .models import \
Post, Resource_image, Resource_code, Resource_download, Resource_map, Project, Developer, DevProj_mapping

admin.site.register(Post)
admin.site.register(Resource_map)

admin.site.register(Project)
admin.site.register(Developer)
admin.site.register(DevProj_mapping)

admin.site.register(Resource_image)
admin.site.register(Resource_code)
admin.site.register(Resource_download)
