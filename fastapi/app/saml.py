import os
from os import environ
from datetime import datetime, timedelta
from urllib.parse import urlparse, urlencode, urlunparse
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.settings import OneLogin_Saml2_Settings
from onelogin.saml2.idp_metadata_parser import (
    OneLogin_Saml2_IdPMetadataParser,
)

from fastapi import (
    APIRouter,
    Depends,
    Response,
    Request,
    HTTPException,
    Cookie,
)
from starlette.responses import RedirectResponse
from starlette.datastructures import UploadFile
from typing import Union, Optional

from jose import jwt
from jose.exceptions import JWTError

from fastapi.logger import logger
import logging

logger.setLevel(logging.DEBUG)

secret:str = environ.get('JWT_SECRET') or exit ( "JWT_SECRET ENV var required")
token_life = 3600

host: str = environ.get("FASTAPI_HOST") or exit(
    "FASTAPI_HOST env var required"
)
host = str.lower(host)
host_parsed = urlparse(host)

idp_metadata_url: str = environ.get("IDP_METADATA_URL") or exit(
    "IDP_METADATA_URL env var required"
)
# idp_metadata_url = 'https://dbspatial.us.auth0.com/samlp/metadata/vEJRZ0X6OtSMzkhBqIUMM62KDJhSNyG3'
idp_metadata_url = 'https://auth.launchpad-sbx.nasa.gov/unauth/metadata/launchpad-sbx.idp.xml'

default_return: str = environ.get("APT_FRONTEND_URL") or exit(
    "APT_FRONTEND_URL env var required"
)

router = APIRouter()

base_path = os.path.dirname(os.path.abspath(__file__))

idp_data = OneLogin_Saml2_IdPMetadataParser.parse_remote(
    idp_metadata_url
)
logger.debug("test debug")


def url_for_path(path):
    url = urlparse(host)
    return urlunparse(url._replace(path=path))


class SamlAuth:
    def __init__(
        self,
        request: Request,
        response: Response,
        RelayState: Optional[str] = default_return,
        return_to: Optional[str] = default_return,
        token: Optional[str] = Cookie(None),
        jwt: Optional[str] = None,
    ):
        self.request = request
        self.response = response
        # self.session = request.session

        self.base_url = host
        self.url = url_for_path(request.url.path)
        self.relay_state = (
            RelayState if RelayState != self.url else default_return
        )
        self.return_to = (
            return_to if return_to != self.url else default_return
        )
        self.auth = None
        self.settings = None
        self.name_id = None
        self.name_id_format = None
        self.nq = None
        self.spnq = None
        self.session_index = None
        self.userdata = None
        self.COOKIE_token = token
        self.GET_token = jwt
        self.token_data = self.get_token_data()
        self.user = self.userdata
        logger.warning(
            "url: %s %s, relay_state: %s %s return_to: %s %s",
            self.request.url,
            self.url,
            RelayState,
            self.relay_state,
            return_to,
            self.return_to,
        )

    def url_for(self, path):
        path = urlparse(self.request.url_for(path)).path
        return url_for_path(path)

    async def prepare_saml_request(self):
        url = urlparse(self.url)
        get_data = self.request.query_params._dict
        form = await self.request.form()
        post_data = {}
        for key, value in form.multi_items():
            if not isinstance(value, UploadFile):
                post_data[key] = value
            if key == 'RelayState':
                if value != self.url:
                    self.relay_state = value
        logger.warning(
            "prepare_saml_request url: %s, relay_state: %s return_to: %s",
            self.url,
            self.relay_state,
            self.return_to,
        )
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
        init_settings = {
            "strict": True,
            "debug": True,
            "sp": {
                "entityId": f"{self.base_url}/",
                "assertionConsumerService": {
                    "url": f"{self.url_for('acs')}",
                    "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST",
                },
                "singleLogoutService": {
                    "url": f"{self.url_for('slo')}",
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

        self.settings = OneLogin_Saml2_Settings(
            settings=init_settings, custom_base_path=base_path,
        )
        self.auth = OneLogin_Saml2_Auth(
            self.saml_request, old_settings=self.settings,
        )
        return self.auth

    def save_session(self):
        if self.user is not None:
            self.response.set_cookie(
                key="jwt", value=self.create_token()
            )

    def create_token_data(self):
        exp = datetime.utcnow() + timedelta(seconds=token_life)
        data = {
            "userdata": self.userdata,
            "name_id": self.name_id,
            "nq": self.nq,
            "spnq": self.spnq,
            "name_id_format": self.name_id_format,
            "session_index": self.session_index,
            "exp": exp,
            "role": "app_user",
        }
        return data

    def create_token(self):
        return jwt.encode(self.create_token_data(), secret)

    def parse_token(self, token):
        if token is None:
            return None
        try:
            contents = jwt.decode(token, secret)
            for key, value in contents.items():
                if hasattr(self, key):
                    setattr(self, key, value)
        except JWTError:
            return None
        return contents

    def get_auth_from_header(self):
        auth_header = self.request.headers.get("Authorization", None)
        if auth_header is None:
            return None
        scheme, _, token = auth_header.partition(" ")
        if scheme.lower() != "bearer":
            return None
        self.parse_token(token)

    def get_token_data(self):
        token_data = self.get_auth_from_header()
        if token_data is None or self.userdata is None:
            token_data = self.parse_token(self.COOKIE_token)
        if token_data is None or self.userdata is None:
            token_data = self.parse_token(self.GET_token)
        self.token_data = token_data
        return token_data

    def raise_autherror(self):
        if self.auth is not None:
            errors = self.auth.get_errors()
            if len(errors) > 0:
                msg = ",".join(errors)
                raise HTTPException(
                    status_code=401, detail=f"Errors: {msg}"
                )
        return None

    def redirect(self, url):
        # only redirect when there are no errors
        logger.warning('redirecting %s', url)
        self.raise_autherror()
        if self.userdata is None:
            response = RedirectResponse(url=url, status_code=303)
            response.delete_cookie("token")
        else:
            token = self.create_token()
            logger.warning('redirect %s %s', url, token)
            if token is not None:
                params = f"token={token}"
                url += ('&' if urlparse(url).query else '?') + params
                logger.warning('return url %s', url)
                response = RedirectResponse(url=url, status_code=303)
                response.set_cookie("token", token, max_age=3600)
        return response


async def saml_auth(saml: SamlAuth = Depends(SamlAuth)):
    await saml.get_auth()
    return saml


User = Union[dict, None]


async def require_user(saml: SamlAuth = Depends(SamlAuth)) -> User:
    if saml.userdata is not None:
        return saml.userdata
    raise HTTPException(
        status_code=401,
        detail=f"Not logged in. Please log in at {saml.url_for('sso')}",
    )


async def get_user(saml: SamlAuth = Depends(SamlAuth)) -> User:
    return saml.userdata


@router.get("/sso")
async def sso(
    saml: SamlAuth = Depends(saml_auth)
):
    return RedirectResponse(url=saml.auth.login(saml.return_to))


@router.post("/acs")
async def acs(saml: SamlAuth = Depends(saml_auth),):
    auth = saml.auth
    auth.process_response()
    saml.raise_autherror()
    saml.name_id = auth.get_nameid()
    saml.name_id_format = auth.get_nameid_format()
    saml.nq = auth.get_nameid_nq()
    saml.spnq = auth.get_nameid_spnq()
    saml.session_index = auth.get_session_index()
    saml.userdata = auth.get_attributes()
    logger.warning('acs relay_state: %s', saml.relay_state)
    if saml.relay_state != saml.url_for('sso'):
        relay_state = saml.relay_state
    else:
        logger.warning('Relay State set to SSO, changing to %s', default_return)
        relay_state = default_return
    return saml.redirect(relay_state)


@router.get("/slo")
@router.post("/slo")
async def slo(saml: SamlAuth = Depends(saml_auth)):
    auth = saml.auth
    logger.warning('slo return_to: %s, relay_state: %s', saml.return_to, saml.relay_state)
    url = auth.logout(
        return_to=saml.return_to,
        name_id=saml.name_id,
        session_index=saml.session_index,
        nq=saml.nq,
        name_id_format=saml.name_id_format,
        spnq=saml.spnq,
    )
    saml.userdata = None
    return saml.redirect(url)


@router.get("/sls")
@router.post("/sls")
async def sls(saml: SamlAuth = Depends(saml_auth)):
    auth = saml.auth
    auth.process_slo()
    logger.warning('acs relay_state: %s', saml.relay_state)
    if saml.relay_state != saml.request.url_for('slo'):
        relay_state = saml.relay_state
    else:
        logger.warning('Relay State set to SLO, changing to %s', default_return)
        relay_state = default_return
    return saml.redirect(relay_state)


@router.get("/attrs")
@router.post("/attrs")
async def attrs(saml: SamlAuth = Depends(saml_auth)):
    if saml.userdata is not None:
        ret = saml.userdata.copy()
        ret['token'] = saml.create_token()
        return ret
    raise HTTPException(
        status_code=401,
        detail=f"Not logged in. Please log in at {saml.request.url_for('sso')}",
    )


@router.get("/token")
async def token(saml: SamlAuth = Depends(saml_auth)):
    if saml.userdata is not None:
        return {"token": saml.create_token()}
    raise HTTPException(
        status_code=401,
        detail=f"Not logged in. Please log in at {saml.url_for('sso')}",
    )


@router.get("/metadata")
async def metadata(saml: SamlAuth = Depends(saml_auth)):
    settings = saml.settings
    metadata = settings.get_sp_metadata()
    errors = settings.validate_metadata(metadata)
    if len(errors) == 0:
        return Response(
            content=metadata, media_type="application/xml"
        )
    else:
        return Response(content=", ".join(errors), status_code=500)
