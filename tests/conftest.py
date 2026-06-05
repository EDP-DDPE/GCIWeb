"""
Configuração global de testes para GCIWeb.

Estratégia:
- SQLite in-memory substitui o SQL Server (sem driver ODBC necessário)
- Schema 'gciweb' é removido via interceptor de SQL para compatibilidade SQLite
- Autenticação Microsoft é bypassada via mock de get_usuario_logado
- Flask-Session é substituída pela sessão cookie padrão do Flask
"""

import os
import pytest
from decimal import Decimal
from datetime import date
from unittest.mock import MagicMock, patch

# Variáveis de ambiente ANTES de qualquer import da app
os.environ.setdefault("FLASK_SECRET", "test-gciweb-secret-key-pytest")
os.environ.setdefault("CLIENT_ID", "test-client-id")
os.environ.setdefault("CLIENT_SECRET", "test-client-secret")
os.environ.setdefault("TENANT_ID", "test-tenant-id")
os.environ.setdefault("REDIRECT_URI", "http://localhost/auth/callback")
os.environ.setdefault("REDIRECT_PATH", "auth/callback")
os.environ.setdefault("HOST", "localhost")

_SQLITE_CFG = {
    "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    "SQLALCHEMY_ECHO": False,
    "SQLALCHEMY_ENGINE_OPTIONS": {},
}

# SQLite não suporta auto-increment em BIGINT — precisa compilar como INTEGER
# para que PRIMARY KEY BIGINT se comporte como rowid auto-increment.
from sqlalchemy.types import BigInteger
from sqlalchemy.ext.compiler import compiles

@compiles(BigInteger, "sqlite")
def _compile_bigint_sqlite(element, compiler, **kw):
    return "INTEGER"


# ---------------------------------------------------------------------------
# App fixture (escopo session: criada uma vez para todos os testes)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def app():
    with (
        patch("app.database.DatabaseConfig.get_sqlalchemy_config", return_value=_SQLITE_CFG),
        patch("app.database.DatabaseManager._setup_engine_events"),
        patch("app.main.Session"),  # substitui Flask-Session pela sessão cookie
    ):
        from app.main import create_app
        flask_app = create_app()

    flask_app.config.update({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test-gciweb-secret-key-pytest",
        "SERVER_NAME": None,
    })

    from app.models import db
    from sqlalchemy import event as sa_event

    # g é app-scoped no Flask 2.x — persiste entre requests no mesmo app context de
    # escopo session. teardown_request limpa o cache APÓS cada request para que o
    # próximo request (possivelmente de outro teste) não herde valores obsoletos.
    from flask import g as flask_g

    @flask_app.teardown_request
    def _clear_user_cache_after_request(error=None):
        """Remove g._cached_user ao final de cada request para evitar vazamento de estado."""
        try:
            del flask_g._cached_user
        except AttributeError:
            pass

    with flask_app.app_context():
        # Registra interceptor DENTRO do contexto, onde db.engine está disponível
        @sa_event.listens_for(db.engine, "before_cursor_execute", retval=True)
        def _strip_schema(conn, cursor, statement, params, context, executemany):
            """Remove prefixo de schema para compatibilidade SQLite."""
            statement = (
                statement
                .replace('"gciweb".', "")
                .replace("[gciweb].", "")
                .replace("gciweb.", "")
            )
            return statement, params

        db.create_all()
        _seed(db)
        yield flask_app
        db.drop_all()


def _seed(db):
    """Dados mínimos de apoio para os testes."""
    from app.models import (
        EDP, Regional, Municipio, Empresa, Tensao,
        TipoSolicitacao, StatusTipo, Subestacao, Circuito,
        FatorK, Usuario, RespRegiao,
    )

    edp = EDP(empresa="SP")
    db.session.add(edp)
    db.session.flush()

    regional = Regional(regional="Campinas", id_edp=edp.id_edp)
    db.session.add(regional)
    db.session.flush()

    municipio = Municipio(municipio="Campinas", id_edp=edp.id_edp, id_regional=regional.id_regional)
    db.session.add(municipio)
    db.session.flush()

    empresa = Empresa(nome_empresa="Empresa Teste SA", cnpj="00000000000191")
    db.session.add(empresa)
    db.session.flush()

    tensao = Tensao(tensao="AT")
    db.session.add(tensao)
    db.session.flush()

    tipo_sol = TipoSolicitacao(viabilidade="EV", analise="Técnica", pedido="Novo")
    db.session.add(tipo_sol)
    db.session.flush()

    status_tipo = StatusTipo(status="Em Análise", ativo=True)
    db.session.add(status_tipo)
    db.session.flush()

    subestacao = Subestacao(
        nome="SE Campinas",
        sigla="SEC",
        id_edp=edp.id_edp,
        id_municipio=municipio.id_municipio,
    )
    db.session.add(subestacao)
    db.session.flush()

    circuito = Circuito(
        circuito="BRT01",
        id_edp=edp.id_edp,
        id_subestacao=subestacao.id_subestacao,
        tensao="AT",
    )
    db.session.add(circuito)
    db.session.flush()

    fator_k = FatorK(
        id_edp=edp.id_edp,
        subgrupo_tarif="A2",
        data_ref=date(2024, 1, 1),
        k=Decimal("1.5"),
    )
    db.session.add(fator_k)
    db.session.flush()

    usuario = Usuario(
        matricula="test01",
        nome="Test Admin",
        id_edp=edp.id_edp,
        admin=True,
        visualizar=True,
        criar=True,
        editar=True,
        deletar=True,
        aprovar=True,
        bloqueado=False,
    )
    db.session.add(usuario)
    db.session.flush()

    resp_regiao = RespRegiao(
        id_regional=regional.id_regional,
        id_usuario=usuario.id_usuario,
        ano_ref=2024,
    )
    db.session.add(resp_regiao)

    db.session.commit()


# ---------------------------------------------------------------------------
# Fixtures reutilizáveis
# ---------------------------------------------------------------------------

@pytest.fixture
def client(app):
    return app.test_client()


def _make_user(**kw):
    """Cria um mock de Usuario para injetar em g.user."""
    u = MagicMock()
    u.id_usuario = kw.get("id_usuario", 1)
    u.matricula = kw.get("matricula", "test01")
    u.nome = kw.get("nome", "Test Admin")
    u.admin = kw.get("admin", True)
    u.bloqueado = False
    u.visualizar = True
    u.criar = True
    u.editar = True
    u.deletar = True
    u.aprovar = True
    u.id_edp = kw.get("id_edp", 1)
    u.first_name = "Test"
    return u


@pytest.fixture
def mock_user():
    return _make_user()


@pytest.fixture
def auth_client(app, mock_user):
    """
    Retorna (client, user) com autenticação funcional.

    A função patcha get_usuario_logado no módulo main E também define
    g._cached_user para que chamadas diretas a get_usuario_logado() nos
    handlers de rota (from app.auth import get_usuario_logado) retornem
    o mock sem precisar acessar o banco.
    """
    with patch("app.main.get_usuario_logado", return_value=mock_user):
        c = app.test_client()
        with c.session_transaction() as sess:
            sess["user"] = {
                "preferred_username": "test01@edp.com",
                "name": "Test Admin",
            }
            sess["access_token"] = "fake-access-token-for-tests"
        yield c, mock_user


@pytest.fixture
def auth_client_no_perm(app):
    """Cliente autenticado mas sem permissões (para testar bloqueios)."""
    user = _make_user(admin=False)
    user.visualizar = False
    user.criar = False
    user.editar = False
    user.deletar = False

    with patch("app.main.get_usuario_logado", return_value=user):
        c = app.test_client()
        with c.session_transaction() as sess:
            sess["user"] = {"preferred_username": "noperm@edp.com", "name": "No Perm"}
        yield c, user


# ---------------------------------------------------------------------------
# Helpers para testes
# ---------------------------------------------------------------------------

def assert_redirect(response, location_fragment):
    """Verifica que a resposta é um redirect contendo o fragmento de URL."""
    assert response.status_code in (301, 302), (
        f"Esperado redirect, mas recebeu {response.status_code}"
    )
    location = response.headers.get("Location", "")
    assert location_fragment in location, (
        f"Redirect para '{location}' não contém '{location_fragment}'"
    )


def json_data(response):
    """Extrai JSON de uma resposta de teste."""
    return response.get_json()
