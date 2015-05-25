import os
from django.db import models
from django.utils import timezone
from . import settings
import scaffold.settings


class Developer(models.Model):
	# Additional information for developer users
	user = models.OneToOneField(scaffold.settings.AUTH_USER_MODEL)
	thumbnail = models.ForeignKey('Resource_image', blank=True, null=True)
	displayName = models.CharField(max_length=200, blank=True)

	def __str__(self):
		return str(self.user.first_name) + " " + str(self.user.last_name)
	

#mapping for many-to-many recording of developers to projects
class DevProj_mapping(models.Model):
	developer = models.ForeignKey('Developer')
	project = models.ForeignKey('Project')

	def __str__(self):
		return str(self.developer) + "--" + str(self.project)



class Project(models.Model):
	title = models.CharField(max_length=200, unique=True)
	description = models.TextField()
	image = models.ForeignKey('Resource_image')
	dateStarted = models.DateTimeField(default=timezone.now)
	inProgress = models.BooleanField(default=True)
	language = models.CharField(max_length=200, blank=True)
	engine = models.CharField(max_length=200, blank=True)

	def __str__(self):
		return self.title



class Post(models.Model):
    #author = models.ForeignKey(scaffold.settings.AUTH_USER_MODEL)
    author = models.ForeignKey('Developer')
    title = models.CharField(max_length=200)
    body = models.TextField()
    createdDate = models.DateTimeField(default=timezone.now)
    publishedDate = models.DateTimeField(blank=True, null=True)
    project = models.ForeignKey('Project')
    backgroundColour = models.CharField(max_length=6)#colour in hex "FFFFFF" with no #

    def publish(self):
            self.published_date = timezone.now()
            self.save()

    def __str__(self):
        return self.title

## maps mmultiple rousources defined in Resourse_base to Post
class Resource_map(models.Model):
	post = models.ForeignKey('Post')
	resource = models.ForeignKey('Resource_image')


	def __str__(self):
		return str(self.post) + "->" + str(self.resource)
# this leaves resource and post independant

# class Resource(models.Model):
# 	resID = models.IntegerField(unique=True)
# 	filePath = models.CharField(max_length=260, blank=True) #this is the full path
# 	caption = models.TextField(blank=True)
# 	contentType = models.CharField(max_length=50, help_text="(image/code)")
# 	thumbnail = models.ForeignKey('Resource', null=True, blank=True)
# 	language = models.CharField(max_length=50, blank=True)
# 	code = models.TextField(blank=True)
# 	owner = models.ForeignKey('developer')
# 	associatedProject = models.ForeignKey('Project', blank=True, null=True)
# 	def __str__(self):
# 		return str(self.resID) + ": " + str(self.caption)


class Resource(models.Model):
	resID = models.IntegerField(unique=True)
	caption = models.TextField(blank=True)
	owner = models.ForeignKey('developer')
	associatedProject = models.ForeignKey('Project', blank=True, null=True)
	def __str__(self):
		return str(self.resID) + ": " + str(self.caption)

class Resource_image(Resource):
	imageFile = models.ImageField(blank=False)
	thumbnail = models.ImageField(null=True, blank=True)

class Resource_code(Resource):
	language = models.CharField(max_length=50, blank=True)
	code = models.TextField(blank=True)

class Resource_download(Resource):
	resFile = models.FileField(blank=False)
