from typing import Union, Tuple

from jose import jwt
from starlette.authentication import AuthenticationBackend, AuthenticationError, AuthCredentials, BaseUser, SimpleUser


class JWTUser(SimpleUser):

    def __init__(self, username: str, token: str, payload: dict) -> None:
        self.username = username
        self.token = token
        self.payload = payload


class JWTAuthenticationBackend(AuthenticationBackend):
    def __init__(self,
                 secret_key: str,
                 algorithm: str = 'HS256',
                 prefix: str = 'JWT',
                 username_field: str = 'sub',
                 ) -> None:
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.prefix = prefix
        self.username_field = username_field

    @classmethod
    def get_token_from_header(cls, authorization: str, prefix: str) -> str:
        """Parses the Authorization header and returns only the token"""
        try:
            scheme, token = authorization.split()
        except ValueError:
            raise AuthenticationError('Could not separate Authorization scheme and token')
        if scheme.lower() != prefix.lower():
            raise AuthenticationError(f'Authorization scheme {scheme} is not supported')
        return token

    async def authenticate(self, request) -> Union[None, Tuple[AuthCredentials, BaseUser]]:
        if "Authorization" not in request.headers:
            return None

        auth = request.headers["Authorization"]
        token = self.get_token_from_header(authorization=auth, prefix=self.prefix)
        try:
            payload = jwt.decode(token, key=self.secret_key, algorithms=self.algorithm)
        except jwt.JWTError as e:
            raise AuthenticationError(str(e))

        return AuthCredentials(["authenticated"]), JWTUser(username=payload[self.username_field], token=token,
                                                           payload=payload)
