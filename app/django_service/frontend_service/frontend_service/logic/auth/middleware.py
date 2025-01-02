import jwt
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect

class JWTAuthenticationMiddleware:
    """
    Middleware to check for a valid JWT token in the request cookies.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get the token from the cookies (assuming the cookie name is 'jwt_token')
        token = request.COOKIES.get('jwt_token')

        # If no token is provided, redirect to the signin page
        if not token:
            return redirect('signin')

        try:
            # Decode and verify the JWT token using a secret or public key
            decoded_data = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])

            # Add user info to the request object (you can use this in views)
            request.user = decoded_data['user_id']  # Assuming 'user' contains user info
        except jwt.ExpiredSignatureError:
            return JsonResponse({"error": "Token has expired"}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({"error": "Invalid token"}, status=401)

        # Proceed with the request
        response = self.get_response(request)
        return response

