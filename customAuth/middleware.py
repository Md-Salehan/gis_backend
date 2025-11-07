from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
from .models import SutUserMst
import jwt
from django.conf import settings
from datetime import datetime

class JWTAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.custom_user = None # Initialize custom_user to None
        # Only skip login endpoint
        if request.path == '/api/login/':
            return None

        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        if not auth_header.startswith('Bearer '):
            return None

        token = auth_header.split(' ')[1]

        try:
            # Manually decode JWT token
            decoded_token = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=["HS256"],
                options={"verify_exp": True}
            )

            # Get user_id from token payload
            user_id = decoded_token.get('user_id')

            if user_id:
                # Get user from your custom user model
                try:
                    user = SutUserMst.objects.get(user_id=user_id)
                    request.custom_user = user
                except SutUserMst.DoesNotExist:
                    pass  # User not found
                
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, jwt.DecodeError):
            pass  # Token validation failed

    def process_response(self, request, response):
        return response