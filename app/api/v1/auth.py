from app import config
from app.logs import logger
from app.auth.saml import SamlAuth, saml_auth

from fastapi import (
    APIRouter,
    Depends,
    Response,
    HTTPException,
)
from starlette.responses import RedirectResponse

router = APIRouter()

mockauth = config.IDP_METADATA_URL == "mock"


@router.get("/sso")
async def sso(saml: SamlAuth = Depends(saml_auth)):
    if mockauth:
        print(f"Redirecting to : {saml.url_for('acs')}?RelayState={saml.return_to}")
        return RedirectResponse(
            url=f"{saml.url_for('acs')}?RelayState={saml.return_to}"
        )
    return RedirectResponse(url=saml.auth.login(saml.return_to))


@router.post("/acs")
@router.get("/acs")
async def acs(saml: SamlAuth = Depends(saml_auth),):
    auth = saml.auth
    if mockauth:
        saml.name_id = "nameid"
        saml.name_id_format = "format"
        saml.nq = "nq"
        saml.spnq = "spnq"
        saml.session_index = "index"
        saml.userdata = {"user": "mockauth-user"}
    else:
        auth.process_response()
        saml.raise_autherror()
        saml.name_id = auth.get_nameid()
        saml.name_id_format = auth.get_nameid_format()
        saml.nq = auth.get_nameid_nq()
        saml.spnq = auth.get_nameid_spnq()
        saml.session_index = auth.get_session_index()
        saml.userdata = auth.get_attributes()
    logger.warning("acs relay_state: %s", saml.relay_state)
    if saml.relay_state != saml.url_for("sso"):
        relay_state = saml.relay_state
    else:
        logger.warning("Relay State set to SSO, changing to %s", config.FRONTEND_URL)
        relay_state = config.FRONTEND_URL
    return saml.redirect(relay_state)


@router.get("/slo")
@router.post("/slo")
async def slo(saml: SamlAuth = Depends(saml_auth)):
    auth = saml.auth
    logger.warning(
        "slo return_to: %s, relay_state: %s", saml.return_to, saml.relay_state
    )
    if mockauth:
        saml.userdata = None
        return saml.redirect(saml.return_to)
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
    logger.warning("acs relay_state: %s", saml.relay_state)
    if saml.relay_state != saml.request.url_for("slo"):
        relay_state = saml.relay_state
    else:
        logger.warning("Relay State set to SLO, changing to %s", config.FRONTEND_URL)
        relay_state = config.FRONTEND_URL
    return saml.redirect(relay_state)


@router.get("/attrs")
@router.post("/attrs")
async def attrs(saml: SamlAuth = Depends(saml_auth)):
    if saml.userdata is not None:
        ret = saml.userdata.copy()
        ret["token"] = saml.create_token()
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
        return Response(content=metadata, media_type="application/xml")
    else:
        return Response(content=", ".join(errors), status_code=500)
