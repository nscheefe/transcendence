from django.utils.deprecation import MiddlewareMixin


class AuthMiddleware(MiddlewareMixin):
    """
        @Todo this is only a middle ware for testing so later one we need the correct auth implementation
    """

    def process_request(self, request):
        request.user_id = 1