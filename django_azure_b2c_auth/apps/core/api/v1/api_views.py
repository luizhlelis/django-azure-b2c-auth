import logging

import msal

from django.shortcuts import redirect
from django.urls import reverse
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from django_azure_b2c_auth.apps.core.api.api_exception import B2CContractNotRespectedException
from django_azure_b2c_auth.apps.core.api.api_exception import ServiceUnavailable
from django_azure_b2c_auth.apps.core.services.microsoft_b2c import obtain_access_token
from django_azure_b2c_auth.apps.core.services.microsoft_b2c import verify_flow
from django_azure_b2c_auth.settings import B2C_AUTHORITY_SIGN_UP_SIGN_IN
from django_azure_b2c_auth.settings import B2C_SCOPES

logger = logging.getLogger(__name__)


@api_view(["GET"])
def handle_response_oidc(request: Request) -> Response:
    current_referer = request.headers.get("referer")
    logger.info("It came from %s", current_referer)

    code_from_user_flow = request.query_params.get("code")
    auth_flow_details = request.session.pop("flow", {})
    auth_flow_details = auth_flow_details if auth_flow_details else request.session.pop("flow-edit", {})
    if not code_from_user_flow or not auth_flow_details:
        # I got this error after cancelling my PROFILE EDIT flow: error=access_denied&error_description=AADB2C90091: The user has cancelled entering self-asserted information.
        raise B2CContractNotRespectedException

    logger.debug("Trying to finish the flow")
    cache = _load_cache(request)
    acquire_token_details = verify_flow(auth_flow_details, request.query_params)
    if acquire_token_details.error:
        logger.error(
            "We got %s! Its description: %s",
            acquire_token_details.error,
            acquire_token_details.error_description,
        )
        raise ServiceUnavailable
    else:
        _save_cache(request, cache)
        # I could set a cookie with HttpOnly right here for instance
        request.session["user"] = acquire_token_details.id_token_claims
        location_index = reverse("index")
        return redirect(location_index)


@api_view(["GET"])
def consult_user_data(request):
    cache = _load_cache(request)
    hard_coded_scopes = B2C_SCOPES
    result = obtain_access_token(hard_coded_scopes, cache, B2C_AUTHORITY_SIGN_UP_SIGN_IN)
    _save_cache(request, cache)

    access_token = result.get("access_token")
    if not access_token:
        logger.warning("Authentication gives you an id token only. Authorization to a resource gives you access tokens")

    return Response(data=result)


@api_view(["GET"])
def what_do_i_have(request):
    id_token_claims = request.session["user"]
    return Response(data=id_token_claims)


def _load_cache(request):
    cache = msal.SerializableTokenCache()
    token_cache = request.session.get("token_cache")
    if token_cache:
        cache.deserialize(token_cache)
    return cache


def _save_cache(request, cache):
    if cache.has_state_changed:
        request.session["token_cache"] = cache.serialize()
