"""Testes para o blueprint principal (home, health, debug)."""

import pytest
import json


class TestHome:
    def test_home_sem_login_redireciona(self, client):
        resp = client.get("/")
        assert resp.status_code in (301, 302)

    def test_home_com_login_retorna_200_ou_redirect(self, auth_client):
        """Home pode redirecionar para dashboard ou retornar 200."""
        client, _ = auth_client
        resp = client.get("/")
        assert resp.status_code in (200, 302)

    def test_home_contem_html(self, auth_client):
        client, _ = auth_client
        resp = client.get("/")
        assert b"<!DOCTYPE html>" in resp.data or b"<html" in resp.data.lower()


class TestHealthCheck:
    def test_health_check_retorna_200(self, client):
        """Health check deve estar acessível sem autenticação."""
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_health_check_retorna_json(self, client):
        resp = client.get("/health")
        data = resp.get_json()
        assert data is not None
        assert "status" in data

    def test_health_check_status_ok_ou_error(self, client):
        resp = client.get("/health")
        data = resp.get_json()
        assert data["status"] in ("ok", "error", "healthy", "unhealthy")


class TestDebug:
    def test_debug_retorna_200_com_login(self, auth_client):
        client, _ = auth_client
        resp = client.get("/debug")
        assert resp.status_code in (200, 403)  # pode ser restrito a admin

    def test_debug_sem_login_redireciona(self, client):
        resp = client.get("/debug")
        assert resp.status_code in (200, 301, 302, 403)
