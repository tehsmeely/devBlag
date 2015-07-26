from django.contrib.auth import REDIRECT_FIELD_NAME
from django.utils.decorators import available_attrs
from django.shortcuts import resolve_url, redirect
from django.http import QueryDict
from django.utils.six.moves.urllib.parse import urlparse, urlunparse
from functools import wraps
from .helpers import getIsDeveloper

def user_passes_tests(test_funcs, redirect_urls, redirect_field_name=REDIRECT_FIELD_NAME):
	"""
	Decorator for views that checks that the user passes the given test,
	redirecting to the log-in page if necessary. The test should be a callable
	that takes the user object and returns True if the user passes.
	"""
	# Loops through all passed test funcs. If one fails, it uses the affiliated
	# redirect url. If all pass, call view_func
	def decorator(view_func):
		@wraps(view_func, assigned=available_attrs(view_func))
		def _wrapped_view(request, *args, **kwargs):

			allPass = 1
			for i in xrange(len(test_funcs)):
				test_func = test_funcs[i]
				redirect_url = redirect_urls[i]
				print "test_func: ", test_func.__name__
				if not test_func(request.user):
					allPass = 0
					print "check fail"
					break
				else:
					print "check pass"

			if allPass:
				return view_func(request, *args, **kwargs)

			path = request.build_absolute_uri()
			resolved_redirect_url = resolve_url(redirect_url)

			# If the login url is the same scheme and net location then just
			# use the path as the "next" url.
			redirect_scheme, redirect_netloc = urlparse(resolved_redirect_url)[:2]
			current_scheme, current_netloc = urlparse(path)[:2]
			if ((not redirect_scheme or redirect_scheme == current_scheme) and
					(not redirect_netloc or redirect_netloc == current_netloc)):
				path = request.get_full_path()

			login_url_parts = list(urlparse(resolved_redirect_url))
			if redirect_field_name:
				querystring = QueryDict(login_url_parts[4], mutable=True)
				querystring[redirect_field_name] = path
				login_url_parts[4] = querystring.urlencode(safe='/')

			#print "redir: ", urlunparse(login_url_parts)
			return redirect(urlunparse(login_url_parts))



		return _wrapped_view
	return decorator


def developer_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, inp_redirect_urls=[]):
	redirect_urls = ["/login/", "/profile/"]

	#handle the input urls if present. there is probably a better way to do this
	# esp for longer lists
	if len(inp_redirect_urls) >= 2:
		redirect_urls = inp_redirect_urls[1:]
	elif len(inp_redirect_urls) == 1:
		redirect_urls[1] = inp_redirect_urls[1]

	def loginCheck(u):
		return u.is_authenticated()

	def devCheck(u):
		if u.is_anonymous():
			return False
		else:
			return getIsDeveloper(u)

	test_funcs = [loginCheck, devCheck]

	actual_decorator = user_passes_tests(
		test_funcs,
		redirect_urls,
		redirect_field_name=redirect_field_name
	)
	if function:
		return actual_decorator(function)
	return actual_decorator
