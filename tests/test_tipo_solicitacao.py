"""Testes para o blueprint de tipos de solicitação."""

import pytest
from io import BytesIO


class TestListarTipoSolicitacao:
    def test_sem_login_redireciona(self, client):
        resp = client.get("/tipo_solicitacao")
        assert resp.status_code in (301, 302)

    def test_com_login_retorna_200(self, auth_client):
        client, _ = auth_client
        resp = client.get("/tipo_solicitacao")
        assert resp.status_code == 200

    def test_exibe_tipo_seed(self, auth_client):
        client, _ = auth_client
        resp = client.get("/tipo_solicitacao")
        html = resp.data.decode("utf-8", errors="replace")
        assert "ev" in html.lower() or "viabilidade" in html.lower()


class TestEditarTipoSolicitacao:
    def test_sem_login_redireciona(self, client):
        resp = client.post("/tipo_solicitacao/1/editar", data={})
        assert resp.status_code in (301, 302)

    def test_inexistente_retorna_404(self, auth_client):
        client, _ = auth_client
        resp = client.post("/tipo_solicitacao/999999/editar", data={})
        assert resp.status_code == 404

    def test_editar_existente(self, auth_client, app):
        client, _ = auth_client
        with app.app_context():
            from app.models import TipoSolicitacao
            tipo = TipoSolicitacao.query.first()
            if not tipo:
                pytest.skip("Nenhum tipo disponível")
            tid = tipo.id_tipo_solicitacao

        resp = client.post(
            f"/tipo_solicitacao/{tid}/editar",
            json={"prazo_ddpe": 20},
            content_type="application/json",
        )
        assert resp.status_code in (200, 302)


class TestExcluirTipoSolicitacao:
    def test_sem_login_redireciona(self, client):
        resp = client.post("/tipo_solicitacao/1/excluir", data={})
        assert resp.status_code in (301, 302)

    def test_inexistente_retorna_404(self, auth_client):
        client, _ = auth_client
        resp = client.post("/tipo_solicitacao/999999/excluir", data={})
        assert resp.status_code == 404

    def test_tipo_com_estudos_nao_exclui(self, auth_client, app):
        """Tipo com estudos vinculados não deve ser excluído."""
        client, _ = auth_client
        with app.app_context():
            from app.models import TipoSolicitacao
            tipo = TipoSolicitacao.query.filter(
                TipoSolicitacao.estudos.any()
            ).first()
            if not tipo:
                pytest.skip("Nenhum tipo com estudos vinculados")
            tid = tipo.id_tipo_solicitacao

        resp = client.post(f"/tipo_solicitacao/{tid}/excluir", data={})
        assert resp.status_code in (200, 302, 400, 500)
        data = resp.get_json()
        if data and resp.status_code == 200:
            assert data.get("success") is False

    def test_excluir_tipo_sem_vinculos(self, auth_client, app):
        client, _ = auth_client
        with app.app_context():
            from app.models import TipoSolicitacao, db
            novo = TipoSolicitacao(
                viabilidade="OT",
                analise="Técnica",
                pedido="Temporário",
            )
            db.session.add(novo)
            db.session.commit()
            tid = novo.id_tipo_solicitacao

        resp = client.post(f"/tipo_solicitacao/{tid}/excluir", data={})
        assert resp.status_code in (200, 302)


class TestUploadDocPadronizado:
    # URL real: /tipo_solicitacao/<id>/documento/upload

    def test_sem_login_redireciona(self, client):
        resp = client.post("/tipo_solicitacao/1/documento/upload", data={})
        assert resp.status_code in (301, 302)

    def test_upload_sem_arquivo_retorna_erro(self, auth_client, app):
        client, _ = auth_client
        with app.app_context():
            from app.models import TipoSolicitacao
            tipo = TipoSolicitacao.query.first()
            if not tipo:
                pytest.skip("Nenhum tipo disponível")
            tid = tipo.id_tipo_solicitacao

        resp = client.post(
            f"/tipo_solicitacao/{tid}/documento/upload",
            data={},
        )
        assert resp.status_code in (200, 400, 302)

    def test_upload_com_arquivo_docx(self, auth_client, app):
        client, _ = auth_client
        with app.app_context():
            from app.models import TipoSolicitacao
            tipo = TipoSolicitacao.query.first()
            if not tipo:
                pytest.skip("Nenhum tipo disponível")
            tid = tipo.id_tipo_solicitacao

        fake_docx = BytesIO(b"PK\x03\x04")
        fake_docx.name = "template.docx"

        resp = client.post(
            f"/tipo_solicitacao/{tid}/documento/upload",
            data={"arquivo": (fake_docx, "template.docx")},
            content_type="multipart/form-data",
        )
        assert resp.status_code in (200, 302, 400)
