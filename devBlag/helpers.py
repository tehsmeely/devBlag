#from .models import 
from django.shortcuts import redirect
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from google.appengine.api import users
from djangae.contrib.gauth.datastore.models import GaeDatastoreUser
from .models import Developer

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

def getIsDeveloper(currentUser=None):
    ##return True is logged in user is developer, false if not, or no logged in user
    #currentUser = users.get_current_user()

    #First check, if none is passed
    if currentUser is None:
        currentUser = getCurrentUser()

    #
    if currentUser is None:
        return False
    else:
        return Developer.objects.filter(user=currentUser).exists()


class NoDefaultProvided(object):
    pass

def getattrd(obj, name, default=NoDefaultProvided):
    """
    Same as getattr(), but allows dot notation lookup
    Discussed in:
    http://stackoverflow.com/questions/11975781
    """

    try:
        return reduce(getattr, name.split("."), obj)
    except AttributeError, e:
        if default != NoDefaultProvided:
            return default
        raise



##developer_required wrapper
# Redirects if not a registered developer in db
# I wanted to use the django user_passes_test decorator
# But this is too locked down for a two-part verification and redirection
# that i want there, as well as not a login redirect
## most of the code is ripped from 

# def developer_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
#     """
#     Decorator for views that checks that the user is logged in as a developer, redirecting
#     to the log-in page if necessary.
#     """
#     print "developer required!", REDIRECT_FIELD_NAME
#     def devCheck(user):
#         if user.is_anonymous():
#             return False
#         else:
#             return getIsDeveloper(user)

            


#     def wrapper(request, *args, **kw):




#             if test_func(request.user):
#                 return view_func(request, *args, **kwargs)
#             path = request.build_absolute_uri()
#             resolved_login_url = resolve_url(login_url or settings.LOGIN_URL)
#             # If the login url is the same scheme and net location then just
#             # use the path as the "next" url.
#             login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
#             current_scheme, current_netloc = urlparse(path)[:2]
#             if ((not login_scheme or login_scheme == current_scheme) and
#                     (not login_netloc or login_netloc == current_netloc)):
#                 path = request.get_full_path()
#             from django.contrib.auth.views import redirect_to_login
#             return redirect_to_login(
#                 path, resolved_login_url, redirect_field_name)