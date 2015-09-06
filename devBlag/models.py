import os, urlparse
from django.db import models
from django.utils import timezone
from . import settings
from google.appengine.api import images
from djangae.fields import SetField
import scaffold.settings
import json


class Developer(models.Model):
	# Additional information for developer users
	user = models.OneToOneField(scaffold.settings.AUTH_USER_MODEL)
	thumbnail = models.ForeignKey('Resource_image', blank=True, null=True)
	displayName = models.CharField(max_length=200, blank=True)

	def __str__(self):
		return str(self.user.first_name) + " " + str(self.user.last_name)

	def getName(self):
		if self.displayName != "":
			return str(self.displayName)
		else:
			return self.__str__()

	def as_JSON(self):
		c = {
		"user": self.user.username,
		"thumbnail": self.thumbnail.imageFile.url,
		"displayName": self.displayName
		}
		return c
	

#title, description, image, dateStarted, inProgress, language, engine, creator, default_backgroundColour
class Project(models.Model):
	title = models.CharField(max_length=200, unique=True)
	description = models.TextField()
	image = models.ForeignKey('Resource_image')
	dateStarted = models.DateTimeField(default=timezone.now)
	inProgress = models.BooleanField(default=True)
	language = models.CharField(max_length=200, blank=True)
	engine = models.CharField(max_length=200, blank=True)
	creator = models.ForeignKey("Developer")
	default_backgroundColour = models.CharField(max_length=6, default="ffffff", help_text="The original default colour for new posts")#colour in hex "FFFFFF" with no #

	def __str__(self):
		return self.title

	def as_JSON(self):
		c = {
		"title" : self.title,
		"description" : self.description,
		"image" : self.image.imageFile.url,
		"dateStarted" : self.dateStarted.strftime("%B %w, %Y, %I:%M %p").replace("PM", "p.m.").replace("AM", "a.m"),
		"inProgress" : self.inProgress,
		"language" : self.language,
		"engine" : self.engine,
		"creator": self.creator.as_JSON(),
		"default_backgroundColour" : self.default_backgroundColour
		}
		return c



class Post(models.Model):
    #author = models.ForeignKey(scaffold.settings.AUTH_USER_MODEL)
    author = models.ForeignKey('Developer')
    title = models.CharField(max_length=200)
    body = models.TextField()
    createdDate = models.DateTimeField(default=timezone.now)
    publishedDate = models.DateTimeField(blank=True, null=True)
    project = models.ForeignKey('Project')
    backgroundColour = models.CharField(max_length=6)#colour in hex "FFFFFF" with no #
    postTags = SetField(models.CharField(max_length=10, error_messages={'max_length':"Tags should be max 10 characters each"}, blank=True), blank=True)

    def publish(self):
            self.publishedDate = timezone.now()
            self.save()

    def getTags(self):
    	##returns a pretty list of the tags in the post
    	return " ".join(self.postTags)

    def as_JSON(self):
    	c = {
    	"author": self.author.as_JSON(),
    	"title": self.title,
    	"body" : self.body,
	    "createdDate" : self.createdDate.strftime("%B %w, %Y, %I:%M %p"),
	    "publishedDate" : "" if self.publishedDate is None else self.publishedDate.strftime("%B %w, %Y, %I:%M %p"),
	    "project" : self.project.as_JSON(),
	    "backgroundColour" : self.backgroundColour,
	    "postTags" : self.getTags()
    	}
    	return c
    def __str__(self):
        return self.title


#resID,caption,imageFile,thumbnail,owner,associatedProject,public
class Resource_image(models.Model):
	#resID = models.IntegerField(unique=True)
	caption = models.TextField(blank=True)
	imageFile = models.ImageField(blank=False)
	thumbnail = models.ImageField(null=True, blank=True)
	owner = models.ForeignKey('developer')
	#associatedProject = models.ForeignKey('Project', blank=True, null=True)
	public = models.BooleanField(default=False)
	def __str__(self):
		return str(self.owner) + ": " + str(self.caption)

	
	def getServingURL(self):
		url = self.imageFile.url
		#Terrible bruteforce localhost replace:
		if scaffold.settings.DEBUG == True:
			url = url.replace("localhost", scaffold.settings.LOCAL_HOST_ADDRESS)
		return url

#resID,caption,code,language,owner,associatedProject,public
class Resource_code(models.Model):
	#resID = models.IntegerField(unique=True)
	caption = models.TextField(blank=True)
	code = models.TextField(blank=True)
	language = models.CharField(max_length=50, blank=True)
	owner = models.ForeignKey('developer')
	#associatedProject = models.ForeignKey('Project', blank=True, null=True)
	public = models.BooleanField(default=False)
	def __str__(self):
		return str(self.owner) + ": " + str(self.caption)



#resID,caption,resFile,owner,associatedProject,public
class Resource_download(models.Model):
	#resID = models.IntegerField(unique=True)
	caption = models.TextField(blank=True)
	resFile = models.FileField(blank=False)
	#filename length max is 255 : http://serverfault.com/questions/9546/filename-length-limits-on-linux
	filename = models.CharField(max_length=255)
	owner = models.ForeignKey('developer')
	#associatedProject = models.ForeignKey('Project', blank=True, null=True)
	public = models.BooleanField(default=False)
	def __str__(self):
		return str(self.owner) + ": " + str(self.caption)

	def getServingURL(self):
		url = self.resFile.url + "/" + str(self.filename)
		#Terrible bruteforce localhost replace:
		if scaffold.settings.DEBUG == True:
			url = url.replace("localhost", scaffold.settings.LOCAL_HOST_ADDRESS)

		return url