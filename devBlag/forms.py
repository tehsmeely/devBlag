from django import forms
from django.utils import timezone
from django.core.files.images import get_image_dimensions

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
	dateStarted = forms.DateTimeField(initial=timezone.now)
	language = forms.CharField(required=False)
	engine = forms.CharField(required=False)
	projectImage = forms.ImageField(help_text="This should be 160x160") 

	def is_valid(self):
	##Override is_valid to check project image dimensions
	#this originally from http://chriskief.com/2012/12/16/override-django-form-is_valid/

		valid = super(ProjectForm, self).is_valid()
		if not valid:
			print "ProjectForm is not valid before image check"
			return valid



		imageDims = get_image_dimensions(self.cleaned_data["projectImage"])
		print valid, imageDims
		if imageDims != (160,160):
			self._errors['incorrect_size'] = 'Image is not 160x160'
			return False



		return True




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