from flask import Blueprint, render_template, request, jsonify
from sqlalchemy.orm import joinedload

from app.models import db, Usuario, EDP
from app.auth import requires_permission
from app.utils.activity_log import ler_logs, registrar_log

admin_bp = Blueprint(
    "admin",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path='/admin/static',
)

# Permissões booleanas editáveis no formulário de usuário.
PERMISSOES = ['admin', 'visualizar', 'criar', 'editar', 'deletar', 'aprovar']


def _to_bool(v):
    if isinstance(v, bool):
        return v
    return str(v).strip().lower() in ('1', 'true', 'on', 'yes', 'sim')


def _usuario_dict(u):
    return {
        'id_usuario': u.id_usuario,
        'matricula': u.matricula,
        'nome': u.nome,
        'email': u.email,
        'id_edp': u.id_edp,
        'admin': u.admin,
        'visualizar': u.visualizar,
        'criar': u.criar,
        'editar': u.editar,
        'deletar': u.deletar,
        'aprovar': u.aprovar,
        'bloqueado': u.bloqueado,
    }


@admin_bp.route("/admin/usuarios", methods=["GET"])
@requires_permission('admin')
def usuarios():
    """Página de administração: gestão de usuários + histórico de atividades."""
    lista = Usuario.query.options(joinedload(Usuario.edp)).order_by(Usuario.nome).all()
    edps = EDP.query.order_by(EDP.empresa).all()
    return render_template("admin/usuarios.html", usuarios=lista, edps=edps)


@admin_bp.route("/admin/usuarios/<int:id>/api", methods=["GET"])
@requires_permission('admin')
def get_usuario_api(id):
    u = Usuario.query.get_or_404(id)
    return jsonify(_usuario_dict(u))


@admin_bp.route("/admin/usuarios/adicionar", methods=["POST"])
@requires_permission('admin')
def adicionar_usuario():
    data = request.get_json() if request.is_json else request.form.to_dict()

    matricula = (data.get('matricula') or '').strip()
    nome = (data.get('nome') or '').strip()
    id_edp = data.get('id_edp')

    if not matricula or not nome or not id_edp:
        return jsonify({'status': 'error',
                        'message': 'Matrícula, nome e EDP são obrigatórios.'}), 400

    if Usuario.query.filter_by(matricula=matricula).first():
        return jsonify({'status': 'error',
                        'message': f'Já existe um usuário com a matrícula {matricula}.'}), 409

    try:
        novo = Usuario(
            matricula=matricula,
            nome=nome,
            email=(data.get('email') or '').strip() or None,
            id_edp=int(id_edp),
            admin=_to_bool(data.get('admin', False)),
            visualizar=_to_bool(data.get('visualizar', False)),
            criar=_to_bool(data.get('criar', False)),
            editar=_to_bool(data.get('editar', False)),
            deletar=_to_bool(data.get('deletar', False)),
            aprovar=_to_bool(data.get('aprovar', False)),
            bloqueado=_to_bool(data.get('bloqueado', False)),
        )
        db.session.add(novo)
        db.session.commit()
        registrar_log('criar_usuario', 'usuario', novo.id_usuario,
                      f'Criou o usuário {nome} ({matricula})')
        return jsonify({'status': 'success', 'message': 'Usuário criado com sucesso!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@admin_bp.route("/admin/usuarios/<int:id>/editar", methods=["POST"])
@requires_permission('admin')
def editar_usuario(id):
    u = Usuario.query.get_or_404(id)
    data = request.get_json() if request.is_json else request.form.to_dict()

    try:
        if data.get('nome'):
            u.nome = data['nome'].strip()
        if 'email' in data:
            u.email = (data.get('email') or '').strip() or None
        if data.get('id_edp'):
            u.id_edp = int(data['id_edp'])

        nova_matricula = (data.get('matricula') or '').strip()
        if nova_matricula and nova_matricula != u.matricula:
            if Usuario.query.filter_by(matricula=nova_matricula).first():
                return jsonify({'status': 'error',
                                'message': 'Matrícula já em uso por outro usuário.'}), 409
            u.matricula = nova_matricula

        for p in PERMISSOES + ['bloqueado']:
            if p in data:
                setattr(u, p, _to_bool(data[p]))

        db.session.commit()
        registrar_log('editar_usuario', 'usuario', u.id_usuario,
                      f'Editou o usuário {u.nome} ({u.matricula})')
        return jsonify({'status': 'success', 'message': 'Usuário atualizado com sucesso!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@admin_bp.route("/admin/logs/api", methods=["GET"])
@requires_permission('admin')
def logs_api():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    dias = request.args.get('dias', 7, type=int)
    matricula = request.args.get('matricula') or None
    acao = request.args.get('acao') or None
    busca = request.args.get('q') or None

    resultado = ler_logs(dias=dias, matricula=matricula, acao=acao,
                         busca=busca, page=page, per_page=per_page)
    return jsonify(resultado)
