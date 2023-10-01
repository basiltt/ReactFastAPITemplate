from dataclasses import dataclass

import requests
from fastapi import HTTPException
from starlette.requests import Request
from starlette.responses import RedirectResponse

TOKEN_URL = r"https://login-itg.ext.hpe.com/as/token.oauth2"
AUTHORIZE_URL = r"https://login-itg.ext.hpe.com/as/authorization.oauth2"
USER_INFO_URL = r"https://login-itg.ext.hpe.com/idp/userinfo.openid"
STATE = "Application State"
SCOPE = "openid email profile"

PROXIES = {
    "http": "http://proxy.houston.hpecorp.net:8080",
    "https": "http://proxy.houston.hpecorp.net:8080",
}


class Validations:
    def __post_init__(self):
        """
        Run validation methods if declared.
        The validation method can be a simple check
        that raises ValueError or a transformation to
        the field value.
        The validation is performed by calling a function named:
            `validate_<field_name>(self, value, field) -> field.type`
        Finally, calls (if defined) `validate(self)` for validations that depend on other fields
        """
        for name, field in self.__dataclass_fields__.items():
            method = getattr(self, f"validate_{name}", None)
            if method:
                new_value = method(getattr(self, name), field=field)
                setattr(self, name, new_value)
        validate = getattr(self, "validate", None)
        if validate and callable(validate):
            validate()


@dataclass
class OauthConfig(Validations):
    """
    Dataclass for the validation
    (pydantic not used to reuse the module in non FastAPI projects with minimal changes)
    """

    client_id: str
    client_secret: str
    redirect_uri: str

    @staticmethod
    def validate_client_id(value, **_) -> str:
        if not isinstance(value, str):
            raise ValueError(
                "Invalid request, parameter 'client_id' should be of type str"
            )
        if len(value) < 2:
            raise ValueError(
                "Invalid request, 'client_id' length should be greater than 2"
            )
        return value

    @staticmethod
    def validate_client_secret(value, **_) -> str:
        if not isinstance(value, str):
            raise ValueError(
                "Invalid request, parameter 'client_secret' should be of type str"
            )
        if len(value) < 5:
            raise ValueError(
                "Invalid request, 'client_secret' length should be greater than 5"
            )
        return value

    @staticmethod
    def validate_redirect_uri(value, **_) -> str:
        if not isinstance(value, str):
            raise ValueError(
                "Invalid request, parameter 'redirect_uri' should be of type str"
            )
        if len(value) < 5:
            raise ValueError(
                "Invalid request, 'redirect_uri' length should be greater than 5"
            )
        if not value.startswith("https://"):
            raise ValueError(
                "Invalid request, 'redirect_uri' should starts with https://"
            )
        return value


class HpaOauth:
    """
    Class to perform Oauth based authentication in HPE org
    """

    def __init__(self, config: dict):
        self.config = OauthConfig(**config)
        self.token_url = TOKEN_URL
        self.authorize_url = AUTHORIZE_URL
        self.user_info_url = USER_INFO_URL
        self.state = STATE
        self.scope = SCOPE

    def redirect_to_auth_provider(self) -> RedirectResponse:
        """
        Method to redirect to the authentication provider
        :return: None
        """
        query_params = {
            "client_id": self.config.client_id,
            "redirect_uri": self.config.redirect_uri,
            "scope": self.scope,
            "state": self.state,
            "response_type": "code",
            "response_mode": "query",
        }
        url = "{base_url}?{query_params}".format(
            base_url=self.authorize_url,
            query_params=requests.compat.urlencode(query_params),
        )
        return RedirectResponse(url)

    def fetch_user_details(self, request: Request) -> dict:
        """
        Method to fetch the user details. Should be used inside callback route
        :param request: request object
        :return: user details as dictionary
        """
        params = request.query_params
        code = params.get("code")
        if not code:
            raise HTTPException(status_code=403, detail="User not authorized")
        query_params = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.config.redirect_uri,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        exchange = requests.post(
            self.token_url,
            headers=headers,
            data=requests.compat.urlencode(query_params),
            proxies=PROXIES,
            auth=(self.config.client_id, self.config.client_secret),
        ).json()
        access_token = exchange.get("access_token", False)
        if not exchange.get("token_type"):
            raise HTTPException(
                status_code=403, detail="Unsupported token type. Should be 'Bearer'"
            )
        user_info = requests.get(
            self.user_info_url,
            proxies=PROXIES,
            headers={"Authorization": f"Bearer {access_token}"},
        ).json()
        return user_info
