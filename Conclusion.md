#Conclusion

##Starting...
At the start of this project:
+ confident in Python, JS and JQuery
+ Familiar with [Flask](http://flask.pocoo.org/) as a python web framework

So Django and GAE (and non-relationals as a whole) as new to me - the learning curve has been steep, so pre-planning has been speculative at best

##Starting Again ...
With the benefit of hindsight and having learnt the basics of Django and GAE, there are some things I think I would have done differently if starting again:

+ Class-based views - views.py is >1000 lines, I'm sure there is plenty that could be done with mixins etc, and so would be better off with Class based view functions
+ More thorough plan of pages and routing around them for styling and functional reasons - buttons, form structure, etc, could be pre-organised and hence more continuity
+ Use more Django functionality if present to help with such things
+ Design for mobile, aim for responsive design - which i prefer and seems most sensible for small projects
+ Use frameworks available to increase productivity
+ Make the most of html5 and css3 - modernizr (as above) can help for browser coverage


Now,
##Reviewing DevBlag...

DevBlag was supposed to focus on the resource system for images, code snippets and downloads. I like how this ended up with the resources independent of the posts and, if you like, able to be used in posts by others. However in the current state your personal resources may become rather unmanagable, and there's no way of knowing if a resource is in a post as it is called from an id in the content (I removed the DB mapping that did this many to many mapping for simplicity).
To expand this idea, a more in depth content/resource manager would be needed, as well as proper mapping for resources to posts, as well as to projects, such as direct source code with version control.

Also, Developer extra user is a bit clunky from the normal GaeDatastoreUser as base user. A better approach may have been to subclass GaeDatastoreUser and create a new baseline user, which can be updated to developer without a separate model and entity - this would make handling rights and login states for access control a lot easier!

TBC ...