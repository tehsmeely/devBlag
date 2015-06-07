from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, render_to_response, redirect
from django.utils import timezone
from django.template import RequestContext
from djangae.contrib.gauth.datastore.models import GaeDatastoreUser, Group
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from google.appengine.api import users
from google.appengine.api.images import get_serving_url
from .models import Post, Resource_image, Resource_code, Resource_download, Resource_map, Project, Developer
from scaffold.settings import BASE_DIR, STATIC_URL, AUTH_USER_MODEL
from .settings import DEFAULT_POST_ORDER_BY, DEFAULT_POST_ORDER
from .forms import PostForm, ResourceImageForm, ResourceCodeForm, ResourceDownloadForm
import os, re, json, urlparse


STATIC_PATH = os.path.join(BASE_DIR, "devBlag", "static")
RES_REGEX = re.compile("(<<id:\w>>)+")



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
	##return True is logged in user is devleoper, false if not, or no logged in user
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

	rc_dl = Resource_download.objects.all()[0]
	print rc_dl
	for item in rc_dl.__dict__:
		print item
	print rc_dl.resFile

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

	posts = Post.objects.filter(project=project).order_by(order_byStr)



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
	latestPosts = Post.objects.all().order_by("-publishedDate")[:10]
	for post in latestPosts:
		post.body = handleBody(post.body)
	return render(request, "devBlag/developerProfile.html", {'developer':developer, 'latestPosts':latestPosts})

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
def addResource(request):
	context = {}
	if request.method == "POST":
		print "POST"
		print request.POST
		print request
		##initialise form vars to None, to fill with unbound if
		##page needs to be re-rendered
		imageForm = None
		codeForm = None
		downloadForm = None

		#Bind the correct form based on the type
		resType = request.POST.get("resType")
		if resType == "image":
			print "image"
			imageForm = ResourceImageForm(request.POST, request.FILES)
			if imageForm.is_valid():
				imageRes = imageForm.save()
				print imageRes
				return redirect("/") ## to be to ResourceList page
		if resType == "code":
			print "code"
			codeForm = ResourceCodeForm(request.POST)
			if codeForm.is_valid():
				return redirect("/") ## to be to ResourceList page
		if resType == "download":
			print "download"
			downloadForm = ResourceDownloadForm(request.POST, request.FILES)
			if downloadForm.is_valid():
				return redirect("/") ## to be to ResourceList page

		#now find the unused forms to fill unbound to send back to page
		if imageForm is None:
			imageForm = ResourceImageForm()
		if codeForm is None:
			codeForm = ResourceCodeForm()
		if downloadForm is None:
			downloadForm = ResourceDownloadForm()
		context["imageForm"] = imageForm
		context["codeForm"] = codeForm
		context["downloadForm"] = downloadForm
		
	else:
		##Unbound forms
		context["imageForm"] = ResourceImageForm()
		context["codeForm"] = ResourceCodeForm()
		context["downloadForm"] = ResourceDownloadForm()

	return render(request, "devBlag/addResource.html", context)

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
			post = form.save(commit=False)
			#developer = Developer.objects.get(user=getCurrentUser())
			post.author_id = developer.id
			post.project_id = project.id
			post.save()
			print "finished"
			#return HttpResponseRedirect("/addPost")

	else:
		#form = PostForm()
		if post is not None:
			form = PostForm(initial={'title':post.title, 'body':post.body, "backgroundColour": post.backgroundColour})
		else:
			form = PostForm()

	print "form.body:"
	for i in form['body'].__dict__:
		print i

	c = {
	"form": form,
	#"myResources": myResources
	}

	c.update(getResources(developer))
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
	
	#userss = GaeDatastoreUser.objects.all()#str(gaeUser.user_id()))
	#user = GaeDatastoreUser.objects.get(username = str(gaeUser.user_id()))
	user = getCurrentUser()
	devGroup = Group.objects.get(name="developers")

	print devGroup.id

	for d in user.__dict__:
		print d
	print "user: ", user.first_name, user.last_name, "grps: ", user.groups_ids

	if devGroup.id in user.groups_ids:
		isDeveloper = True
		developer = Developer.objects.get(user=user)
	else:
		isDeveloper = False
		developer = None

	print "developer", developer
	return render(request, "devBlag/profile.html", {"user":user, "isDeveloper":isDeveloper, "developer": developer}, )


###VIEW /updateProfile/
@login_required()
def updateProfile(request):
	returnContext = {}
	returnContext["nameUpdated"] = False
	if request.method == "GET":
		#context = RequestContext(request)
		newName = request.GET.get("newName", None)

		if newName is not None:
			print "NEW NAME!"
			returnContext["nameUpdated"] = True
			#return HttpResponse(json.dumps(returnContext))
			return JsonResponse(returnContext)

	##,function(){function t(t){var i,s,n=t.ownerDocument.defaultView?t.ownerDoc


	return JsonResponse(returnContext)


def getResources(developer):
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
	resources_dict["Resource_image"]["mine"] = Resource_image.objects.filter(public=True)
	resources_dict["Resource_code"]["mine"] = Resource_code.objects.filter(owner=developer)
	resources_dict["Resource_code"]["mine"] = Resource_code.objects.filter(public=True)
	resources_dict["Resource_download"]["mine"] = Resource_download.objects.filter(owner=developer)
	resources_dict["Resource_download"]["mine"] = Resource_download.objects.filter(public=True)
	return resources_dict
