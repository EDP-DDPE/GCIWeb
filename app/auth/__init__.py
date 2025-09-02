from functools import wraps
from flask import session, redirect, url_for, flash, abort
from app.models import Usuario, db


def get_usuario_logado():
    if 'user' not in session:
        return None

    # Pega a parte antes do @ no email do Azure
    matricula = session['user']['preferred_username'].split('@')[0]

    usuario = Usuario.query.filter_by(matricula=matricula).first()
    return usuario


def requires_permission(permission):
    """Decorator para checar permissões do usuário."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            usuario = get_usuario_logado()
            if not usuario:
                flash("Você precisa estar logado.", "danger")
                return redirect(url_for("auth.login"))

            # Se for admin, libera tudo
            if usuario.admin:
                return f(*args, **kwargs)

            if usuario.bloqueado:
                return abort(403)

            if not getattr(usuario, permission, False):
                return abort(403)

            return f(*args, **kwargs)
        return decorated_function
    return decorator