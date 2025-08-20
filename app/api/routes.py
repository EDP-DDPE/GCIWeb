from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from app.models import db, Estudo, get_dashboard_stats, EDP, listar_estudos, obter_estudo

api_bp = Blueprint("api", __name__)


@api_bp.route('/api/teste')
def teste():
    edp = Estudo.query.all()
    return jsonify(
        [{
            'nome': e.nome_projeto
        } for e in edp]
    )


@api_bp.route('/api/estudos')
def api_listar_estudos():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    return jsonify(listar_estudos(page, per_page))


@api_bp.route('/api/estudos/<int:estudo_id>')
def api_obter_estudo(estudo_id):
    return obter_estudo(estudo_id)


@api_bp.route('/api/dashboard/stats')
def dashboard_stats():
    """Estatísticas para o dashboard - queries otimizadas"""

    try:
        stats = get_dashboard_stats()

        return jsonify({
            'total_estudos': stats['total_estudos'],
            'estudos_por_regional': [
                {'regional': regional, 'total': total}
                for regional, total in stats['estudos_por_regional']
            ],
            'estudos_por_status': [
                {'status': status, 'total': total}
                for status, total in stats['estudos_por_status']
            ]
        })

    except Exception as e:
        return jsonify({
            'error': 'Erro ao obter estatísticas',
            'message': str(e)
        }), 500


@api_bp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Erro interno do servidor'}), 500


@api_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint não encontrado'}), 404
