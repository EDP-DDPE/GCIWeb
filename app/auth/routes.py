from flask import Blueprint, session, redirect, url_for, request, current_app, render_template
from urllib.parse import quote_plus
import msal


def create_auth_blueprint(redirect_path="/auth/callback"):
    """
    Cria e retorna o Blueprint de autenticação, com rotas:
      - /login
      - redirect_path (callback, ex.: /auth/callback)
      - /logout
    O redirect_path é definido ANTES do registro do blueprint
    para evitar o AssertionError.
    """
    auth_bp = Blueprint("auth", __name__, template_folder='templates')

    # ========= Helpers MSAL =========
    def _msal_app(cache=None):
        cfg = current_app.config
        return msal.ConfidentialClientApplication(
            cfg["AUTH_CLIENT_ID"],
            authority=cfg["AUTH_AUTHORITY"],
            client_credential=cfg["AUTH_CLIENT_SECRET"],
            token_cache=cache,
        )

    def _auth_url(scopes=None):
        cfg = current_app.config
        # Garantir que scopes seja sempre uma lista e NÃO inclua scopes OIDC
        if scopes is None:
            scopes = cfg["AUTH_SCOPES"]

        # Converter para lista se necessário
        if isinstance(scopes, (set, frozenset)):
            scopes = list(scopes)
        elif isinstance(scopes, str):
            scopes = [scopes]
        elif not isinstance(scopes, list):
            scopes = list(scopes) if scopes else []

        # REMOVER scopes OIDC se estiverem presentes (são automáticos)
        oidc_scopes = {"openid", "profile", "offline_access"}
        scopes = [s for s in scopes if s not in oidc_scopes]

        print(f"[DEBUG] Scopes sendo usados (sem OIDC): {scopes} (tipo: {type(scopes)})")

        flow = _msal_app().initiate_auth_code_flow(
            scopes=scopes,
            redirect_uri=cfg["AUTH_REDIRECT_URI"],
        )
        session["flow"] = flow
        return flow["auth_uri"]

    # ========= Rotas =========

    @auth_bp.route("/public")
    def public():
        return render_template('auth/login.html')


    @auth_bp.route("/login")
    def login():
        # Limpar qualquer sessão anterior para evitar conflitos
        if "flow" in session:
            session.pop("flow", None)
        if "last_processed_code" in session:
            session.pop("last_processed_code", None)

        scopes = current_app.config["AUTH_SCOPES"]
        print(f"[DEBUG] Iniciando novo login com scopes: {scopes}")

        try:
            auth_url = _auth_url(scopes)
            print(f"[DEBUG] Redirecionando para: {auth_url[:50]}...")
            return redirect(auth_url)
        except Exception as e:
            print(f"[DEBUG] Erro ao gerar URL de auth: {e}")
            return f"Erro ao iniciar login: {str(e)}", 500

    @auth_bp.route("/logout")
    def logout():
        cfg = current_app.config
        session.clear()
        # Se não existir um blueprint "main" para a home, troque por url_for("index")
        return redirect(
            "https://login.microsoftonline.com/"
            f"{cfg['AUTH_TENANT_ID']}/oauth2/v2.0/logout"
            f"?post_logout_redirect_uri={quote_plus(url_for('main.home', _external=True))}"
        )

    @auth_bp.route("/clear-session")
    def clear_session():
        """Rota para limpar a sessão em caso de problemas"""
        session.clear()
        return redirect(url_for("main.home"))

    @auth_bp.route("/fresh-login")
    def fresh_login():
        """Força um novo login completamente limpo"""
        session.clear()
        print("[DEBUG] Sessão limpa - iniciando fresh login")
        return redirect(url_for("auth.login"))

    # Callback DINÂMICO definido ANTES do registro
    @auth_bp.route(redirect_path, endpoint="callback")
    def callback():
        try:
            # Verificar se há código de autorização nos parâmetros
            if not request.args.get('code'):
                print("[DEBUG] Nenhum código de autorização recebido")
                return redirect(url_for("auth.login"))

            if "flow" not in session:
                print("[DEBUG] Flow não encontrado na sessão, redirecionando para login")
                return redirect(url_for("auth.login"))

            # Verificar se já processamos este callback (evitar reprocessamento)
            current_code = request.args.get('code')
            if session.get('last_processed_code') == current_code:
                print("[DEBUG] Código já processado, redirecionando para home")
                return redirect(url_for("main.home"))

            # Debug da sessão e args
            flow_state = session.get('flow', {}).get('state', 'N/A')
            request_state = request.args.get('state', 'N/A')
            print(f"[DEBUG] Flow state: {flow_state}")
            print(f"[DEBUG] Request state: {request_state}")
            print(f"[DEBUG] Authorization code: {current_code[:10]}..." if current_code else "N/A")

            # Verificar se há erro na resposta
            if request.args.get('error'):
                error_desc = request.args.get('error_description', 'Erro desconhecido')
                print(f"[DEBUG] Erro OAuth: {error_desc}")
                session.clear()
                return f"Erro OAuth: {error_desc}", 400

            # Fazer uma cópia do flow antes de usar
            flow_data = session.get("flow").copy()

            result = _msal_app().acquire_token_by_auth_code_flow(
                flow_data, request.args
            )

            if "error" in result:
                error_code = result.get("error")
                msg = result.get("error_description") or result.get("error")
                print(f"[DEBUG] Erro MSAL: {error_code} - {msg}")

                # Se o código já foi usado, limpar sessão e tentar novo login
                if "AADSTS54005" in msg or "already redeemed" in msg:
                    session.clear()
                    return redirect(url_for("auth.login"))

                return f"Erro MSAL: {msg}", 400

            # Marcar este código como processado
            session['last_processed_code'] = current_code

            # Limpar o flow da sessão após uso bem-sucedido
            session.pop("flow", None)

            # Salvar dados do usuário
            session["user"] = result.get("id_token_claims")
            session["access_token"] = result.get("access_token")
            session["refresh_token"] = result.get("refresh_token")

            user_name = result.get('id_token_claims', {}).get('name', 'N/A')
            print(f"[DEBUG] Login bem-sucedido para: {user_name}")

            return redirect(url_for("main.home"))

        except ValueError as e:
            error_msg = str(e)
            print(f"[DEBUG] ValueError: {error_msg}")
            if "state mismatch" in error_msg:
                print("[DEBUG] State mismatch - limpando sessão e redirecionando")
                session.clear()
                return redirect(url_for("auth.login"))
            else:
                session.clear()
                return f"Erro de validação: {error_msg}", 400

        except Exception as e:
            print(f"[DEBUG] Erro inesperado no callback: {e}")
            session.clear()
            return f"Erro inesperado: {str(e)}", 500

    return auth_bp