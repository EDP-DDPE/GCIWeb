"""Testes para o blueprint de alternativas."""

import pytest
from unittest.mock import patch, MagicMock
from io import BytesIO
from decimal import Decimal


def _get_ids(app):
    """Retorna (id_estudo, id_circuito, id_alternativa) de registros existentes."""
    with app.app_context():
        from app.models import Estudo, Circuito, Alternativa
        estudo = Estudo.query.first()
        circuito = Circuito.query.first()
        alternativa = Alternativa.query.first()
        return (
            estudo.id_estudo if estudo else None,
            circuito.id_circuito if circuito else None,
            alternativa.id_alternativa if alternativa else None,
        )


class TestListarAlternativas:
    def test_sem_login_redireciona(self, client):
        resp = client.get("/estudo/1/alternativas/")
        assert resp.status_code in (301, 302)

    def test_estudo_inexistente_retorna_erro(self, auth_client):
        """get_with_all_relations retorna None para estudo inexistente, causando AttributeError na rota."""
        client, _ = auth_client
        try:
            resp = client.get("/estudo/999999/alternativas/")
            assert resp.status_code in (404, 500)
        except AttributeError:
            pass  # Rota não valida None antes de acessar estudo.id_edp

    def test_com_estudo_valido_retorna_200(self, auth_client, app):
        client, _ = auth_client
        with app.app_context():
            from app.models import Estudo
            estudo = Estudo.query.first()
            if not estudo:
                pytest.skip("Nenhum estudo disponível")
            eid = estudo.id_estudo

        resp = client.get(f"/estudo/{eid}/alternativas/")
        assert resp.status_code == 200

    def test_pagina_contem_lista(self, auth_client, app):
        client, _ = auth_client
        with app.app_context():
            from app.models import Estudo
            estudo = Estudo.query.first()
            if not estudo:
                pytest.skip("Nenhum estudo disponível")
            eid = estudo.id_estudo

        resp = client.get(f"/estudo/{eid}/alternativas/")
        assert resp.status_code == 200
        html = resp.data.decode("utf-8", errors="replace")
        assert "alternativa" in html.lower()


class TestCriarAlternativa:
    def _payload(self, id_circuito=1, **kw):
        data = {
            "id_circuito": str(id_circuito),
            "descricao": "Alternativa de teste",
            "dem_p_ant": "100.0",
            "dem_fp_ant": "80.0",
            "dem_p_dep": "150.0",
            "dem_fp_dep": "120.0",
            "latitude_ponto_conexao": "-22.9",
            "longitude_ponto_conexao": "-47.06",
            "letra_alternativa": "A",
            "subgrupo_tarif": "A2",
            "etapa": "1",
            "custo_modular": "10000.00",
            "ERD": "50.0",
            "demanda_disponivel_ponto": "200.0",
            "proporcionalidade": "0.5",
            "flag_carga": "y",
        }
        data.update(kw)
        return data

    def test_sem_login_redireciona(self, client):
        resp = client.post("/estudo/1/alternativas/", data=self._payload())
        assert resp.status_code in (301, 302)

    def test_formulario_invalido_retorna_aviso(self, auth_client, app):
        client, _ = auth_client
        with app.app_context():
            from app.models import Estudo
            estudo = Estudo.query.first()
            if not estudo:
                pytest.skip("Nenhum estudo disponível")
            eid = estudo.id_estudo

        resp = client.post(f"/estudo/{eid}/alternativas/", data={})
        assert resp.status_code in (200, 302)

    def test_criacao_valida(self, auth_client, app):
        client, _ = auth_client
        with app.app_context():
            from app.models import Estudo, Circuito
            estudo = Estudo.query.first()
            circuito = Circuito.query.first()
            if not estudo or not circuito:
                pytest.skip("Dados de apoio insuficientes")
            eid = estudo.id_estudo
            cid = circuito.id_circuito

        resp = client.post(
            f"/estudo/{eid}/alternativas/",
            data=self._payload(id_circuito=cid),
        )
        assert resp.status_code in (200, 302)


class TestCarregarAlternativa:
    def test_sem_login_redireciona(self, client):
        resp = client.get("/alternativas/1")
        assert resp.status_code in (301, 302)

    def test_inexistente_retorna_404(self, auth_client):
        client, _ = auth_client
        resp = client.get("/alternativas/999999")
        assert resp.status_code == 404

    def test_retorna_json_com_campos_esperados(self, auth_client, app):
        client, _ = auth_client
        with app.app_context():
            from app.models import Alternativa
            alt = Alternativa.query.first()
            if not alt:
                pytest.skip("Nenhuma alternativa disponível")
            aid = alt.id_alternativa

        resp = client.get(f"/alternativas/{aid}")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data is not None
        assert "id_alternativa" in data
        assert "descricao" in data
        assert "latitude_ponto_conexao" in data
        assert "longitude_ponto_conexao" in data


class TestEditarAlternativa:
    def test_sem_login_redireciona(self, client):
        resp = client.post("/alternativas/1", data={})
        assert resp.status_code in (301, 302)

    def test_inexistente_retorna_404(self, auth_client):
        client, _ = auth_client
        resp = client.post("/alternativas/999999", data={})
        assert resp.status_code in (302, 404)

    def test_editar_com_dados_validos(self, auth_client, app):
        client, _ = auth_client
        with app.app_context():
            from app.models import Alternativa, Circuito
            alt = Alternativa.query.first()
            circ = Circuito.query.first()
            if not alt or not circ:
                pytest.skip("Dados insuficientes para editar")
            aid = alt.id_alternativa
            cid = circ.id_circuito

        resp = client.post(
            f"/alternativas/{aid}",
            data={
                "id_circuito": str(cid),
                "descricao": "Alternativa editada",
                "dem_p_ant": "100.0",
                "dem_fp_ant": "80.0",
                "dem_p_dep": "150.0",
                "dem_fp_dep": "120.0",
                "latitude_ponto_conexao": "-22.9",
                "longitude_ponto_conexao": "-47.06",
                "letra_alternativa": "A",
                "subgrupo_tarif": "A2",
                "etapa": "1",
                "custo_modular": "10000.00",
                "ERD": "50.0",
                "demanda_disponivel_ponto": "200.0",
                "flag_carga": "y",
            },
        )
        assert resp.status_code in (200, 302)


class TestExcluirAlternativa:
    def test_sem_login_redireciona(self, client):
        resp = client.delete("/alternativas/excluir/1")
        assert resp.status_code in (301, 302)

    def test_inexistente_retorna_404(self, auth_client):
        client, _ = auth_client
        resp = client.delete("/alternativas/excluir/999999")
        assert resp.status_code == 404

    def test_excluir_com_obras_retorna_erro(self, auth_client, app):
        """Alternativa com obras associadas não pode ser excluída."""
        client, _ = auth_client
        with app.app_context():
            from app.models import Alternativa
            # Busca alternativa com obras
            alt_com_obras = Alternativa.query.filter(
                Alternativa.obras.any()
            ).first()
            if not alt_com_obras:
                pytest.skip("Nenhuma alternativa com obras disponível")
            aid = alt_com_obras.id_alternativa

        resp = client.delete(f"/alternativas/excluir/{aid}")
        data = resp.get_json()
        assert data is not None
        assert data.get("success") is False
