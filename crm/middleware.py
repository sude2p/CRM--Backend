from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
import jwt
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.models import AnonymousUser
from django.utils.deprecation import MiddlewareMixin
import jwt
from django.conf import settings


class JWTAuthCookieMiddleware(MiddlewareMixin):
    def process_request(self, request):
        """
        This middleware sets the request.user based on the access token from the
        Authorization header or the access_token cookie.

        If the token is valid and contains a user_id, it fetches the corresponding
        CustomUser object and assigns it to request.user.

        If the token is invalid or no token is present, it sets request.user to None.
        """

        access_token = request.COOKIES.get("access_token") or request.headers.get(
            "Authorization", ""
        ).replace("Bearer ", "")

        if access_token:
            print(f"Access Token Cookie: {access_token}")
            request.META["HTTP_AUTHORIZATION"] = f"Bearer {access_token}"
            print(f"Authorization Header Set: {request.META.get('HTTP_AUTHORIZATION')}")

            signing_key = settings.SIMPLE_JWT["SIGNING_KEY"]

            try:
                # Decode the JWT token
                decoded_token = jwt.decode(
                    access_token, signing_key, algorithms=["HS256"]
                )
                print(f"Decoded token: {decoded_token}")

                user_id = decoded_token.get("user_id")
                print(f"User ID: {user_id}")

                if user_id:
                    # Get the custom user model
                    User = get_user_model()

                    try:
                        # Fetch the CustomUser object based on the ref_user_id
                        user = User.objects.get(user_ref_id=user_id)
                        request.user = user  # Assign the user object to request.user
                        print(f"User authenticated: {user}")
                        # Explicitly load permissions
                        if hasattr(user, "get_all_permissions"):
                            user_permissions = user.get_all_permissions()
                            print(f"User permissions: {user_permissions}")
                        else:
                            print("User permissions not found.")
                    except User.DoesNotExist:
                        print(f"User with ref_user_id {user_id} does not exist")
                        request.user = (
                            None  # Set request.user to None if user is not found
                        )
                else:
                    request.user = None  # Set request.user to None if user_id is not found in the token

            except jwt.ExpiredSignatureError:
                print("Token has expired")
                request.user = None
            except jwt.InvalidTokenError:
                print("Invalid token")
                request.user = None

        else:
            request.user = None


# User = get_user_model()
# class JWTAuthCookieMiddleware(MiddlewareMixin):
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         access_token = request.COOKIES.get('access_token')
#         print(f"Access Token Cookie: {access_token}")

#         if access_token:
#             request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
#             print(f"Authorization Header Set: {request.META.get('HTTP_AUTHORIZATION')}")

#             try:
#                 decoded_token = self._decode_jwt(access_token)
#                 print(f'Decoded Token: {decoded_token}')

#                 if not decoded_token:
#                     print("Failed to decode token")
#                     request.user = None
#                     return self.get_response(request)

#                 user_id = decoded_token.get('user_id')
#                 print(f'User ID: {user_id}')

#                 if user_id:
#                     user = self._fetch_user_from_auth_service(user_id)
#                     if user:
#                         print(f"Authenticated user: {user}")
#                         request.user = user
#                         print(f"Request user set: {request.user}")
#                     else:
#                         print(f"User with ID {user_id} not found in auth microservice")
#                         request.user = None
#                 else:
#                     print("User ID not found in token")
#                     request.user = None

#             except Exception as e:
#                 print(f"Error in authentication: {e}")
#                 request.user = None
#         else:
#             print("Access Token Cookie Missing")
#             request.user = None

#         response = self.get_response(request)
#         print(f"Response status code: {response.status_code}")
#         return response

#     def _decode_jwt(self, token):
#         try:
#             return jwt.decode(token, settings.SIMPLE_JWT['SIGNING_KEY'], algorithms=["HS256"])
#         except jwt.ExpiredSignatureError:
#             print("Token has expired")
#         except jwt.InvalidTokenError:
#             print("Invalid Token")
#         except Exception as e:
#             print(f"Error decoding token: {e}")
#         return None

#     def _fetch_user_from_auth_service(self, user_id):
#         try:
#             url = f'{settings.AUTH_SERVICE_URL}/api/v1/auth/user-get/{user_id}/'
#             print(f"Fetching user from: {url}")
#             # response = requests.get(f'{settings.AUTH_SERVICE_URL}/api/v1/auth/user-get/{user_id}/')
#             response = requests.get(url)
#             print(f'response from 8000: {response}')
#             if response.status_code == 200:
#                 user_data = response.json()
#                 User = get_user_model()
#                 user_id = user_data.get('id')
#                 # Assuming user_data has fields like 'id' that match your User model
#                 user = User.objects.filter(id=user_id).first()
#                 if user:
#                     print(f"User found: {user}")  # Debugging line
#                 else:
#                     print(f"User with ID {user_id} not found in local database")
#                 return user

#             else:
#                 print(f"Error fetching user from auth microservice: {response.status_code}")
#         except requests.RequestException as e:
#             print(f"Request to auth microservice failed: {e}")
#         return None
