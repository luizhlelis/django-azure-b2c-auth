from dataclasses import dataclass
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import msal

from django.http import QueryDict
from msal import ConfidentialClientApplication
from msal import SerializableTokenCache

from django_azure_b2c_auth.settings import B2C_AUTHORITY_SIGN_UP_SIGN_IN
from django_azure_b2c_auth.settings import B2C_YOUR_APP_CLIENT_APPLICATION_ID
from django_azure_b2c_auth.settings import B2C_YOUR_APP_CLIENT_CREDENTIAL


@dataclass(frozen=True)
class AuthFlowDetails:
    state: str
    scope: List[str]
    auth_uri: str
    code_verifier: str
    nonce: str
    claims_challenge: str
    redirect_uri: Optional[str] = None


@dataclass(frozen=True)
class AcquireTokenDetails:
    id_token: str = None
    token_type: str = None
    not_before: int = None
    client_info: str = None
    scope: str = None
    refresh_token: str = None
    refresh_token_expires_in: int = None
    id_token_claims: Dict[str, Union[int, str, List[str]]] = None
    error: Optional[str] = None
    error_description: Optional[str] = None


def retrieve_client_app(cache: SerializableTokenCache = None, authority: str = None) -> ConfidentialClientApplication:
    return msal.ConfidentialClientApplication(
        B2C_YOUR_APP_CLIENT_APPLICATION_ID,
        authority=authority,
        client_credential=B2C_YOUR_APP_CLIENT_CREDENTIAL,
        token_cache=cache,
    )


def build_logout_uri(post_logout_redirect_uri: str = None):
    # https://xptoorg.b2clogin.com/xptoorg.onmicrosoft.com/v2.0/.well-known/openid-configuration?p=B2C_1_sign-in-sign-up
    # You can grab the link above if you click on "Run user flow"
    address = f"{B2C_AUTHORITY_SIGN_UP_SIGN_IN}/oauth2/v2.0/logout"

    if post_logout_redirect_uri:
        return f"{address}?post_logout_redirect_uri={post_logout_redirect_uri}"

    return address


def verify_flow(auth_flow_details: Dict, query_params: QueryDict) -> AcquireTokenDetails:
    authority = auth_flow_details["auth_uri"].split("/oauth2")[0]
    msal_app = retrieve_client_app(authority=authority)
    result = msal_app.acquire_token_by_auth_code_flow(auth_flow_details, query_params)
    return AcquireTokenDetails(**result)


def build_auth_code_flow(authority: str = None, scopes: List[str] = None, redirect_uri: str = None) -> AuthFlowDetails:
    msal_app = retrieve_client_app(authority=authority)

    scopes = scopes if scopes else []
    value = msal_app.initiate_auth_code_flow(scopes, redirect_uri)

    return AuthFlowDetails(**value)

def obtain_access_token(scopes=None, cache=None, authority=None) -> dict:
    msal_app = retrieve_client_app(cache=cache, authority=authority)
    accounts = msal_app.get_accounts()
    # So all account(s) belong to the current signed-in user!
    if accounts:
        first_account = accounts[0]
        result = msal_app.acquire_token_silent(scopes, account=first_account)
        return result
