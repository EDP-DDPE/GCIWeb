from functools import wraps
from flask import session, redirect, url_for, flash, abort
from flask_session.sqlalchemy import sqlalchemy

from app.models import Usuario, db


def get_usuario_logado():
    if 'user' not in session:
        return None

    try:

        # Pega a parte antes do @ no email do Azure
        matricula = session['user']['preferred_username'].split('@')[0]

        usuario = Usuario.query.filter_by(matricula=matricula).first()
    except Exception as e:
        print(f'Erro ao pegar usuario logado: {e}')
        flash(f'Erro ao pegar usuario logado: {e}')
        return None

    return usuario


def requires_permission(permission):
    """Decorator para checar permissões do usuário."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            usuario = get_usuario_logado()
            if not usuario:
                try:
                    flash(f"Você não tem autorizações. Não encontrei a matrícula {session['user']['preferred_username'].split('@')[0]} na base de dados.", "danger")
                    return redirect(url_for("auth.login"))
                except KeyError as e:
                    flash(
                        f"Você não esta logado.",
                        "danger")
                    return redirect(url_for("auth.public"))


            # Se for admin, libera tudo
            if usuario.admin:
                return f(*args, **kwargs)

            if usuario.bloqueado:
                return abort(403)

            if not getattr(usuario, permission, False):
                flash(
                    f"Você não tem a autorização necessária.",
                    "error")
                return redirect(url_for("main.home"))

            return f(*args, **kwargs)
        return decorated_function
    return decorator