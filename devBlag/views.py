from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, render_to_response, redirect
from django.utils import timezone
from django.template import RequestContext
from djangae.contrib.gauth.datastore.models import GaeDatastoreUser, Group
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers import serialize
from google.appengine.api import users
from google.appengine.api.images import get_serving_url
from .models import Post, Resource_image, Resource_code, Resource_download, Resource_map, Project, Developer
from scaffold.settings import BASE_DIR, STATIC_URL, AUTH_USER_MODEL
from .settings import DEFAULT_POST_ORDER_BY, DEFAULT_POST_ORDER
from .forms import PostForm, ResourceImageForm, ResourceCodeForm, ResourceDownloadForm
from . import helpers
import os, re, json, urlparse, random


STATIC_PATH = os.path.join(BASE_DIR, "devBlag", "static")


# TAG_REGEX = re.compile("(<<[idc]:[0-9]+>>)")
# TAG_INNER_REGEX = re.compile("<<(?P<type>[idc]):(?P<RId>[0-9]+)>>")

TAG_REGEX = re.compile("(?P<all><<(?P<type>[idc]):(?P<RId>[0-9]+)>>)")
#all:  full original tag string <<<type>:<id>>> - for replacement in the body string
#name: the contents of the square brackets. None if not present
#url: the contents of the parentheses, a vlaid url for the href of a link




##these have been replaced by a one-shot regex below
#LINK_REGEX = re.compile("""(\[[0-9a-zA-Z \+\-\.,!@#\$%\^&*\(\);\/|<>"']*\])?\((https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?\)""")
#LINK_INNER_REGEX = re.compile("""((\[(?P<text>[0-9a-zA-Z \+\-\.,!@#\$%\^&*\(\);\/|<>"']*)\])?)\((?P<url>(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?)\)""")

#links are in text as [<name>](<url>). The name and square brackets are optional, if removed the raw link is used for text
LINK_REGEX = re.compile("""(?P<all>(?:\[(?P<name>[0-9a-zA-Z \+\-\.,!@#\$%\^&*\(\);\/|<>"']*)\])?\((?P<url>(?:https?:\/\/)?(?:[\da-z\.-]+)\.(?:[a-z\.]{2,6})(?:[\/\w \.-]*)*\/?)\))""")
#all:  full original link string []() - for replacement in the body string
#name: the contents of the square brackets. None if not present
#url: the contents of the parentheses, a vlaid url for the href of a link

# View functions are labels as below:

###VIEW <url>

#all other functions are helpers and usually roughly just after the views that use them.


def getCurrentUser():
	#returns the current gauth user, using gae users api to get the user id
	currentUser = users.get_current_user()
	if currentUser is None:
		return None
	else:
		return GaeDatastoreUser.objects.get(username=str(currentUser.user_id()))


def getDeveloper():
	##returns the current Developer is there is one, None if not
	#currentUser = users.get_current_user()
	currentUser = getCurrentUser()
	if currentUser is None:
		return None
	else:
		return Developer.objects.get(user=currentUser)

def getIsDeveloper():
	##return True is logged in user is developer, false if not, or no logged in user
	#currentUser = users.get_current_user()
	currentUser = getCurrentUser()
	if currentUser is None:
		return None
	else:
		return Developer.objects.filter(user=currentUser).exists()


def getServingURLPath(blobID):
	return urlparse.urlparse(get_serving_url(blobID)).path



#### ##    ## ########  ######## ##     ##
 ##  ###   ## ##     ## ##        ##   ##
 ##  ####  ## ##     ## ##         ## ##
 ##  ## ## ## ##     ## ######      ###
 ##  ##  #### ##     ## ##         ## ##
 ##  ##   ### ##     ## ##        ##   ##
#### ##    ## ########  ######## ##     ##

###VIEW /
def index(request):
	projects = Project.objects.all().order_by("title")
	##group projects in groups of 4 for the table
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



########  ########   #######        ## ########  ######  ########
##     ## ##     ## ##     ##       ## ##       ##    ##    ##
##     ## ##     ## ##     ##       ## ##       ##          ##
########  ########  ##     ##       ## ######   ##          ##
##        ##   ##   ##     ## ##    ## ##       ##          ##
##        ##    ##  ##     ## ##    ## ##       ##    ##    ##
##        ##     ##  #######   ######  ########  ######     ##

##VIEW project/<pid>
def projectPosts(request, pid): #project id
	project = Project.objects.get(id=pid)


	#sort by newest first "nf" or oldest first "of"
	sortCrit = request.GET.get("order", DEFAULT_POST_ORDER)
	if sortCrit not in ["nf", "of"]: #handle erroneous query values
		sortCrit = DEFAULT_POST_ORDER

	orderByCrit = request.GET.get("orderBy", DEFAULT_POST_ORDER_BY)
	if orderByCrit not in ["publishedDate", "createdDate"]: #handle erroneous query values
		orderByCrit = DEFAULT_POST_ORDER_BY

	if sortCrit == "of":
		order_byStr = orderByCrit
	else:
		order_byStr = "-" + orderByCrit

	print order_byStr

	posts = Post.objects.filter(project=project).exclude(publishedDate=None).order_by(order_byStr)



	resources = []
	for post in posts:
		postRes = []
		## for each post, grab the resources
		maps = Resource_map.objects.filter(post=post)
		for rmap in maps:
			fp = os.path.join(STATIC_PATH, rmap.resource.filePath)
			#print "full fp", fp
			if os.path.isfile(fp):
				resources.append(rmap.resource)
				postRes.append(rmap.resource)
		#print "\nbody before:\n", post.body
		post.body = handleBody(post.body)
		#print "\nbody after:\n", post.body

	c = {
		'posts':posts,
		'resources':resources,
		'isDeveloper': getIsDeveloper(),
		'project' : project
	}

	return render(request, 'devBlag/projectPosts.html', c)

 ######   ######## ########    ########   #######   ######  ########  ######
##    ##  ##          ##       ##     ## ##     ## ##    ##    ##    ##    ##
##        ##          ##       ##     ## ##     ## ##          ##    ##
##   #### ######      ##       ########  ##     ##  ######     ##     ######
##    ##  ##          ##       ##        ##     ##       ##    ##          ##
##    ##  ##          ##       ##        ##     ## ##    ##    ##    ##    ##
 ######   ########    ##       ##         #######   ######     ##     ######

def getPosts(request):
	projectID = request.GET.get("projectID")
	project = Project.objects.get(id=projectID)
	#sort by newest first "nf" or oldest first "of"
	sortCrit = request.GET.get("order", DEFAULT_POST_ORDER)
	if sortCrit not in ["nf", "of"]: #handle erroneous query values
		sortCrit = DEFAULT_POST_ORDER

	orderByCrit = request.GET.get("orderDirection", "down")
	if orderByCrit not in ["publishedDate", "createdDate"]: #handle erroneous query values
		orderByCrit = DEFAULT_POST_ORDER_BY

	if sortCrit == "up":
		order_byStr = orderByCrit
	else:
		order_byStr = "-" + orderByCrit

	print order_byStr

	tagFilters = request.GET.get("tagFilterInput", "").split(" ")


	posts = Post.objects.filter(project=project).exclude(publishedDate=None)

	if len(tagFilters) > 0 and tagFilters != [""]:
		posts = posts.filter(postTags__in=tagFilters)

	posts = handlePosts(posts.order_by(order_byStr))

	

	return JsonResponse({"POSTS": [post.as_JSON() for post in posts]})
	#return JsonResponse(posts[0].as_JSON())




########  ######## ##     ## ######## ##        #######  ########  ######## ########
##     ## ##       ##     ## ##       ##       ##     ## ##     ## ##       ##     ##
##     ## ##       ##     ## ##       ##       ##     ## ##     ## ##       ##     ##
##     ## ######   ##     ## ######   ##       ##     ## ########  ######   ########
##     ## ##        ##   ##  ##       ##       ##     ## ##        ##       ##   ##
##     ## ##         ## ##   ##       ##       ##     ## ##        ##       ##    ##
########  ########    ###    ######## ########  #######  ##        ######## ##     ##

###VIEW /developer/<did>
def developerProfile(request, did):  #developer id
	developer = Developer.objects.get(user__id=did)
	latestPosts = Post.objects.filter(author=developer).order_by("-publishedDate")[:10]
	for post in latestPosts:
		post.body = handleBody(post.body)
	return render(request, "devBlag/developerProfile.html", {'developer':developer, 'latestPosts':latestPosts})







##     ##    ###    ##    ## ########  ##       ########    ########   #######  ########  ##    ##
##     ##   ## ##   ###   ## ##     ## ##       ##          ##     ## ##     ## ##     ##  ##  ##
##     ##  ##   ##  ####  ## ##     ## ##       ##          ##     ## ##     ## ##     ##   ####
######### ##     ## ## ## ## ##     ## ##       ######      ########  ##     ## ##     ##    ##
##     ## ######### ##  #### ##     ## ##       ##          ##     ## ##     ## ##     ##    ##
##     ## ##     ## ##   ### ##     ## ##       ##          ##     ## ##     ## ##     ##    ##
##     ## ##     ## ##    ## ########  ######## ########    ########   #######  ########     ##

def handlePosts(posts):
	##Easy function to call handleBody on all post bodies
	for post in posts:
		post.body = handleBody(post.body)
	return posts

def handleBody(body):
## Takes the body and handles it to be ready to inject
	# linebreaks
	# resource html tags
	print "\nhandleBody before:\n", body
	#body = body.replace("\n", "<br />")
	#print "\nhandleBody before2:\n", body

	#<<[i/d/c]:[id]>>
	#TAG_REGEX
	
	# Resources
	r = TAG_REGEX.finditer(body) 
	for tag in r:
		print "TAGE: ", tag
		#searchGroups = TAG_INNER_REGEX.search(tag)
		resType = tag.group("type")
		resID = tag.group("RId")
		if resType == "i":
			resource = Resource_image.objects.get(id=resID)
		elif resType == "c":
			resource = Resource_code.objects.get(id=resID)
		else:# resType == "d"       
			resource = Resource_download.objects.get(id=resID)

		replaceString = get_replaceString(resource, resType)

		print "\nhandleBody Replace before:\n", body
		body = body.replace(tag.group("all"), replaceString)
		print "\nhandleBody Replace after:\n", body

	# Links
	#all:  full original tag string <<<type>:<id>>> - for replacement in the body string
	#name: the contents of the square brackets. None if not present
	#url: the contents of the parentheses, a vlaid url for the href of a link
	r = LINK_REGEX.finditer(body)
	for link in r:
		url = link.group("url")
		if urlparse.urlparse(url).scheme == "":  # no scheme on url. <a> will incorrectly make it relative url
			url = "http://" + url # just slap an http:// scheme on it
		name = link.group("name")
		print "link.\nname: {}\nurl: {}".format(name, url)
		if name is None:
			name = url
		replaceString = "<a href={}>{}</a>".format(url, name)
		body = body.replace(link.group("all"), replaceString)

	print "\nhandleBody after:\n", body
	return body

def get_replaceString(resource, resType):

	if resType == "i":
		#return "<img src='"+ os.path.join(STATIC_URL, resource.filePath) + "'>"

		return "<img src='" + urlparse.urlparse(resource.imageFile.url).path + "'>"

	elif resType == "c":
		language = resource.language
		#return "<pre><code class='{}'>".format(language) + resource.content + "</code></pre>"
		return "<pre><code class='" + resource.language + "'>" + resource.code + "</code></pre>"

	elif resType == "d":
		return "<a href='" + urlparse.urlparse(resource.resFile.url).path + "'>Download</a>"

	else:
		print "CONTENT TYPE NOT FOUND"
		replaceString = ""

from django.views.decorators.csrf import csrf_exempt

   ###    ########  ########     ########  ########  ######   #######  ##     ## ########   ######  ########
  ## ##   ##     ## ##     ##    ##     ## ##       ##    ## ##     ## ##     ## ##     ## ##    ## ##
 ##   ##  ##     ## ##     ##    ##     ## ##       ##       ##     ## ##     ## ##     ## ##       ##
##     ## ##     ## ##     ##    ########  ######    ######  ##     ## ##     ## ########  ##       ######
######### ##     ## ##     ##    ##   ##   ##             ## ##     ## ##     ## ##   ##   ##       ##
##     ## ##     ## ##     ##    ##    ##  ##       ##    ## ##     ## ##     ## ##    ##  ##    ## ##
##     ## ########  ########     ##     ## ########  ######   #######   #######  ##     ##  ######  ########
###VIEW /addResource
@login_required
#@csrf_exempt
def addResource(request):
	if request.method == "POST":
		print "POST:", request.POST
		print "FILES:", request.FILES
		#Bind the correct form based on the type
		resType = request.POST.get("resType")
		if resType == "image":
			#resID,caption,imageFile,thumbnail,owner,associatedProject,public
			print "image"
			imageForm = ResourceImageForm(request.POST, request.FILES)
			if imageForm.is_valid():
				print "form:", imageForm.cleaned_data
				imageRes = Resource_image()
				#imageRes.resID = random.randrange(20, 2000)
				imageRes.caption = imageForm.cleaned_data['caption']
				imageRes.imageFile = imageForm.cleaned_data['imageFile']
				imageRes.thumbnail = imageForm.cleaned_data['thumbnail']
				imageRes.owner = getDeveloper()
				imageRes.save()
				print "Image Resource Created"
				return JsonResponse({"resourceCreated": True})
			else:
				c = {"resourceCreated": False,
				"errors" : imageForm.errors}
				return JsonResponse(c)

		if resType == "code":
			#resID,caption,code,language,owner,associatedProject,public
			print "code"
			codeForm = ResourceCodeForm(request.POST)
			if codeForm.is_valid():
				print "Code Resource Created"
				return JsonResponse({"resourceCreated": True})
			else:
				c = {"resourceCreated": False,
				"errors" : imageForm.errors}
				return JsonResponse(c)

		if resType == "download":
			#resID,caption,resFile,owner,associatedProject,public
			print "download"
			downloadForm = ResourceDownloadForm(request.POST, request.FILES)
			if downloadForm.is_valid():
				print "Download Resource Created"
				return JsonResponse({"resourceCreated": True})
			else:
				c = {"resourceCreated": False,
				"errors" : imageForm.errors}
				return JsonResponse(c)

	else:
		print "addResource should be POST only"
		return redirect("/")

########  ########  ######   #######  ##     ## ########   ######  ########    ########  #######  ########  ##     ##  ######
##     ## ##       ##    ## ##     ## ##     ## ##     ## ##    ## ##          ##       ##     ## ##     ## ###   ### ##    ##
##     ## ##       ##       ##     ## ##     ## ##     ## ##       ##          ##       ##     ## ##     ## #### #### ##
########  ######    ######  ##     ## ##     ## ########  ##       ######      ######   ##     ## ########  ## ### ##  ######
##   ##   ##             ## ##     ## ##     ## ##   ##   ##       ##          ##       ##     ## ##   ##   ##     ##       ##
##    ##  ##       ##    ## ##     ## ##     ## ##    ##  ##    ## ##          ##       ##     ## ##    ##  ##     ## ##    ##
##     ## ########  ######   #######   #######  ##     ##  ######  ########    ##        #######  ##     ## ##     ##  ######

def resourceForms(request):
	context = {}
	context["imageForm"] = ResourceImageForm()
	context["codeForm"] = ResourceCodeForm()
	context["downloadForm"] = ResourceDownloadForm()

	return context




   ###    ########  ########     ########   #######   ######  ########
  ## ##   ##     ## ##     ##    ##     ## ##     ## ##    ##    ##
 ##   ##  ##     ## ##     ##    ##     ## ##     ## ##          ##
##     ## ##     ## ##     ##    ########  ##     ##  ######     ##
######### ##     ## ##     ##    ##        ##     ##       ##    ##
##     ## ##     ## ##     ##    ##        ##     ## ##    ##    ##
##     ## ########  ########     ##         #######   ######     ##

    # author = models.ForeignKey('Developer')
    # title = models.CharField(max_length=200)
    # body = models.TextField()
    # createdDate = models.DateTimeField(default=timezone.now)
    # publishedDate = models.DateTimeField(blank=True, null=True)
    # project = models.ForeignKey('Project')
    # backgroundColour = models.CharField(max_length=6)#colour in hex "FFFFFF" with no #


###VIEW /addPost
@login_required()
def addPost(request, projectID, postID):

	##catch if user logged in but not developer, and send them a special message
	if not getIsDeveloper():
		return render(request, "devBlag/addPost_notDev.html")

	try:
		project = Project.objects.get(id=projectID)
	except ObjectDoesNotExist:
		print "ERROR: Invalid project ID"
		return redirect("/")

	print project


	if postID == "new":
		post = None
	else:
		try:
			post = Post.objects.get(id=postID)
			print "Editing a post"
		except ObjectDoesNotExist:
			print "ERROR: Invalid post ID, defaulting to blank"
			post = None

	developer = Developer.objects.get(user=getCurrentUser())
	print request.user
	if request.method == "POST":
		#form = PostForm(request.POST)
		form = PostForm(request.POST)
		if form.is_valid():
			print "Form is Valid"
			if post is None:
				post = form.save(commit=False)
				post.author_id = developer.id
				post.project_id = project.id
			else:
				#Updating a post. title, body, backgroundColour, postTags
				post.title = form.cleaned_data["title"]
				post.body = form.cleaned_data["body"]
				post.backgroundColour = form.cleaned_data["backgroundColour"]
				post.postTags = forms.cleaned_data["postTags"]

			post.save()
			print "Add post ", post.id
			return redirect("/post/{}/".format(post.id))

	else:
		#form = PostForm()
		if post is not None:
			form = PostForm(initial={'title':post.title, 'body':post.body, "backgroundColour": post.backgroundColour, "postTags": post.postTags})
		else:
			print "NEW FORM"
			form = PostForm(initial={"backgroundColour":project.default_backgroundColour})

	# print "form:"
	# for i in form.__dict__:
	# 	print i
	# print "form.body:"
	# for i in form['body'].__dict__:
	# 	print i
	# print "form.fields:"
	# for i in form['body'].__dict__:
	# 	print i

	c = {
	"form": form,
	"projectID": projectID,
	"postID": postID
	#"myResources": myResources
	}

	#c.update(getResources(developer))
	c.update(resourceForms(request))
	print c
	#return render(request, "devBlag/addPost.html", {"form": form})
	return render(request, "devBlag/addPost.html", c)


##        #######   ######   #### ##    ##
##       ##     ## ##    ##   ##  ###   ##
##       ##     ## ##         ##  ####  ##
##       ##     ## ##   ####  ##  ## ## ##
##       ##     ## ##    ##   ##  ##  ####
##       ##     ## ##    ##   ##  ##   ###
########  #######   ######   #### ##    ##
###VIEW /login/
def login(request):
	return redirect(users.create_login_url(dest_url=request.GET.get('next', '/')))

##        #######   ######    #######  ##     ## ########
##       ##     ## ##    ##  ##     ## ##     ##    ##
##       ##     ## ##        ##     ## ##     ##    ##
##       ##     ## ##   #### ##     ## ##     ##    ##
##       ##     ## ##    ##  ##     ## ##     ##    ##
##       ##     ## ##    ##  ##     ## ##     ##    ##
########  #######   ######    #######   #######     ##
###VIEW /logout/
def logout(request):
    return redirect(users.create_logout_url(dest_url=request.GET.get('next', '/')))


##     ## #### ######## ##      ##    ########   #######   ######  ########
##     ##  ##  ##       ##  ##  ##    ##     ## ##     ## ##    ##    ##
##     ##  ##  ##       ##  ##  ##    ##     ## ##     ## ##          ##
##     ##  ##  ######   ##  ##  ##    ########  ##     ##  ######     ##
 ##   ##   ##  ##       ##  ##  ##    ##        ##     ##       ##    ##
  ## ##    ##  ##       ##  ##  ##    ##        ##     ## ##    ##    ##
   ###    #### ########  ###  ###     ##         #######   ######     ##
def viewPost(request, postID):
	post = Post.objects.get(id=postID)
	post.body = handleBody(post.body)
	print post.postTags
	print post.as_JSON()
	return render(request, "devBlag/post.html", {"post": post})



########  ##     ## ########  ##       ####  ######  ##     ##    ########   #######   ######  ########
##     ## ##     ## ##     ## ##        ##  ##    ## ##     ##    ##     ## ##     ## ##    ##    ##
##     ## ##     ## ##     ## ##        ##  ##       ##     ##    ##     ## ##     ## ##          ##
########  ##     ## ########  ##        ##   ######  #########    ########  ##     ##  ######     ##
##        ##     ## ##     ## ##        ##        ## ##     ##    ##        ##     ##       ##    ##
##        ##     ## ##     ## ##        ##  ##    ## ##     ##    ##        ##     ## ##    ##    ##
##         #######  ########  ######## ####  ######  ##     ##    ##         #######   ######     ##

def publishPost(request):
	success = False
	if request.method == "GET":
		postID = request.GET.get("postID", None)
		if postID is not None:
			post = Post.objects.get(id=postID)
			post.publish()
			success = True
	
	
	return JsonResponse({"SUCCESS":success})

########  ########   #######  ######## #### ##       ########
##     ## ##     ## ##     ## ##        ##  ##       ##
##     ## ##     ## ##     ## ##        ##  ##       ##
########  ########  ##     ## ######    ##  ##       ######
##        ##   ##   ##     ## ##        ##  ##       ##
##        ##    ##  ##     ## ##        ##  ##       ##
##        ##     ##  #######  ##       #### ######## ########
###VIEW /profile/
@login_required()
def profile(request):
	gaeUser = users.get_current_user()
	if gaeUser is None: # if there isnt a current user somehow, redirect to index
		redirect("/")

	c = {}
	
	#if developer, get unpublished posts to send to template, None if not
	unpublishedPosts = None

	user = getCurrentUser()

	isDeveloper = getIsDeveloper()

	if isDeveloper:
		developer = Developer.objects.get(user=user)
		unpublishedPosts = handlePosts(Post.objects.filter(author=developer).filter(publishedDate=None))
		c.update(getResources(developer, False))
	else:
		developer = None

	
		

	c.update({
	"user":user,
	"isDeveloper":isDeveloper,
	"developer": developer,
	"unpublishedPosts": unpublishedPosts
	})
	

	print "developer", developer
	return render(request, "devBlag/profile.html", c)

##     ## ########  ########     ###    ######## ########    ########  ########   #######  ######## #### ##       ########
##     ## ##     ## ##     ##   ## ##      ##    ##          ##     ## ##     ## ##     ## ##        ##  ##       ##
##     ## ##     ## ##     ##  ##   ##     ##    ##          ##     ## ##     ## ##     ## ##        ##  ##       ##
##     ## ########  ##     ## ##     ##    ##    ######      ########  ########  ##     ## ######    ##  ##       ######
##     ## ##        ##     ## #########    ##    ##          ##        ##   ##   ##     ## ##        ##  ##       ##
##     ## ##        ##     ## ##     ##    ##    ##          ##        ##    ##  ##     ## ##        ##  ##       ##
 #######  ##        ########  ##     ##    ##    ########    ##        ##     ##  #######  ##       #### ######## ########

###VIEW /updateProfile/
VALID_UPDATEPROFILE_METHODS = ["updateFirstName", "updateLastName", "updateDisplayName"]
@login_required()
def updateProfile(request):
	returnContext = {}
	returnContext["nameUpdated"] = False
	if request.method == "GET":
		#context = RequestContext(request)
		newVal = request.GET.get("newVal", None)
		method = request.GET.get("method", None)

		if newVal is not None and method is not None:

			print "Updating profile: {} = {}!".format(method, newVal)
			if method in VALID_UPDATEPROFILE_METHODS:
				user = getCurrentUser()
				if method == "updateFirstName":
					user.first_name = newVal
					user.save()
				elif method == "updateLastName":
					user.last_name = newVal
					user.save()
				else: #method == "updateDisplayName"
					developer = getDeveloper()
					developer.displayName = newVal
					developer.save()

				returnContext["nameUpdated"] = True
				return JsonResponse(returnContext)

	##,function(){function t(t){var i,s,n=t.ownerDocument.defaultView?t.ownerDoc


	return JsonResponse(returnContext)


def getResources(developer, public):
	##returns: dict of the three types of resource,
	#each in turn split in to "mine" and "public"
	#"mine" is belooing to the logged in developer
	#'public' is not in mine, but with property "public" set to True


	resources_dict = {
	"Resource_image":
		{ 
			"mine"		:	[],
			"public" 	:	[]
		},
	"Resource_code":
		{ 
			"mine"		:	[],
			"public" 	:	[]
		},
	"Resource_download":
		{ 
			"mine"		:	[],
			"public" 	:	[]
		}
	}

	#public includes owner's as cannot .excuse(owner=developer) here.
	#"Cross-join WHERE constraints aren't supported: [(u'devBlag_resource', 'public'), (u'devBlag_resource', u'owner_id')]"
	resources_dict["Resource_image"]["mine"] = Resource_image.objects.filter(owner=developer)
	if public:
		resources_dict["Resource_image"]["public"] = Resource_image.objects.filter(public=True)
	resources_dict["Resource_code"]["mine"] = Resource_code.objects.filter(owner=developer)
	if public:
		resources_dict["Resource_code"]["public"] = Resource_code.objects.filter(public=True)
	resources_dict["Resource_download"]["mine"] = Resource_download.objects.filter(owner=developer)
	if public:
		resources_dict["Resource_download"]["public"] = Resource_download.objects.filter(public=True)
	return resources_dict

 ######   ######## ########    ########  ########  ######   #######  ##     ## ########   ######  ########  ######
##    ##  ##          ##       ##     ## ##       ##    ## ##     ## ##     ## ##     ## ##    ## ##       ##    ##
##        ##          ##       ##     ## ##       ##       ##     ## ##     ## ##     ## ##       ##       ##
##   #### ######      ##       ########  ######    ######  ##     ## ##     ## ########  ##       ######    ######
##    ##  ##          ##       ##   ##   ##             ## ##     ## ##     ## ##   ##   ##       ##             ##
##    ##  ##          ##       ##    ##  ##       ##    ## ##     ## ##     ## ##    ##  ##    ## ##       ##    ##
 ######   ########    ##       ##     ## ########  ######   #######   #######  ##     ##  ######  ########  ######

###VIEW /getResources/
def getResources2(request):
##Gets JSON data for specific resources
	resourceType = request.GET.get("resourceType")
	public = request.GET.get("public", "false")

	RES_SERVING_FIELDS_IMAGE = ["imageFile.url"]
	RES_SERVING_FIELDS_CODE = ["code"]
	RES_SERVING_FIELDS_DOWNLOAD = []
	RES_SERVING_FIELDS_ALL = ["caption", "id"]
	
	if resourceType is None or resourceType not in ["image", "code", "download"]:
		print "INVALID"
		return JsonResponse({'SUCCESS': False})

	response = {"SUCCESS":True}

	## for each type, get the resources, and set the specific attributes
	if resourceType == "image":
		if public == "true":
			resources = Resource_image.objects.filter(public=True)
		else:
			resources = Resource_image.objects.filter(owner=getDeveloper())
		#resources = Resource_image.objects.all()
		#resources = Resource_image.objects.filter(owner=getDeveloper())

		response["RESOURCE_TYPE"] = "image"

		resServingFields = RES_SERVING_FIELDS_IMAGE
 
	elif resourceType == "code":
		if public == "true":
			resources = Resource_code.objects.filter(public=True)
		else:
			resources = Resource_code.objects.filter(owner=getDeveloper())
		#resources = Resource_code.objects.all()
		resources = Resource_code.objects.filter(owner=getDeveloper())

		response["RESOURCE_TYPE"] = "code"

		resServingFields = RES_SERVING_FIELDS_CODE

	else:# resourceType == "download":
		if public == "true":
			resources = Resource_download.objects.filter(public=True)
		else:
			resources = Resource_download.objects.filter(owner=getDeveloper())
		resources = Resource_download.objects.all()

		response["RESOURCE_TYPE"] = "download"

		resServingFields = RES_SERVING_FIELDS_DOWNLOAD

	## now we have resources, now we collect attributes
	servingResources = []
	for res in resources:
		resFields = {}
		## get the default ones
		for field in RES_SERVING_FIELDS_ALL:
			resFields[field.replace(".", "_")] = helpers.getattrd(res, field, "")

		## get the specific ones
		for field in resServingFields:
			resFields[field.replace(".", "_")] = helpers.getattrd(res, field, "")

		## get username, with 2 fallbacks for blank names
		if res.owner.displayName != "":
			resFields["owner"] = res.owner.displayName
			print "name", res.owner.displayName
		elif res.owner.user.first_name != "" and res.owner.user.last_name != "":
			resFields["owner"] = res.owner.user.first_name + " " + res.owner.user.last_name
			print "name", res.owner.user.first_name + " " + res.owner.user.last_name
		else:
			resFields["owner"] = res.owner.user.username
			print "name", res.owner.user.username

		servingResources.append(resFields)

	response["RESOURCES"] = servingResources

	return JsonResponse(response)


def dialogTest(request):
	return render(request, "test/dialogTest.html")