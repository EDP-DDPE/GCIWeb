from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from app.models import db, Estudo, get_dashboard_stats, EDP, listar_estudos, obter_estudo, Municipio, TipoSolicitacao, \
    Regional, Circuito, RespRegiao, Usuario, Subestacao, Instalacao

api_bp = Blueprint("api", __name__)


@api_bp.route('/api/teste')
def teste():
    edp = Estudo.query.all()
    return jsonify(
        [{
            'nome': e.nome_projeto
        } for e in edp]
    )


# @api_bp.route('/api/municipios/<int:municipio_id>')
# def api_obter_municipio(municipio_id):
#     try:
#         # Método otimizado que carrega tudo de uma vez
#         municipio = Municipio.query.get_or_404(municipio_id)
#
#         if not municipio:
#             return jsonify({'error': 'Municipio não encontrado'}), 404
#
#         municipio_data = {
#             'id': municipio.id_municipio,
#             'nome': municipio.municipio,
#             'edp': municipio.id_edp
#
#         }
#
#         return jsonify(municipio_data)
#
#     except Exception as e:
#         return {
#             'error': 'Erro ao obter municipio',
#             'message': str(e)
#         }, 500


@api_bp.route('/api/estudos')
def api_listar_estudos():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    return jsonify(listar_estudos(page, per_page))


@api_bp.route('/api/estudos/<int:estudo_id>')
def api_obter_estudo(estudo_id):
    return obter_estudo(estudo_id)


@api_bp.route("/api/tipo_analises/<viabilidade>")
def get_analises(viabilidade):
    analises = (
        db.session.query(TipoSolicitacao.analise)
        .filter_by(viabilidade=viabilidade)
        .distinct()
        .order_by(TipoSolicitacao.analise)
        .all()
    )
    return jsonify([a[0] for a in analises])


@api_bp.route("/api/cliente/<instalacao>")
def get_cliente_by_instalacao(instalacao):
    cliente = Instalacao.query.filter(Instalacao.INSTALACAO.contains(instalacao)).first()
    return jsonify({
            'regiao': cliente.EMPRESA,
            'instalacao': cliente.INSTALACAO,
            'cnpj': cliente.CNPJ,
            'CPF': cliente.CPF,
            'nivel_tensao': cliente.TIPO_CLIENTE,
            'carga': cliente.CARGA,
            'nome': cliente.NOME_PARCEIRO,
            'cep': cliente.CEP
    })



@api_bp.route("/api/tipo_pedidos/<viabilidade>/<analise>")
def get_pedidos(viabilidade, analise):
    solicitacoes = (
        db.session.query(TipoSolicitacao.id_tipo_solicitacao, TipoSolicitacao.pedido)
        .filter_by(viabilidade=viabilidade, analise=analise)
        .order_by(TipoSolicitacao.pedido)
        .all()
    )
    return jsonify([{"id": s.id_tipo_solicitacao, "pedido": s.pedido} for s in solicitacoes])


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


# Rotas AJAX para filtros dinâmicos no forms Cadastrar
@api_bp.route("/api/municipios/<int:id_edp>")
def get_municipios_by_edp(id_edp):
    """API para buscar municípios por EDP"""
    municipios = Municipio.query.filter_by(id_edp=id_edp).all()
    return {'municipios': [{'id': m.id_municipio, 'nome': m.municipio} for m in municipios]}


@api_bp.route("/api/regionais/<int:id_edp>")
def get_regionais_by_edp(id_edp):
    """API para buscar regionais por EDP"""
    regionais = Regional.query.filter_by(id_edp=id_edp).all()
    return {'regionais': [{'id': r.id_regional, 'nome': r.regional} for r in regionais]}


@api_bp.route("/api/circuitos/<int:id_edp>")
def get_circuitos_by_edp(id_edp):
    """API para buscar circuitos por EDP"""
    circuitos = Circuito.query.filter_by(id_edp=id_edp).join(Subestacao).all()
    return {'circuitos': [{'id': c.id_circuito, 'nome': f"{c.circuito} - {c.subestacao.nome}"}
                          for c in circuitos]}


@api_bp.route("/api/resp_regioes/<int:id_regional>")
def get_resp_by_regional(id_regional):
    """API para buscar responsáveis por regional"""
    responsaveis = RespRegiao.query.filter_by(id_regional=id_regional).join(Usuario).all()
    return {'responsaveis': [{'id': r.id_resp_regiao, 'nome': r.usuario.nome}
                             for r in responsaveis]}
