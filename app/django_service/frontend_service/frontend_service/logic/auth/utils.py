from django.shortcuts import redirect

def jwt_required(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        if not isJwtSet(request):
            return redirect('signin')
        return view_func(request, *args, **kwargs)
    return _wrapped_view_func

def isJwtSet(request):
	if 'jwt_token' in request.COOKIES:
		return True
	return False
