from django.shortcuts import render
from django.utils import timezone
from djangae.contrib.gauth.models import GaeDatastoreUser
from .models import Post, Resource, Resource_map, Project, Developer
from scaffold.settings import BASE_DIR, STATIC_URL, AUTH_USER_MODEL
from .settings import DEFAULT_POST_ORDER
import os, re

STATIC_PATH = os.path.join(BASE_DIR, "devBlag", "static")
RES_REGEX = re.compile("(<<id:\w>>)+")

def index(request):
	projects = Project.objects.all().order_by("title")
	##group projects in groups of 4
	#projects[subGroup1[p1, p2, p3, p4], subGroup2[p5, p6, p7, p8], subGroup3[p9, p10]]
	# quadProj = []
	# i = 0
	# subGroup = []
	# for project in projects:
	# 	subGroup.append(project)
	# 	if i == 3:
	# 		quadProj.append(subGroup)
	# 		subGroup = []
	# 		i = 0
	# 	else:
	# 		i += 1
	# ##If there is an unfilled on left, add it on anyway
	# if subGroup != []:
	# 	quadProj.append(subGroup)
	quadProj = sortToNumGroups(projects, 4)
	print "projects:  ", projects
	print "quadProj:  ", quadProj

	developers = Developer.objects.all()
	quadDev = sortToNumGroups(developers, 4)

	print "AUTH USER MODEL", AUTH_USER_MODEL
	return render(request, "devBlag/index.html", {"projects": quadProj, "developers": quadDev, "STATIC_PATH":STATIC_PATH})

#sorts a group into smaller subgroups of a given number
def sortToNumGroups(items, groupNum):
	groups = []
	i = 0
	group = []
	for item in items:
		group.append(item)
		if i == groupNum-1:
			groups.append(group)
			group = []
			i = 0
		else:
			i += 1
	##If there is an unfilled on left, add it on anyway
	if len(group) > 0:
		groups.append(group)

	return groups


def projectPosts(request, pid):
	project = Project.objects.get(id=pid)

	posts = Post.objects.filter(project=project).order_by("publishedDate")

	#sort by newest first "nf" or oldest first "of"
	sortCrit = request.GET.get("order", DEFAULT_POST_ORDER)
	if sortCrit not in ["nf", "of"]: #handle erroneous query values
		sortCrit = DEFAULT_POST_ORDER

	orderByCrit = request.GET.get("orderBy", DEFAULT_POST_ORDER_BY)
	if orderByCrit not in ["publishedDate", "createdDate"]: #handle erroneous query values
		orderByCrit = DEFAULT_POST_ORDER_BY




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
		replaceString = get_replaceString(resource)
		print "\nhandleBody Replace before:\n", body
		body = body.replace(tag, replaceString)
		print "\nhandleBody Replace after:\n", body
	print "\nhandleBody after:\n", body
	return body

def get_replaceString(resource):

	if resource.contentType == "image":
		return "<img src='"+ os.path.join(STATIC_URL, resource.filePath) + "'>"

	elif resource.contentType == "code":
		language = resource.language
		#return "<pre><code class='{}'>".format(language) + resource.content + "</code></pre>"
		return "<pre><code class='" + resource.language + "'>" + resource.code + "</code></pre>"

	else:
		print "CONTENT TYPE NOT FOUND"
		replaceString = ""



def developerProfile(request, did):
	developer = Developer.objects.get(user__id=did)
	latestPosts = Post.objects.all().order_by("publishedDate")[:10]
	return render(request, "devBlag/developerProfile.html", {'developer':developer, 'latestPosts':latestPosts})