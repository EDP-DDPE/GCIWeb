from flask import jsonify, request
from models.respregiao import RespRegiao

from datetime import datetime
from database import db

from models.estudo import Estudo
from models.anexo import Anexo

import os
from werkzeug.utils import secure_filename


class EstudoService:

    @staticmethod
    def criar_estudo(form, usuario, upload_folder_base):

        novo_estudo = Estudo(
            num_doc=form.num_doc.data,
            protocolo=int(form.protocolo.data) if form.protocolo.data else None,
            nome_projeto=form.nome_projeto.data,
            descricao=form.descricao.data,

            id_tensao=form.tensao.data,
            instalacao=int(form.instalacao.data) if form.instalacao.data else 0,

            n_alternativas=form.n_alternativas.data or 0,

            dem_carga_atual_fp=form.dem_carga_atual_fp.data or 0,
            dem_carga_atual_p=form.dem_carga_atual_p.data or 0,
            dem_carga_solicit_fp=form.dem_carga_solicit_fp.data or 0,
            dem_carga_solicit_p=form.dem_carga_solicit_p.data or 0,

            dem_ger_atual_fp=form.dem_ger_atual_fp.data or 0,
            dem_ger_atual_p=form.dem_ger_atual_p.data or 0,
            dem_ger_solicit_fp=form.dem_ger_solicit_fp.data or 0,
            dem_ger_solicit_p=form.dem_ger_solicit_p.data or 0,

            latitude_cliente=form.latitude_cliente.data,
            longitude_cliente=form.longitude_cliente.data,
            observacao=form.observacao.data,

            id_edp=form.edp.data,
            id_regional=form.regional.data,
            id_criado_por=usuario.id_usuario,
            id_resp_alteracao=usuario.id_usuario,
            id_resp_regiao=form.resp_regiao.data,
            id_empresa=form.id_empresa.data,
            id_municipio=form.municipio.data,
            id_tipo_solicitacao=form.tipo_pedido.data,

            data_registro=datetime.today(),
            data_abertura_cliente=form.data_abertura_cliente.data,
            data_desejada_cliente=form.data_desejada_cliente.data,
            data_vencimento_cliente=form.data_vencimento_cliente.data,
            data_prevista_conexao=form.data_prevista_conexao.data,
            data_vencimento_ddpe=form.data_vencimento_ddpe.data,

            tipo_geracao=form.tipo_geracao.data
        )

        db.session.add(novo_estudo)
        db.session.flush()

        EstudoService.processar_anexos(
            estudo=novo_estudo,
            arquivos=form.arquivos.data,
            upload_folder_base=upload_folder_base
        )

        db.session.commit()

        return novo_estudo

    @staticmethod
    def processar_anexos(estudo, arquivos, upload_folder_base):

        prefix = f"DDPE_{str(estudo.num_doc).replace('/', '_')}"

        upload_folder = os.path.join(upload_folder_base, prefix)

        os.makedirs(upload_folder, exist_ok=True)

        for file in arquivos:

            if not file:
                continue

            if prefix not in file.filename:
                new_name = f"{prefix}_{file.filename}"
            else:
                new_name = file.filename

            nome_arquivo = secure_filename(new_name)

            caminho_arquivo = os.path.join(upload_folder, nome_arquivo)

            file.save(caminho_arquivo)

            novo_anexo = Anexo(
                nome_arquivo=nome_arquivo,
                endereco=caminho_arquivo,
                tamanho_arquivo=os.path.getsize(caminho_arquivo),
                tipo_mime=file.content_type,
                id_estudo=estudo.id_estudo
            )

            db.session.add(novo_anexo)


def listar_estudos():
    """Lista estudos com paginação otimizada"""
    try:
        page = request.args.get('page', type=int)
        per_page = request.args.get('per_page', 100, type=int)

        # Query otimizada evitando N+1
        estudos_paginated = Estudo.query.options(
            db.joinedload(Estudo.regional),
            db.joinedload(Estudo.empresa),
            db.joinedload(Estudo.municipio),
            db.joinedload(Estudo.tipo_solicitacao),
            db.joinedload(Estudo.criado_por),
            db.joinedload(Estudo.resp_regiao).joinedload(RespRegiao.usuario),
            #db.selectinload(Estudo.ultimo_status).selectinload(StatusEstudo.status_tipo),

            db.selectinload(Estudo.alternativas),
            db.selectinload(Estudo.anexos)

        ).order_by(Estudo.id_estudo.desc()) \
            .paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        estudos_data = []
        for estudo in estudos_paginated.items:
           #print(estudo.ultimo_status.status_tipo.status) if estudo.ultimo_status else None

            estudos_data.append({
                'id': estudo.id_estudo,
                'num_doc': estudo.num_doc,
                'nome_projeto': estudo.nome_projeto,
                'regional': estudo.regional.regional if estudo.regional else None,
                'empresa': estudo.empresa.nome_empresa if estudo.empresa else None,
                'municipio': estudo.municipio.municipio if estudo.municipio else None,
                'tipo_solicitacao': estudo.tipo_solicitacao.viabilidade if estudo.tipo_solicitacao else None,
                'eng_responsavel': estudo.resp_regiao.usuario.nome if estudo.resp_regiao else None,
                'criado_por': estudo.criado_por.nome if estudo.criado_por else None,
                'status': estudo.ultimo_status.status_tipo.status if estudo.ultimo_status else "Status não cadastrado",
                'qtd_alternativas': len(estudo.alternativas),
                'qtd_anexos': len(estudo.anexos),
                'data_registro': estudo.data_registro.isoformat() if estudo.data_registro else None
            })

        return {
            'estudos': estudos_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': estudos_paginated.total,
                'pages': estudos_paginated.pages,
                'has_next': estudos_paginated.has_next,
                'has_prev': estudos_paginated.has_prev
            }
        }

    except Exception as e:
        return {
            'error': 'Erro ao listar estudos',
            'message': str(e)
        }, 500


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

            'dem_carga_atual_fp': float(estudo.dem_carga_atual_fp),
            'dem_carga_atual_p': float(estudo.dem_carga_atual_p),
            'dem_carga_solicit_fp': float(estudo.dem_carga_solicit_fp),
            'dem_carga_solicit_p': float(estudo.dem_carga_solicit_p),
            'dem_ger_atual_fp': float(estudo.dem_ger_atual_fp),
            'dem_ger_atual_p': float(estudo.dem_ger_atual_p),
            'dem_ger_solicit_fp': float(estudo.dem_ger_solicit_fp),
            'dem_ger_solicit_p': float(estudo.dem_ger_solicit_p),
            'latitude_cliente': float(estudo.latitude_cliente) if estudo.latitude_cliente else None,
            'longitude_cliente': float(estudo.longitude_cliente) if estudo.longitude_cliente else None,
            'observacao': estudo.observacao,
            'qtd_alternativas': len(estudo.alternativas),
            'qtd_anexos': len(estudo.anexos),
            'data_registro': estudo.data_registro.isoformat() if estudo.data_registro else None,

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

            'tipo_solicitacao': {
                'id': estudo.tipo_solicitacao.id_tipo_solicitacao,
                'viabilidade': estudo.tipo_solicitacao.viabilidade,
                'analise': estudo.tipo_solicitacao.analise,
                'pedido': estudo.tipo_solicitacao.pedido

            } if estudo.tipo_solicitacao else None,

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
                    'endereco': anexo.endereco,
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
                    'status': status.status_tipo.status if status.status_tipo else None,
                    'observacao': status.observacao,
                    'criado_por': status.criado_por.nome if status.criado_por else None
                }
                for status in estudo.status_estudos
            ],

            'alternativas': [
                {
                    'id': alt.id_alternativa,
                    'letra_alternativa': alt.letra_alternativa,
                    'descricao': alt.descricao,
                    'custo_modular': float(alt.custo_modular),
                    'flag_alternativa_escolhida': alt.flag_alternativa_escolhida,
                    'has_image': alt.blob_image is not None,
                    'circuito': {
                        'id': alt.circuito.id_circuito,
                        'nome': alt.circuito.circuito,
                        'tensao': alt.circuito.tensao,
                    } if alt.circuito else None
                }
                for alt in estudo.alternativas
            ]
        }

        return estudo_data

    except Exception as e:
        return {
            'error': 'Erro ao obter estudo',
            'message': str(e)
        }, 500