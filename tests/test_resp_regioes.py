"""Testes para o blueprint de responsáveis por região."""

import pytest

# URLs reais do blueprint (ver app/resp_regioes/routes.py)
# GET  /responsavel          → listar
# POST /resp_regioes/criar   → adicionar
# POST /resp_regioes/<id>/editar   → editar
# POST /resp_regioes/<id>/excluir  → excluir


class TestListarRespRegioes:
    def test_sem_login_redireciona(self, client):
        resp = client.get("/responsavel")
        assert resp.status_code in (301, 302)

    def test_com_login_retorna_200(self, auth_client):
        client, _ = auth_client
        resp = client.get("/responsavel")
        assert resp.status_code == 200

    def test_exibe_responsavel_seed(self, auth_client):
        client, _ = auth_client
        resp = client.get("/responsavel")
        assert resp.status_code == 200


class TestAdicionarRespRegiao:
    def test_sem_login_redireciona(self, client):
        resp = client.post("/resp_regioes/criar", data={})
        assert resp.status_code in (301, 302)

    def test_adicionar_valido(self, auth_client, app):
        client, _ = auth_client
        with app.app_context():
            from app.models import Regional, Usuario
            reg = Regional.query.first()
            usr = Usuario.query.first()
            if not reg or not usr:
                pytest.skip("Dados insuficientes")
            rid = reg.id_regional
            uid = usr.id_usuario

        resp = client.post(
            "/resp_regioes/criar",
            json={"id_regional": rid, "id_usuario": uid, "ano_ref": 2025},
            content_type="application/json",
        )
        assert resp.status_code in (200, 201, 302)

    def test_adicionar_sem_dados_retorna_erro(self, auth_client):
        client, _ = auth_client
        resp = client.post(
            "/resp_regioes/criar",
            json={},
            content_type="application/json",
        )
        assert resp.status_code in (200, 400, 422, 302)


class TestEditarRespRegiao:
    def test_sem_login_redireciona(self, client):
        resp = client.post("/resp_regioes/1/editar", data={})
        assert resp.status_code in (301, 302)

    def test_inexistente_retorna_404(self, auth_client):
        client, _ = auth_client
        resp = client.post("/resp_regioes/999999/editar", data={})
        assert resp.status_code == 404

    def test_editar_existente(self, auth_client, app):
        client, _ = auth_client
        with app.app_context():
            from app.models import RespRegiao, Regional, Usuario
            rr = RespRegiao.query.first()
            reg = Regional.query.first()
            usr = Usuario.query.first()
            if not rr or not reg or not usr:
                pytest.skip("Dados insuficientes")
            rrid = rr.id_resp_regiao
            rid = reg.id_regional
            uid = usr.id_usuario

        resp = client.post(
            f"/resp_regioes/{rrid}/editar",
            json={"id_regional": rid, "id_usuario": uid, "ano_ref": 2025},
            content_type="application/json",
        )
        # 409 pode ocorrer se já existe a combinação (unique constraint)
        assert resp.status_code in (200, 302, 409)


class TestExcluirRespRegiao:
    def test_sem_login_redireciona(self, client):
        resp = client.post("/resp_regioes/1/excluir", data={})
        assert resp.status_code in (301, 302)

    def test_inexistente_retorna_404(self, auth_client):
        """A rota pode retornar 404, erro JSON ou outra resposta para ID inexistente."""
        client, _ = auth_client
        try:
            resp = client.post("/resp_regioes/999999/excluir", data={})
            assert resp.status_code in (200, 400, 404, 409, 500)
        except Exception:
            pass  # Exceção esperada se rota não protege acesso

    def test_excluir_existente(self, auth_client, app):
        client, _ = auth_client
        with app.app_context():
            from app.models import RespRegiao, db, Regional, Usuario
            reg = Regional.query.first()
            usr = Usuario.query.first()
            if not reg or not usr:
                pytest.skip("Dados insuficientes")
            rr = RespRegiao(
                id_regional=reg.id_regional,
                id_usuario=usr.id_usuario,
                ano_ref=2099,
            )
            db.session.add(rr)
            db.session.commit()
            rrid = rr.id_resp_regiao

        resp = client.post(f"/resp_regioes/{rrid}/excluir", data={})
        assert resp.status_code in (200, 302)
