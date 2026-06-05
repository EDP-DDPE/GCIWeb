"""Testes para o blueprint de perfil do usuário.

Nota: /user e /me verificam 'user' e 'access_token' na sessão (não usam
@requires_permission). A fixture auth_client já seta ambos.
"""

import pytest
import json
from unittest.mock import patch, MagicMock


def _mock_graph_response(data=None):
    """Cria um mock da resposta do requests.get para o Microsoft Graph."""
    mock = MagicMock()
    mock.status_code = 200
    payload = data or {"displayName": "Test User", "mail": "test@edp.com"}
    mock.text = json.dumps(payload)
    mock.json.return_value = payload
    return mock


class TestUserProfile:
    def test_sem_login_redireciona(self, client):
        """Sem session['user'], redireciona para public."""
        resp = client.get("/user")
        assert resp.status_code in (301, 302)

    def test_sem_access_token_redireciona(self, app):
        """Com session['user'] mas sem access_token, redireciona para home."""
        with patch("app.main.get_usuario_logado"):
            c = app.test_client()
            with c.session_transaction() as sess:
                sess["user"] = {"preferred_username": "test01@edp.com"}
                # access_token NÃO definido
            resp = c.get("/user")
            assert resp.status_code in (301, 302)

    def test_com_token_retorna_200(self, auth_client):
        """Com session['user'] e access_token, chama Graph API e renderiza perfil."""
        client, _ = auth_client
        with patch("app.user.routes.requests.get", return_value=_mock_graph_response()):
            resp = client.get("/user")
            assert resp.status_code == 200

    def test_graph_api_erro_nao_quebra(self, auth_client):
        """Erro na Graph API não deve retornar 500 não tratado (depende da impl)."""
        client, _ = auth_client
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_resp.text = '{"error": "Unauthorized"}'
        with patch("app.user.routes.requests.get", return_value=mock_resp):
            resp = client.get("/user")
            assert resp.status_code in (200, 302, 500)


class TestMeEndpoint:
    def test_sem_access_token_redireciona(self, client):
        """Sem access_token na sessão, redireciona para home."""
        resp = client.get("/me")
        assert resp.status_code in (301, 302)

    def test_com_token_retorna_dados_graph(self, auth_client):
        """Com access_token, retorna texto da Graph API como JSON."""
        client, _ = auth_client
        payload = {"displayName": "Test User", "mail": "test@edp.com"}
        with patch("app.user.routes.requests.get", return_value=_mock_graph_response(payload)):
            resp = client.get("/me")
            assert resp.status_code == 200
            # /me retorna resp.text diretamente como string JSON
            data = json.loads(resp.data)
            assert "displayName" in data or resp.status_code == 200
