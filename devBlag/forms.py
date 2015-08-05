from django import forms
from django.utils import timezone
from django.core.files.images import get_image_dimensions
from django.core.exceptions import ValidationError

from .models import Post, Project

# class ProjectForm(forms.ModelForm):

# 	class Meta:
# 		model = Project
# 		fields = ('title','description','image','language','engine')


# title
# description
# image
# dateStarted - auto today
# inProgress - auto 1
# language - not required
# engine - not required
# creator - auto logged in dev
# default_backgroundColour

class ProjectForm(forms.Form):
	title = forms.CharField()
	description = forms.CharField(widget=forms.Textarea)
	default_backgroundColour = forms.CharField(widget=forms.TextInput(attrs={'class': "color"}))
	dateStarted = forms.DateTimeField(initial=timezone.now)
	language = forms.CharField(required=False)
	engine = forms.CharField(required=False)
	projectImage = forms.ImageField(help_text="This should be 160x160")

	def clean_projectImage(self):
		imageDims = get_image_dimensions(self.cleaned_data.get("projectImage"))
		print imageDims
		if imageDims != (160,160):
			print "invalid image dims"
			raise ValidationError("Image is not 160x160", code="invalid")


class DeveloperForm(forms.Form):
	displayName = forms.CharField()
	developerImage = forms.ImageField(help_text="This should be 160x160")

	def clean_developerImage(self):
		imageDims = get_image_dimensions(self.cleaned_data.get("developerImage"))
		print imageDims
		if imageDims != (160,160):
			print "invalid image dims"
			raise ValidationError("Image is not 160x160", code="invalid")



class PostForm(forms.ModelForm):

	#Force background colour to use class "color" for the colour picker JS addin
	backgroundColour = forms.CharField(widget=forms.TextInput(attrs={'class': "color"}))

	class Meta:
		model = Post
		fields = ('title', 'body', "backgroundColour", "postTags")



###For the below, involving file/image uploads
#https://docs.djangoproject.com/en/1.8/ref/forms/api/#binding-uploaded-files

class ResourceImageForm(forms.Form):
	caption = forms.CharField(widget=forms.Textarea, required=False)
	imageFile = forms.ImageField()
	thumbnail = forms.ImageField(required=False)

class ResourceCodeForm(forms.Form):
	caption = forms.CharField(widget=forms.Textarea, required=False)
	language = forms.CharField(required=False)
	code = forms.CharField(widget=forms.Textarea)

class ResourceDownloadForm(forms.Form):
	caption = forms.CharField(widget=forms.Textarea, required=False)
	resFile = forms.FileField()

#						user enter		required
# Resource
# 	resID				    n       		
# 	caption				    y				n
# 	owner				    n
# 	associatedProject	    n

# Resource_image
# 	imageFile			    y				y
# 	thumbnail			    y				n

# Resource_code
# 	language			    y				n
# 	code 				    y				y

# Resource_download
# 	resFile				    y				y