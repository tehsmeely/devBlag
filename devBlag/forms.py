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
		fields = ('title', 'body', 'project', "backgroundColour")


class LoginForm(forms.Form):
	emailAddress = forms.EmailField()
	password = forms.CharField(widget=forms.PasswordInput)