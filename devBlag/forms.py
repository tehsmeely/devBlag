from django import forms

from .models import Post, Project


class ProjectForm(forms.ModelForm):

	class Meta:
		model = Project
		fields = (	'title','description','image','dateStarted','inProgress','language','engine')


class PostForm(forms.ModelForm):

	class Meta:
		model = Post
		fields = ('title', 'body', 'project')


