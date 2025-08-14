from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from app.models import db, Estudo, get_dashboard_stats

api_bp = Blueprint("api", __name__)

@api_bp.route('/api/estudos')
def listar_estudos():
    """Lista estudos com paginação otimizada"""

    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        # Query otimizada evitando N+1
        estudos_paginated = Estudo.query.options(
            db.joinedload(Estudo.regional),
            db.joinedload(Estudo.empresa),
            db.joinedload(Estudo.municipio),
            db.joinedload(Estudo.tipo_viabilidade),
            db.joinedload(Estudo.criado_por)
        ).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        estudos_data = []
        for estudo in estudos_paginated.items:
            estudos_data.append({
                'id': estudo.id_estudo,
                'num_doc': estudo.num_doc,
                'nome_projeto': estudo.nome_projeto,
                'regional': estudo.regional.regional if estudo.regional else None,
                'empresa': estudo.empresa.nome_empresa if estudo.empresa else None,
                'municipio': estudo.municipio.municipio if estudo.municipio else None,
                'tipo_viabilidade': estudo.tipo_viabilidade.descricao if estudo.tipo_viabilidade else None,
                'criado_por': estudo.criado_por.nome if estudo.criado_por else None,
                'data_criacao': estudo.data_criacao.isoformat() if estudo.data_criacao else None
            })

        return jsonify({
            'estudos': estudos_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': estudos_paginated.total,
                'pages': estudos_paginated.pages,
                'has_next': estudos_paginated.has_next,
                'has_prev': estudos_paginated.has_prev
            }
        })

    except Exception as e:
        return jsonify({
            'error': 'Erro ao listar estudos',
            'message': str(e)
        }), 500


@api_bp.route('/api/estudos/<int:estudo_id>')
def obter_estudo(estudo_id):
    """Obtém um estudo específico com todos os relacionamentos"""

    try:
        # Método otimizado que carrega tudo de uma vez
        estudo = Estudo.get_with_all_relations(estudo_id)

        if not estudo:
            return jsonify({'error': 'Estudo não encontrado'}), 404

        estudo_data = {
            'id': estudo.id_estudo,
            'num_doc': estudo.num_doc,
            'protocolo': estudo.protocolo,
            'nome_projeto': estudo.nome_projeto,
            'descricao': estudo.descricao,
            'dem_solicit_fp': float(estudo.dem_solicit_fp),
            'dem_solicit_p': float(estudo.dem_solicit_p),
            'latitude_cliente': float(estudo.latitude_cliente) if estudo.latitude_cliente else None,
            'longitude_cliente': float(estudo.longitude_cliente) if estudo.longitude_cliente else None,
            'observacao': estudo.observacao,
            'data_registro': estudo.data_registro.isoformat() if estudo.data_registro else None,
            'data_criacao': estudo.data_criacao.isoformat() if estudo.data_criacao else None,

            # Relacionamentos (já carregados, sem N+1)
            'regional': {
                'id': estudo.regional.id_regional,
                'nome': estudo.regional.regional
            } if estudo.regional else None,

            'empresa': {
                'id': estudo.empresa.id_empresa,
                'nome': estudo.empresa.nome_empresa,
                'cnpj': estudo.empresa.cnpj
            } if estudo.empresa else None,

            'municipio': {
                'id': estudo.municipio.id_municipio,
                'nome': estudo.municipio.municipio
            } if estudo.municipio else None,

            'tipo_viabilidade': {
                'id': estudo.tipo_viabilidade.id_tipo_viab,
                'descricao': estudo.tipo_viabilidade.descricao
            } if estudo.tipo_viabilidade else None,

            'criado_por': {
                'id': estudo.criado_por.id_usuario,
                'nome': estudo.criado_por.nome,
                'matricula': estudo.criado_por.matricula
            } if estudo.criado_por else None,

            'responsavel_regiao': {
                'id': estudo.resp_regiao.id_resp_regiao,
                'usuario': {
                    'id': estudo.resp_regiao.usuario.id_usuario,
                    'nome': estudo.resp_regiao.usuario.nome,
                    'matricula': estudo.resp_regiao.usuario.matricula
                }
            } if estudo.resp_regiao and estudo.resp_regiao.usuario else None,

            # Coleções (carregadas com selectinload)
            'anexos': [
                {
                    'id': anexo.id_anexo,
                    'nome_arquivo': anexo.nome_arquivo,
                    'tamanho_arquivo': anexo.tamanho_arquivo,
                    'tipo_mime': anexo.tipo_mime,
                    'data_upload': anexo.data_upload.isoformat() if anexo.data_upload else None
                }
                for anexo in estudo.anexos
            ],

            'status_historico': [
                {
                    'id': status.id_status,
                    'data': status.data.isoformat() if status.data else None,
                    'status': status.status,
                    'observacao': status.observacao,
                    'criado_por': status.criado_por.nome if status.criado_por else None
                }
                for status in estudo.status_estudos
            ],

            'alternativas': [
                {
                    'id': alt.id_alternativa,
                    'descricao': alt.descricao,
                    'custo_modular': float(alt.custo_modular),
                    'flag_alternativa_escolhida': alt.flag_alternativa_escolhida,
                    'circuito': {
                        'id': alt.circuito.id_circuito,
                        'nome': alt.circuito.circuito,
                        'tensao': alt.circuito.tensao
                    } if alt.circuito else None
                }
                for alt in estudo.alternativas
            ]
        }

        return jsonify(estudo_data)

    except Exception as e:
        return jsonify({
            'error': 'Erro ao obter estudo',
            'message': str(e)
        }), 500


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