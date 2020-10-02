import os

from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.utils import OneLogin_Saml2_Utils

from flask import Flask, redirect

from starlette.requests import HTTPConnection
from starlette.middleware.sessions import SessionMiddleware

app.add_middleware(SessionMiddleware, secret_key="ASFDASDFASWEsdfsfsadfas")

secret_key = 'lksjlksjlsdkajsdjlkf'
saml_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'saml')


def init_saml_auth(req):
    auth = OneLogin_Saml2_Auth(req, custom_base_path=app.config['SAML_PATH'])
    return auth


def prepare_request(request):
    return {
            'https': 'on' if request.url.scheme == 'https' else 'off',
            'http_host': request.client.host,
            'server_port': request.url.port,
            'script_name': request.url.path,
            'get_data': request.query_params.copy(),
            'post_data': request.form.copy(),
        }


def prepare_session(request):
    session = request.session
    rs = {}
    name_id = session_index = name_id_format = name_id_nq = name_id_spnq = None
    if 'samlNameId' in session:
        rs['name_id'] = session['samlNameId']
    if 'samlSessionIndex' in session:
        rs['session_index'] = session['samlSessionIndex']
    if 'samlNameIdFormat' in session:
        rs['name_id_format'] = session['samlNameIdFormat']
    if 'samlNameIdNameQualifier' in session:
        rs['name_id_nq'] = session['samlNameIdNameQualifier']
    if 'samlNameIdSPNameQualifier' in session:
        rs['name_id_spnq'] = session['samlNameIdSPNameQualifier']
    return rs


class SamlAuth:
    def __init__(self, request):
        self.auth = authenticate(request)
        self.session = request.session

    def authenticate(self, request):
        req = prepare_request(request)
        auth = init_saml_auth(req)


@app.get('saml/sso')
def sso():
    return redirect(auth.login())

@app.get('saml/sso2')
def sso2():
    return_to = f'{req.host}/attrs'
    return redirect(auth.login(return_to))

@app.get('saml/acs')
def acs():
    request_id = None
    session = request.session
    if 'AuthNRequestID' in session:
        request_id = session['AuthNRequestID']

    auth.process_response(request_id=request_id)
    errors = auth.get_errors()
    not_auth_warn = not auth.is_authenticated()
    if len(errors) == 0:
        if 'AuthNRequestID' in session:
            del session['AuthNRequestID']
        session['samlUserdata'] = auth.get_attributes()
        session['samlNameId'] = auth.get_nameid()
        session['samlNameIdFormat'] = auth.get_nameid_format()
        session['samlNameIdNameQualifier'] = auth.get_nameid_nq()
        session['samlNameIdSPNameQualifier'] = auth.get_nameid_spnq()
        session['samlSessionIndex'] = auth.get_session_index()
        self_url = OneLogin_Saml2_Utils.get_self_url(req)
        if 'RelayState' in request.form and self_url != request.form['RelayState']:
            return redirect(auth.redirect_to(request.form['RelayState']))
    elif auth.get_settings().is_debug_active():
        error_reason = auth.get_last_error_reason()


@app.get('saml/slo')
def slo():
    session = prepare_session(request)
    return redirect(auth.logout(**session))


@app.get('saml/sls')
def sls():
    request_id = None
    session = request.session
    if 'LogoutRequestID' in session:
        request_id = session['LogoutRequestID']
    dscb = lambda: session.clear()
    url = auth.process_slo(request_id=request_id, delete_session_cb=dscb)
    errors = auth.get_errors()
    if len(errors) == 0:
        if url is not None:
            return redirect(url)
        else:
            success_slo = True
    elif auth.get_settings().is_debug_active():
        error_reason = auth.get_last_error_reason()


@app.get('saml/attrs')
def attrs():
    session = request.session
    if len(session['samlUserdata']) > 0:
        attributes = session['samlUserdata'].items()
    return render_template(
        'attrs.html',
        paint_logout=paint_logout,
        attributes=attributes
    )


@app.get('/metadata')
def metadata():
    settings = auth.get_settings()
    metadata = auth.get_sp_metadata()
    errors = settings.validate_metadata()
    if len(errors) == 0:
        resp = make_response(metadata, 200)
        resp.headers['Content-Type'] = 'text/xml'
    else:
        resp = make_response(', '.join(errors), 500)
    return resp
