import os
from os import environ
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.settings import OneLogin_Saml2_Settings
from onelogin.saml2.idp_metadata_parser import OneLogin_Saml2_IdPMetadataParser

from fastapi import APIRouter, Depends, Response, Request, HTTPException
from starlette.responses import RedirectResponse
from starlette.datastructures import UploadFile
from typing import Union

from fastapi.logger import logger
import logging

logger.setLevel(logging.DEBUG)

host: str = environ.get("FASTAPI_HOST") or exit(
    "FASTAPI_HOST env var required"
)
host = str.lower(host)

idp_metadata_url: str = environ.get("IDP_METADATA_URL") or exit(
    "IDP_METADATA_URL env var required"
)


router = APIRouter()

base_path = os.path.dirname(os.path.abspath(__file__))

idp_data = OneLogin_Saml2_IdPMetadataParser.parse_remote(
    idp_metadata_url
)
logger.debug('test debug')

init_settings = {
    "strict": True,
    "debug": True,
    "sp": {
        "entityId": f"{host}/metadata",
        "assertionConsumerService": {
            "url": f"{host}/acs",
            "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST",
        },
        "singleLogoutService": {
            "url": f"{host}/sls",
            "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
        },
        "NameIDFormat": "urn:oasis:names:tc:SAML:2.0:nameid-format:persistent",
        "x509cert": "",
        "privateKey": "",
    },
    "idp": idp_data["idp"],
    "security": {
        "nameIdEncrypted": False,
        "authnRequestsSigned": False,
        "logoutRequestSigned": False,
        "logoutResponsesSigned": False,
        "signMetadata": False,
        "wantMessagesSigned": False,
        "wantAssertionsSigned": False,
        "wantNameId": False,
        "wantNameIdEncrypted": False,
        "signatureAlgorithm": "http://www.w3.org/2001/04/xmldsig-more#rsa-sha256",
        "digestAlgorithm": "http://www.w3.org/2001/04/xmlenc#sha256",
    },
}

settings = OneLogin_Saml2_Settings(
    settings=init_settings,
    custom_base_path=base_path,
)


class SamlAuth:
    def __init__(
        self,
        request: Request,
    ):
        self.request = request
        self.session = request.session
        self.user = None
        userdata = request.session.get("samlUserdata")
        if userdata and len(userdata) > 0:
            self.user = userdata.items()
        self.auth = None
        self.acs_url = request.url_for("acs")
        self.sso_url = request.url_for("sso")
        self.metadata_url = request.url_for("metadata")
        self.attrs_url = request.url_for("attrs")
        self.slo_url = request.url_for("slo")
        url = request.url
        self.base_url = f'{url.scheme}://{url.hostname}:{url.port}'

    async def prepare_saml_request(self):
        url = self.request.url
        get_data = self.request.query_params._dict
        form = await self.request.form()
        post_data = {}
        for key, value in form.multi_items():
            if not isinstance(value, UploadFile):
                post_data[key] = value

        return {
            "https": "on" if url.scheme == "https" else "off",
            "http_host": url.hostname,
            "server_port": url.port,
            "script_name": url.path,
            "get_data": get_data,
            "post_data": post_data,
        }

    async def get_auth(self):
        self.saml_request = await self.prepare_saml_request()
        self.auth = OneLogin_Saml2_Auth(
            self.saml_request,
            old_settings=settings,
        )
        return self.auth


async def saml_auth(request: Request):
    saml = SamlAuth(request)
    await saml.get_auth()
    return saml


User = Union[dict, None]


async def require_user(request: Request) -> User:
    saml = SamlAuth(request)
    if saml.user is not None:
        return saml.user
    raise HTTPException(status_code=401)


async def get_user(request: Request) -> User:
    saml = SamlAuth(request)
    return saml.user


@router.get("/sso")
async def sso(
    saml: SamlAuth = Depends(saml_auth), return_to: str = host
):
    return RedirectResponse(url=saml.auth.login(return_to))


@router.post("/acs")
async def acs(
    saml: SamlAuth = Depends(saml_auth),
):
    auth = saml.auth
    session = saml.session
    saml_request = saml.saml_request
    request_id = None
    if "AuthNRequestID" in session:
        request_id = session["AuthNRequestID"]
    auth.process_response(request_id=request_id)
    errors = auth.get_errors()
    if len(errors) == 0:
        if "AuthNRequestID" in session:
            del session["AuthNRequestID"]
        session["samlUserdata"] = auth.get_attributes()
        session["samlNameId"] = auth.get_nameid()
        session["samlNameIdFormat"] = auth.get_nameid_format()
        session["samlNameIdNameQualifier"] = auth.get_nameid_nq()
        session["samlNameIdSPNameQualifier"] = auth.get_nameid_spnq()
        session["samlSessionIndex"] = auth.get_session_index()
        self_url = saml.acs_url
        RelayState = saml_request.get("post_data").get("RelayState", None)
        if RelayState and self_url != RelayState:
            return RedirectResponse(url=RelayState, status_code=303)
        else:
            return RedirectResponse(url=saml.attrs_url, status_code=303)
    elif auth.get_settings().is_debug_active():
        error_reason = auth.get_last_error_reason()
        return {"authorization_error": error_reason}


@router.get("/slo")
@router.post("/slo")
async def slo(
    saml: SamlAuth = Depends(saml_auth), return_to: str = host
):
    auth = saml.auth
    session = saml.session
    url = auth.logout(
        return_to=return_to,
        name_id=session.get("samlNameId", None),
        session_index=session.get("samlSessionIndex", None),
        nq=session.get("samlNameIdNameQualifier", None),
        name_id_format=session.get("samlNameIdFormat", None),
        spnq=session.get("samlNameIdSPNameQualifier", None),
    )
    return RedirectResponse(url=url)


@router.get("/sls")
@router.post("/sls")
async def sls(
    saml: SamlAuth = Depends(saml_auth), RelayState: str = host
):
    request_id = None
    session = saml.session
    auth = saml.auth
    if "LogoutRequestID" in session:
        request_id = session["LogoutRequestID"]
    auth.process_slo(request_id=request_id, delete_session_cb=session.clear)
    session.clear()
    errors = auth.get_errors()
    if len(errors) == 0:
        return RedirectResponse(url=RelayState, status_code=303)
    elif auth.get_settings().is_debug_active():
        error_reason = auth.get_last_error_reason()
        return {"logout_error": error_reason}


@router.get("/attrs")
@router.post("/attrs")
async def attrs(user: User = Depends(require_user)):
    return user


@router.get("/metadata")
async def metadata(saml: SamlAuth = Depends(saml_auth)):
    metadata = settings.get_sp_metadata()
    errors = settings.validate_metadata(metadata)
    if len(errors) == 0:
        return Response(content=metadata, media_type="application/xml")
    else:
        return Response(content=", ".join(errors), status_code=500)
