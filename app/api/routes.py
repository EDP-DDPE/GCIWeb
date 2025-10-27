from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash, Response
from app.models import db, Estudo, get_dashboard_stats, EDP, listar_estudos, obter_estudo, Municipio, TipoSolicitacao, \
    Regional, Circuito, RespRegiao, Usuario, Subestacao, Instalacao, Empresa, Socio, FatorK
import requests
import re
from datetime import datetime
from sqlalchemy import func, and_, literal_column

api_bp = Blueprint("api", __name__)


def convert_date(data_str: str) -> str:
    if data_str == '':
        return ''
    dt = datetime.strptime(data_str, "%d/%m/%Y")
    return dt.strftime("%Y-%m-%d")


def iso_para_sql_datetime(iso_str: str) -> str:
    if iso_str == '':
        return ''
    """
    Converte string ISO 8601 '2025-08-19T14:11:57.464Z' para
    formato SQL Server 'YYYY-MM-DD HH:MM:SS'
    """
    dt = datetime.strptime(iso_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def only_digits(s: str) -> str:
    """Remove tudo que não for número"""
    return re.sub(r'\D', '', s)


def get_cnpj(c: str) -> dict:
    """
    Consulta o CNPJ na API da ReceitaWS
    Retorna um dicionário (JSON).
    """
    cnpj = only_digits(c)
    url = f"https://www.receitaws.com.br/v1/cnpj/{cnpj}"

    response = requests.get(url, timeout=10)

    if response.status_code == 200:
        try:
            return response.json()
        except Exception as e:
            return {"erro": f"Falha ao converter JSON: {e}"}
    else:
        return {"erro": f"Falha na requisição: {response.status_code}"}



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
    try:
        cliente = Instalacao.query.filter(Instalacao.INSTALACAO.contains(instalacao)).first()
        return jsonify({
            'regiao': cliente.EMPRESA,
            'instalacao': cliente.INSTALACAO,
            'cnpj': cliente.CNPJ,
            #'CPF': cliente.CPF,
            'nivel_tensao': cliente.TIPO_CLIENTE,
            'carga': cliente.CARGA,
            'nome': cliente.NOME_PARCEIRO,
            'cep': cliente.CEP
        })
    except Exception as e:
        return Response(status=204)


@api_bp.route("/api/cliente/cnpj/<cnpj>")
def get_cliente_by_cnpj(cnpj):
    try:
        cliente = Instalacao.query.filter(Instalacao.CNPJ.contains(cnpj)).first()
        return jsonify({
            'regiao': cliente.EMPRESA,
            'instalacao': cliente.INSTALACAO,
            'cnpj': cliente.CNPJ,
            #'CPF': cliente.CPF,
            'nivel_tensao': cliente.TIPO_CLIENTE,
            'carga': cliente.CARGA,
            'nome': cliente.NOME_PARCEIRO,
            'cep': cliente.CEP
        })
    except Exception as e:
        return Response(status=204)


# @api_bp.route("/api/cliente/<cpf>")
# def get_cliente_by_cpf(cpf):
#     cliente = Instalacao.query.filter(Instalacao.CPF.contains(cpf)).first()
#     return jsonify({
#         'regiao': cliente.EMPRESA,
#         'instalacao': cliente.INSTALACAO,
#         'cnpj': cliente.CNPJ,
#         'CPF': cliente.CPF,
#         'nivel_tensao': cliente.TIPO_CLIENTE,
#         'carga': cliente.CARGA,
#         'nome': cliente.NOME_PARCEIRO,
#         'cep': cliente.CEP
#     })


@api_bp.route("/api/consulta/<cnpj>")
def cadastra_cnpj(cnpj):
    empresa = Empresa.query.filter(Empresa.cnpj.contains(cnpj)).first()
    if not empresa:
        try:
            data = get_cnpj(cnpj)
            nova_empresa = Empresa(
                nome_empresa=data['nome'],
                cnpj=only_digits(data['cnpj']),
                abertura=convert_date(data['abertura']),
                situacao=data['situacao'],
                tipo=data['tipo'],
                porte=data['porte'],
                natureza_juridica=data['natureza_juridica'],
                logradouro=data['logradouro'],
                numero=data['numero'],
                complemento=data['complemento'],
                municipio=data['municipio'],
                bairro=data['bairro'],
                uf=data['uf'],
                cep=only_digits(data['cep']),
                email=data['email'],
                telefone=data['telefone'],
                data_situacao=convert_date(data['data_situacao']),
                ultima_atualizacao=iso_para_sql_datetime(data['ultima_atualizacao']),
                status=data['status'],
                fantasia=data['fantasia'],
                efr=data['efr'],
                motivo_situacao=data['motivo_situacao'],
                situacao_especial=data['situacao_especial'],
                data_situacao_especial=convert_date(data['data_situacao_especial'])
            )
            db.session.add(nova_empresa)
            db.session.flush()

            for socio in data['qsa']:
                novo_socio = Socio(
                    nome=socio['nome'],
                    cargo=socio['qual'],
                    id_empresa=nova_empresa.id_empresa
                )
                db.session.add(novo_socio)
            db.session.commit()
            return jsonify({'id_empresa': nova_empresa.id_empresa, 'nome': data['nome']})
        except Exception as e:
            print(str(e))
            db.session.rollback()
            return jsonify({'id_empresa': -1})
    else:
        return jsonify({
            'id_empresa': empresa.id_empresa,
            'nome': empresa.nome_empresa
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
@api_bp.route("/api/municipios_by_regional/<int:id_regional>")
def get_municipios_by_regional(id_regional):
    municipios = Municipio.query.filter_by(id_regional=id_regional).all()
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
    return {'responsaveis': [{'id': r.id_resp_regiao, 'nome': f"{r.usuario.nome} ({r.ano_ref})"}
                             for r in responsaveis]}


@api_bp.route("/api/fator_k/<int:id_edp>/<subgrupo>/<data_ref>/<carga>")
def get_fator_k(id_edp, subgrupo, data_ref, carga):
    # Converte a string de data (YYYY-MM-DD)
    data_ref_dt = datetime.strptime(data_ref, "%Y-%m-%d")

    k = (
        FatorK.query.filter(
            and_(
                FatorK.id_edp == id_edp,
                FatorK.subgrupo_tarif == subgrupo,
                FatorK.data_ref <= data_ref_dt,
                func.DATEADD(literal_column("day"), 365, FatorK.data_ref) >= data_ref_dt,
            )
        )
        .order_by(FatorK.data_ref.desc())
        .first()
    )

    if not k:
        return jsonify({"k": 0})

    if carga == "1":
        return jsonify({"k": k.k})
    else:
        return jsonify({"k": k.kg})
