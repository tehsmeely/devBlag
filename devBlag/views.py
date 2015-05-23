from django.shortcuts import render, render_to_response, redirect
from django.utils import timezone
from django.template import RequestContext
from djangae.contrib.gauth.datastore.models import GaeDatastoreUser, Group
from django.contrib.auth.decorators import login_required
from google.appengine.api import users
from .models import Post, Resource, Resource_map, Project, Developer
from scaffold.settings import BASE_DIR, STATIC_URL, AUTH_USER_MODEL
from .settings import DEFAULT_POST_ORDER_BY, DEFAULT_POST_ORDER
from .forms import PostForm
import os, re

STATIC_PATH = os.path.join(BASE_DIR, "devBlag", "static")
RES_REGEX = re.compile("(<<id:\w>>)+")


print "devBlag/views.py my __name__:", __name__

# View functions are labels as below:

###VIEW <url>

#all other functions are helpers and usually roughly just after the views that use them.


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

	return render(request, 'devBlag/projectPosts.html', {'posts':posts, 'resources':resources})


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


   ###    ########  ########  ########   #######   ######  ########
  ## ##   ##     ## ##     ## ##     ## ##     ## ##    ##    ##
 ##   ##  ##     ## ##     ## ##     ## ##     ## ##          ##
##     ## ##     ## ##     ## ########  ##     ##  ######     ##
######### ##     ## ##     ## ##        ##     ##       ##    ##
##     ## ##     ## ##     ## ##        ##     ## ##    ##    ##
##     ## ########  ########  ##         #######   ######     ##

###VIEW /addPost
@login_required()
def addPost(request):
	print request.user
	if request.method == "POST":
		#form = PostForm(request.POST)
		form = PostForm(request.POST)
		if form.is_valid():
			print "boop"
			#return HttpResponseRedirect("/addPost")

	else:
		#form = PostForm()
		form = PostForm()

	print "form.body:"
	for i in form['body'].__dict__:
		print i

	allResources = Resource.objects.all().order_by("resID")
	#myResources = Resources.objects.get(user)

	c = {
	"form": form,
	#"myResources": myResources,
	"allResources": allResources
	}
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
	user = GaeDatastoreUser.objects.get(username = str(gaeUser.user_id()))
	devGroup = Group.objects.get(name="developers")

	print devGroup.id

	for d in user.__dict__:
		print d
	print "user: ", user.first_name, user.last_name, "grps: ", user.groups_ids

	if devGroup.id in user.groups_ids:
		isDeveloper = True
	else:
		isDeveloper = False
	return render(request, "devBlag/profile.html", {"user":user, "isDeveloper":isDeveloper})