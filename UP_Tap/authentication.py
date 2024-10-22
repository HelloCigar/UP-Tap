from ninja.security import HttpBearer
from rest_framework.authtoken.models import Token

class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        try:
            # Look up the token in the Token model
            auth_token = Token.objects.get(key=token)
            # Return the username associated with the token
            request.user = auth_token.user
            return auth_token.user.email
        except Token.DoesNotExist:
            raise InvalidToken

class InvalidToken(Exception):
    pass