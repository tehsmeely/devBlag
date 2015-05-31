from django import forms

from .models import Post, Project

class ProjectForm(forms.ModelForm):

	class Meta:
		model = Project
		fields = (	'title','description','image','dateStarted','inProgress','language','engine')


class PostForm(forms.ModelForm):

	#Force background colour to use class "color" for the colour picker JS addin
	backgroundColour = forms.CharField(widget=forms.TextInput(attrs={'class': "color"}))

	class Meta:
		model = Post
		fields = ('title', 'body', "backgroundColour")


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