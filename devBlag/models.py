import os
from django.db import models
from django.utils import timezone
import scaffold.settings as settings

# Create your models here.
class OldPost(models.Model):
	author = models.ForeignKey(settings.AUTH_USER_MODEL)
	title = models.CharField(max_length=200)
	text = models.TextField()
	created_date = models.DateTimeField(default=timezone.now)
	published_date = models.DateTimeField(blank=True, null=True)

	def publish(self):
		self.published_date = timezone.now()
		self.save()

	def __str__(self):
		return self.title


class Post(models.Model):
        author = models.ForeignKey(settings.AUTH_USER_MODEL)
        title = models.CharField(max_length=200)
        body = models.TextField()
        created_date = models.DateTimeField(default=timezone.now)
        published_date = models.DateTimeField(blank=True, null=True)

        def publish(self):
                self.published_date = timezone.now()
                self.save()

        def __str__(self):
                return self.title

## maps mmultiple rousources defined in Resourse_base to Post
class Resources(models.Model):
	postID = models.ForeignKey('Post')
	resID = models.OneToOneField('Resource')


	def __str__(self):
		return str(self.postID) + "->" + str(self.resID)
# this leaves resource and post independant


class Resource(models.Model):
	resID = models.IntegerField()
	filePath = models.FilePathField(path=os.path.join(settings.BASE_DIR, "devBlag", "static"),
					allow_folders=True,
					allow_files=False, 
					recursive=True)
	caption = models.TextField()
	thumbnailID = models.ForeignKey('Resources', null=True, blank=True)
	language = models.CharField(max_length=50, blank=True)
	def __str__(self):
		return str(self.resID) + ": " + str(self.caption)
