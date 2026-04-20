from flask import Blueprint, render_template, request, jsonify, send_file, current_app, flash, abort
from app.models import db, TipoSolicitacao, DocPadronizado
from werkzeug.utils import safe_join
from app.auth import requires_permission, get_usuario_logado
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import os
import shutil

tipo_solicitacao_bp = Blueprint("tipo_solicitacao", __name__, template_folder="templates", static_folder="static", static_url_path='/tipo_solicitacao/static')

@tipo_solicitacao_bp.route("/tipo_solicitacao", methods=["GET", "POST"])
@requires_permission('visualizar')
def listar():
    registros = TipoSolicitacao.query.all()
    usuario = get_usuario_logado()

    ids = [r.id_tipo_solicitacao for r in registros]
    docs = DocPadronizado.query.filter(
        DocPadronizado.id_tipo_solicitacao.in_(ids)
    ).all()

    doc_map = {d.id_tipo_solicitacao: d for d in docs}

    hoje = datetime.now()
    status_map = {}

    for r in registros:
        doc = doc_map.get(r.id_tipo_solicitacao)
        if not doc:
            status_map[r.id_tipo_solicitacao] = {
                'classe': 'secondary',
                'icone': 'bi-file-earmark-x',
                'texto': 'Sem documento',
                'dias': None
            }
        else:
            data_ref = doc.data_atualizacao or doc.data_criacao
            if data_ref:
                data_limite = data_ref.replace(
                    month=data_ref.month + 6 if data_ref.month <= 6 else data_ref.month - 6,
                    year=data_ref.year if data_ref.month <= 6 else data_ref.year + 1
                )
                # forma mais segura com timedelta equivalente a ~6 meses
                from dateutil.relativedelta import relativedelta
                data_limite = data_ref + relativedelta(months=6)
                diff_dias = (data_limite - hoje).days

                if diff_dias < 0:
                    status_map[r.id_tipo_solicitacao] = {
                        'classe': 'danger',
                        'icone': 'bi-exclamation-triangle-fill',
                        'texto': f'Vencido há {abs(diff_dias)}d',
                        'dias': diff_dias,
                        'data_limite': data_limite.strftime('%d/%m/%Y')
                    }
                elif diff_dias <= 30:
                    status_map[r.id_tipo_solicitacao] = {
                        'classe': 'warning',
                        'icone': 'bi-clock-fill',
                        'texto': f'Vence em {diff_dias}d',
                        'dias': diff_dias,
                        'data_limite': data_limite.strftime('%d/%m/%Y')
                    }
                else:
                    status_map[r.id_tipo_solicitacao] = {
                        'classe': 'success',
                        'icone': 'bi-check-circle-fill',
                        'texto': f'OK até {data_limite.strftime("%d/%m/%Y")}',
                        'dias': diff_dias,
                        'data_limite': data_limite.strftime('%d/%m/%Y')
                    }
            else:
                status_map[r.id_tipo_solicitacao] = {
                    'classe': 'secondary',
                    'icone': 'bi-file-earmark-x',
                    'texto': 'Sem documento',
                    'dias': None
                }

    return render_template(
        "listar_tipo_solicitacao.html",
        documentos=registros,
        usuario=usuario,
        status_map=status_map
    )


@tipo_solicitacao_bp.route('/tipo_solicitacao/<int:id>/editar', methods=['POST'])
@requires_permission('editar')
def editar_circuito(id):
    tipo_solicitacao = TipoSolicitacao.query.get_or_404(id)
    
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()
    
    for campo in data:
        if hasattr(tipo_solicitacao, campo):
            setattr(tipo_solicitacao, campo, data[campo])
    
    try:
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Tipo atualizado com sucesso!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@tipo_solicitacao_bp.route('/tipo_solicitacao/<int:id>/api', methods=['GET'])
def get_tipo_solicitacao_api(id):
    tipo_solicitacao = TipoSolicitacao.query.get_or_404(id)

    fluxoReverso = request.args.get('fluxo_reverso', 0, type=int)

    doc = db.session.query(DocPadronizado).filter_by(id_tipo_solicitacao=id,fluxo_reverso=fluxoReverso).order_by(DocPadronizado.versao.desc()).first()
    doc_info = None
    if doc:
        total_versoes = doc.versao
        doc_info = {
            'id': doc.id_doc_padronizado,
            'nome_doc': doc.nome_doc,
            'tipo_doc': doc.tipo_doc,
            'data_criacao': doc.data_criacao.strftime('%d/%m/%Y %H:%M') if doc.data_criacao else None,
            'data_atualizacao': doc.data_atualizacao.strftime('%d/%m/%Y %H:%M') if doc.data_atualizacao else None,
            'versao': doc.versao,
            'fluxo_reverso': doc.fluxo_reverso,
            'total_versoes': total_versoes
        }

    return jsonify({
        'id': tipo_solicitacao.id_tipo_solicitacao,
        'viabilidade': tipo_solicitacao.viabilidade,
        'analise': tipo_solicitacao.analise,
        'pedido': tipo_solicitacao.pedido,
        'viabilidade_abrev': tipo_solicitacao.viabilidade_abrev,
        'analise_abrev': tipo_solicitacao.analise_abrev,
        'pedido_abrev': tipo_solicitacao.pedido_abrev,
        'doc_padronizado': doc_info
    })


@tipo_solicitacao_bp.route('/tipo_solicitacao/<int:id>/excluir', methods=['POST'])
@requires_permission('excluir')
def excluir_circuito(id):
    tipo_solicitacao = TipoSolicitacao.query.get_or_404(id)
    
    if not tipo_solicitacao.estudos:
        try:
            db.session.delete(tipo_solicitacao)
            db.session.commit()
            return jsonify({'status': 'success', 'message': 'Tipo excluído com sucesso!'})
        except IntegrityError as e:
            db.session.rollback()
            error_message = str(e.orig)
            return jsonify({'status': 'error', 'message': error_message}), 409
        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': 'Erro inesperado ao excluir o circuito.'}), 500
    else:
        return jsonify({
            'status': 'error', 
            'message': 'Não foi possível apagar, pois há um estudo com esse tipo de solicitação.'
        }), 400
    
@tipo_solicitacao_bp.route('/tipo_solicitacao/adicionar', methods=['POST'])
@requires_permission('criar')
def adicionar_circuito():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()
    
    campos_obrigatorios = ['viabilidade', 'analise', 'pedido']
    campos_faltantes = [campo for campo in campos_obrigatorios if not data.get(campo)]
    
    if campos_faltantes:
        return jsonify({
            'status': 'error',
            'message': f'Campos obrigatórios faltando: {", ".join(campos_faltantes)}'
        }), 400
    
    try:
        novo_tipo_solicitacao = TipoSolicitacao(
            viabilidade=data.get('viabilidade'),
            viabilidade_abrev=data.get('viabilidade_abrev'),
            analise=data.get('analise'),
            analise_abrev=data.get('analise_abrev'),
            pedido=data.get('pedido'),
            pedido_abrev=data.get('pedido_abrev')
        )
        db.session.add(novo_tipo_solicitacao)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Tipo de solicitação adicionado com sucesso!'})
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao adicionar tipo de solicitação: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
    

@tipo_solicitacao_bp.route('/tipo_solicitacao/<int:id>/documento/upload', methods=['POST'])
@requires_permission('editar')
def upload_documento_tipo(id):
    tipo_solicitacao = TipoSolicitacao.query.get_or_404(id)

    fluxoReverso = request.args.get('fluxo_reverso', 0, type=int)

    if 'arquivo' not in request.files:
        return jsonify({'status': 'error', 'message': 'Nenhum arquivo enviado.'}), 400

    arquivo = request.files['arquivo']
    if arquivo.filename == '':
        return jsonify({'status': 'error', 'message': 'Nome de arquivo inválido.'}), 400

    doc_mais_recente = db.session.query(DocPadronizado).filter_by(id_tipo_solicitacao=id,fluxo_reverso=fluxoReverso).order_by(DocPadronizado.versao.desc()).first()

    if doc_mais_recente:
        nova_versao = doc_mais_recente.versao + 1
        data_criacao = doc_mais_recente.data_criacao
    else:
        nova_versao = 1
        data_criacao = datetime.now()

    _, ext = os.path.splitext(arquivo.filename)
    ext = ext.lower()

    nome_arquivo = f"doc_{id}_{nova_versao}_{fluxoReverso}{ext}"

    template_folder = current_app.config['TEMPLATE_FOLDER']
    os.makedirs(template_folder, exist_ok=True)

    template_folder = os.path.join(template_folder,nome_arquivo)

    dir = os.path.join(os.path.dirname(os.path.dirname(current_app.root_path))).replace('\\', '/')

    caminho_arquivo = os.path.join(dir, template_folder)

    try:
        arquivo.save(caminho_arquivo)

        doc = DocPadronizado(
            nome_doc = arquivo.filename,
            caminho_doc = template_folder,
            tipo_doc = ext.lstrip('.'),
            data_criacao = data_criacao,
            data_atualizacao = datetime.now(),
            id_tipo_solicitacao = id,
            versao = nova_versao,
            fluxo_reverso = fluxoReverso
        )

        db.session.add(doc)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Documento enviado com sucesso.',
            'versao': nova_versao,
            'doc_id': doc.id_doc_padronizado
        })

    except Exception as e:
        db.session.rollback()
        print("Erro upload_documento_tipo:", e)
        return jsonify({'status': 'error', 'message': 'Erro ao salvar documento.'}), 500


@tipo_solicitacao_bp.route('/tipo_solicitacao/<int:id>/documento/download', methods=['GET'])
@requires_permission('visualizar')
def download_documento_atual(id):

    fluxoReverso = request.args.get('fluxo_reverso', 0, type=int)

    doc = db.session.query(DocPadronizado).filter_by(id_tipo_solicitacao=id,fluxo_reverso=fluxoReverso).order_by(DocPadronizado.versao.desc()).first()

    if not doc or not doc.caminho_doc:
        return jsonify({'status': 'error', 'message': 'Documento padrão não encontrado.'}), 404

    dir = os.path.join(os.path.dirname(os.path.dirname(current_app.root_path))).replace('\\', '/')

    safe_path = os.path.join(dir,doc.caminho_doc)

    return send_file(
        safe_path,
        as_attachment=True,
        download_name=doc.nome_doc
    )

@tipo_solicitacao_bp.route('/tipo_solicitacao/<int:id>/documento/versoes', methods=['GET'])
@requires_permission('visualizar')
def listar_versoes_documento(id):

    fluxoReverso = request.args.get('fluxo_reverso', 0, type=int)

    tipo_solicitacao = TipoSolicitacao.query.get_or_404(id)
    
    versoes = DocPadronizado.query.filter_by(id_tipo_solicitacao=id,fluxo_reverso=fluxoReverso).order_by(DocPadronizado.versao.desc()).all() # NOT FLUXO REVERSO

    if not versoes:
        return jsonify({'status': 'success', 'versoes': []})

    versoes_anteriores = versoes[1:]

    if not versoes_anteriores:
        return jsonify({'status': 'success', 'versoes': []})

    dados = [{
        'id': v.id_doc_padronizado,
        'versao': v.versao,
        'nome_doc': v.nome_doc,
        'data_atualizaocao': v.data_atualizacao.strftime('%d/%m/%Y %H:%M') if v.data_atualizacao else None
    } for v in versoes_anteriores]

    return jsonify({'status': 'success', 'versoes': dados})


@tipo_solicitacao_bp.route('/tipo_solicitacao/documento/versao/<int:id_versao>/download', methods=['GET'])
@requires_permission('visualizar')
def download_versao_documento(id_versao):

    versao = DocPadronizado.query.get_or_404(id_versao)

    if not versao.caminho_doc or not os.path.isfile(versao.caminho_doc):
        return jsonify({'status': 'error', 'message': 'Arquivo da versão não encontrado.'}), 404

    dir = os.path.join(os.path.dirname(os.path.dirname(current_app.root_path))).replace('\\', '/')

    safe_path = os.path.join(dir,versao.caminho_doc)

    return send_file(
        safe_path,
        as_attachment=True,
        download_name=versao.nome_doc
    )
