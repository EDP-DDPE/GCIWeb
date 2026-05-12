from functools import wraps
from flask import redirect, url_for, flash, abort, g


def get_usuario_logado():
    return getattr(g, 'user', None)


def requires_permission(permission):

    def decorator(f):

        @wraps(f)
        def decorated_function(*args, **kwargs):

            usuario = get_usuario_logado()

            if not usuario:

                flash(
                    "Você não está autenticado.",
                    "danger"
                )

                return abort(403)

            if usuario.bloqueado:
                return abort(403)

            if usuario.admin:
                return f(*args, **kwargs)

            if not getattr(usuario, permission, False):

                flash(
                    "Você não tem autorização necessária.",
                    "danger"
                )

                return redirect(url_for("main.home"))

            return f(*args, **kwargs)

        return decorated_function

    return decorator