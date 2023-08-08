#!/usr/bin/env python3
""" Basic Auth module
"""
from api.v1.auth.auth import Auth
import base64
from typing import Tuple, TypeVar
from models.user import User


class BasicAuth(Auth):
    """ Basic auth class
    """

    def extract_base64_authorization_header(
            self, authorization_header: str) -> str:
        """Extracts and returns base64 authorization header
        """
        if authorization_header is None:
            return None
        if type(authorization_header) != str:
            return None
        if not authorization_header.startswith('Basic '):
            return None
        else:
            return authorization_header.split(' ')[1]

    def decode_base64_authorization_header(
            self, base64_authorization_header: str) -> str:
        """ Decodes and returns the decoded value of
        Base64 string
        """
        if base64_authorization_header is None:
            return None
        if type(base64_authorization_header) != str:
            return None
        try:
            # header_bytes = base64_authorization_header.encode('utf-8')
            utf8_bytes = base64.b64decode(base64_authorization_header)
            utf8_str = utf8_bytes.decode('utf-8')
            return utf8_str
        except Exception as err:
            return None

    def extract_user_credentials(
            self, decoded_base64_authorization_header: str) -> Tuple:
        """ Extracts user's credentials and returns user
        email and password from base64 decoded value
        """
        if decoded_base64_authorization_header is None:
            return None, None
        if type(decoded_base64_authorization_header) != str:
            return None, None
        if ':' not in decoded_base64_authorization_header:
            return None, None
        idx = decoded_base64_authorization_header.find(':')
        email = decoded_base64_authorization_header[0:idx]
        password = decoded_base64_authorization_header[idx + 1:]
        # email, password = decoded_base64_authorization_header.split(':')
        return email, password

    def user_object_from_credentials(
            self, user_email: str, user_pwd: str) -> TypeVar('User'):
        """ Returns User instance based on his password and email
        """
        if user_email is None or type(user_email) != str:
            return None
        if user_pwd is None or type(user_pwd) != str:
            return None

        users = User.search({"email": user_email})
        if len(users) == 0:
            return None
        if users[0].is_valid_password(user_pwd):
            return users[0]
        else:
            return None

    def current_user(self, request=None) -> TypeVar('User'):
        """ Retrieves user instance for a request
        """
        auth_header = self.authorization_header(request)
        if auth_header:
            auth_header64 = self.extract_base64_authorization_header(
                auth_header)
            if auth_header64:
                decoded_auth = self.decode_base64_authorization_header(
                    auth_header64)
                if decoded_auth:
                    credentials = self.extract_user_credentials(decoded_auth)
                    if credentials:
                        user = self.user_object_from_credentials(*credentials)
                        return user
