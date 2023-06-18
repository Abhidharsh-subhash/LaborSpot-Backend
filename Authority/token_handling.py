from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken


class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        try:
            return super().authenticate(request)
        except TokenError:
            token = self.get_raw_token(request)
            #method to obtain a new access token.
            validated_token = self.get_validated_token(token)
            user = self.get_user(validated_token)

            # Obtain a new access token using the refresh token
            new_access_token = self.get_refreshed_token(token)

            return user, new_access_token
    def get_refreshed_token(self, refresh_token):
        # Create a RefreshToken instance from the refresh token string
        refresh_token = RefreshToken(refresh_token)

        # Generate a new access token using the refresh token
        new_access_token = refresh_token.access_token

        # Return the new access token
        return new_access_token