"""Rota que entrega ao Expansion 3D o ticket do usuário logado no Atlas.

Fluxo, todo por redirecionamento no navegador:

    Expansion  ->  GET /api/expansion/ticket?retorno=<url do Expansion>&auto=1
    Atlas      ->  redireciona para <retorno>?ticket=<assinado>   (logado)
                   ou para        <retorno>?ticket=nenhum         (sem sessão)

O parâmetro `retorno` é conferido contra EXPANSION_URL antes de qualquer redirecionamento,
para que a rota não possa ser usada para mandar o usuário (e o ticket) a um site de fora.
"""
import base64
import hashlib
import hmac
import json
import os
import time
from urllib.parse import urlencode, urlparse

from flask import Blueprint, current_app, redirect, request, session

from app.auth import get_usuario_logado

expansion_bp = Blueprint("expansion", __name__)


def _assinar(payload: dict, segredo: str) -> str:
    """Mesmo formato que o Expansion confere: corpo.assinatura, ambos em base64url."""
    corpo = base64.urlsafe_b64encode(
        json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()).decode().rstrip("=")
    mac = hmac.new(segredo.encode(), corpo.encode(), hashlib.sha256).digest()
    return f"{corpo}.{base64.urlsafe_b64encode(mac).decode().rstrip('=')}"


def _retorno_confiavel(retorno: str) -> bool:
    """Só aceita voltar para o endereço configurado do Expansion (mesmo host e porta)."""
    permitido = os.getenv("EXPANSION_URL", "").strip()
    if not retorno or not permitido:
        return False
    alvo, base = urlparse(retorno), urlparse(permitido)
    return bool(alvo.scheme in ("http", "https") and alvo.netloc and alvo.netloc == base.netloc)


def _voltar(retorno: str, **parametros):
    """Volta ao Expansion preservando a query que ele já tenha mandado no `retorno`."""
    separador = "&" if "?" in retorno else "?"
    return redirect(f"{retorno}{separador}{urlencode(parametros)}")


@expansion_bp.route("/api/expansion/ticket")
def ticket():
    retorno = request.args.get("retorno", "")
    auto = request.args.get("auto", "0")
    if not _retorno_confiavel(retorno):
        current_app.logger.warning("Expansion: retorno recusado (%s)", retorno[:120])
        return "Endereço de retorno não autorizado. Confira EXPANSION_URL no .env do Atlas.", 400

    segredo = os.getenv("EXPANSION_SECRET", "").strip()
    if not segredo:
        current_app.logger.error("Expansion: EXPANSION_SECRET não configurado no .env")
        return _voltar(retorno, ticket="nenhum", auto=auto)

    claims = session.get("user") or {}
    matricula = (claims.get("preferred_username") or "").split("@")[0]
    if not matricula:
        # ninguém logado aqui: o Expansion abre em modo Visualização
        return _voltar(retorno, ticket="nenhum", auto=auto)

    usuario = get_usuario_logado()
    if usuario is not None and getattr(usuario, "bloqueado", False):
        return _voltar(retorno, ticket="nenhum", auto=auto)

    payload = {
        "matricula": matricula,
        "nome": (getattr(usuario, "nome", None) or claims.get("name") or matricula),
        "email": (getattr(usuario, "email", None) or claims.get("preferred_username") or ""),
        "admin": bool(getattr(usuario, "admin", False)),
        "ts": int(time.time()),
    }
    return _voltar(retorno, ticket=_assinar(payload, segredo), auto=auto)
