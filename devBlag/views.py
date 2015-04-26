from django.shortcuts import render
from django.utils import timezone
from .models import Post, Resource, Resource_map, Project
from scaffold.settings import BASE_DIR, STATIC_URL
import os, re

STATIC_PATH = os.path.join(BASE_DIR, "devBlag", "static")
RES_REGEX = re.compile("(<<id:\w>>)+")

def index(request):
	projects = Project.objects.all().order_by("title")
	##group projects in groups of 4
	#projects[subGroup1[p1, p2, p3, p4], subGroup2[p5, p6, p7, p8], subGroup3[p9, p10]]
	quadProj = []
	i = 0
	subGroup = []
	for project in projects:
		subGroup.append(project)
		if i == 3:
			quadProj.append(subGroup)
			subGroup = []
			i = 0
		else:
			i += 1
	##If there is an unfilled on left, add it on anyway
	if subGroup != []:
		quadProj.append(subGroup)
	print "projects:  ", projects
	print "quadProj:  ", quadProj
	return render(request, "devBlag/index.html", {"projects": quadProj, "STATIC_PATH":STATIC_PATH})


def post_list(request):
	posts = Post.objects.filter(publishedDate__lte=timezone.now()).order_by("publishedDate")
	
	resources = []
	for post in posts:
		postRes = []
		## for each post, grab the resources
		maps = Resource_map.objects.filter(post=post)
		for rmap in maps:
			fp = os.path.join(STATIC_PATH, rmap.resource.filePath)
			print "full fp", fp
			if os.path.isfile(fp):
				resources.append(rmap.resource)
				postRes.append(rmap.resource)
		print "\nbody before:\n", post.body
		post.body = handleBody(post.body)
		print "\nbody after:\n", post.body

	return render(request, 'devBlag/post_list.html', {'posts':posts, 'resources':resources})

def projectPosts(request, pid):
	project = Project.objects.get(id=pid)
	posts = Post.objects.filter(project=project).order_by("publishedDate")

	resources = []
	for post in posts:
		postRes = []
		## for each post, grab the resources
		maps = Resource_map.objects.filter(post=post)
		for rmap in maps:
			fp = os.path.join(STATIC_PATH, rmap.resource.filePath)
			print "full fp", fp
			if os.path.isfile(fp):
				resources.append(rmap.resource)
				postRes.append(rmap.resource)
		print "\nbody before:\n", post.body
		post.body = handleBody(post.body)
		print "\nbody after:\n", post.body

	return render(request, 'devBlag/projectPosts.html', {'posts':posts, 'resources':resources})


def handleBody(body):
## Takes the body and handles it to be ready to inject
	# linebreaks
	# resource html tags
	print "\nhandleBody before:\n", body
	#body = body.replace("\n", "<br />")
	#print "\nhandleBody before2:\n", body


	
	r = RES_REGEX.findall(body)
	for tag in r:
		print "TAGE: ", tag
		resNum = int(tag[5:-2])
		resource = Resource.objects.get(resID=resNum)
		if resource.contentType == "image":
			replaceString = "<img src='"+ os.path.join(STATIC_URL, resource.filePath) + "'>"
		else:
			print "CONTENT TYPE NOT FOUND"
			replaceString = ""
		#replaceString = "<img src='{% static " + resource.filePath + "%}'>"
		print "\nhandleBody Replace before:\n", body
		body = body.replace(tag, replaceString)
		print "\nhandleBody Replace after:\n", body
	print "\nhandleBody after:\n", body
	return body