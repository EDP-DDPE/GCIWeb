from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.models import db,Subestacao, Municipio, EDP, Circuito
from sqlalchemy.orm import joinedload
from sqlalchemy import asc, desc

#circuito_bp = Blueprint("circuitos", __name__, template_folder="templates", static_folder="static", static_url_path='/static')
circuito_bp = Blueprint("circuitos", __name__, template_folder="templates")

@circuito_bp.route("/circuitos")
def listar_circuitos():
    # Buscar todos os circuitos COM relacionamentos (evita N+1 queries)
    registros = Circuito.query.options(
        joinedload(Circuito.subestacao),
        joinedload(Circuito.edp)
    ).all()

    # Converter usando o método to_dict()
    itens_serializaveis = [circuito.to_dict() for circuito in registros]

    colunas = [
        {'value': 'id_circuito', 'nome': 'ID', 'visivel': True},
        {'value': 'circuito', 'nome': 'Circuito', 'visivel': True},
        {'value': 'tensao', 'nome': 'Tensão', 'visivel': True},
        {'value': 'edp.empresa', 'nome': 'EDP', 'visivel': True},
        {'value': 'subestacao.nome', 'nome': 'Subestação', 'visivel': True}
    ]

    # Definir as ações disponíveis para cada registro
    acoes = [
        {
            'type': 'view',
            'icon': 'bi bi-eye',
            'js_function': 'verDetalhes', # Chama a função JS verDetalhes(id)
            'tooltip': 'Ver detalhes'
        }
    ]

    return render_template(
        "listar_unificado.html",
        titulo="Lista de Circuitos",    # OBRIGATÓRIO
        #botao_novo -> OPCIONAL
        colunas = colunas,    # OBRIGATÓRIO
        itens = itens_serializaveis,
        acoes = acoes
    )

# # ✅ Rotas adicionais implementadas
# @circuito_bp.route("/circuitos/novo")
# def novo():
#     """Rota para criar novo circuito"""
#     # TODO: Implementar formulário de novo circuito
#     return render_template('form_circuito.html', titulo="Novo Circuito")

# @circuito_bp.route("/circuitos/editar/<int:id>")
# def editar(id):
#     """Rota para editar circuito"""
#     circuito = Circuito.query.get_or_404(id)
#     # TODO: Implementar formulário de edição
#     return render_template('form_circuito.html', 
#                          titulo="Editar Circuito", 
#                          circuito=circuito)

# @circuito_bp.route("/circuitos/excluir/<int:id>", methods=['GET', 'POST'])
# def excluir(id):
#     """Rota para excluir circuito"""
#     circuito = Circuito.query.get_or_404(id)
    
#     if request.method == 'POST':
#         try:
#             db.session.delete(circuito)
#             db.session.commit()
#             flash(f'Circuito "{circuito.circuito}" foi excluído com sucesso!', 'success')
#             return redirect(url_for('circuitos.listar_circuitos'))
#         except Exception as e:
#             db.session.rollback()
#             flash(f'Erro ao excluir circuito: {str(e)}', 'danger')
#             return redirect(url_for('circuitos.listar_circuitos'))
    
#     return render_template('confirmar_exclusao.html',
#                          titulo="Excluir Circuito",
#                          item=circuito,
#                          campo_nome="circuito",
#                          url_voltar=url_for('circuitos.listar_circuitos'))

# # ✅ OPCIONAL: Rota para filtros dinâmicos (AJAX)
# @circuito_bp.route("/circuitos/filtrar")
# def filtrar_circuitos():
#     """Rota para filtrar circuitos via AJAX"""
#     # Parâmetros de filtro
#     busca_global = request.args.get('busca', '')
#     filtro_edp = request.args.get('edp', '')
#     filtro_subestacao = request.args.get('subestacao', '')
    
#     # Query base com relacionamentos
#     query = Circuito.query.options(
#         joinedload(Circuito.subestacao),
#         joinedload(Circuito.edp)
#     )
    
#     # Aplicar filtros
#     if busca_global:
#         query = query.filter(
#             db.or_(
#                 Circuito.circuito.ilike(f'%{busca_global}%'),
#                 Circuito.tensao.ilike(f'%{busca_global}%')
#             )
#         )
    
#     if filtro_edp:
#         query = query.join(EDP).filter(EDP.empresa.ilike(f'%{filtro_edp}%'))
    
#     if filtro_subestacao:
#         query = query.join(Subestacao).filter(Subestacao.nome.ilike(f'%{filtro_subestacao}%'))
    
#     registros = query.all()
    
#     # Retornar JSON para AJAX (se necessário)
#     from flask import jsonify
#     return jsonify({
#         'total': len(registros),
#         'dados': [{
#             'id_circuito': c.id_circuito,
#             'circuito': c.circuito,
#             'tensao': c.tensao,
#             'edp': c.edp.empresa if c.edp else 'N/A',
#             'subestacao': c.subestacao.nome if c.subestacao else 'N/A'
#         } for c in registros]
#     })