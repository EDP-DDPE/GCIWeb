from flask import Blueprint, render_template, request, jsonify, session, g, send_file
from app.auth import get_usuario_logado, requires_permission
from datetime import datetime
import json
import os
import uuid

from app.bot.atlas_agent import AtlasAgent
from app.bot.sql_schema import get_schema_from_sqlserver

bot_bp = Blueprint('bot', __name__,
                   template_folder='templates',
                   static_folder='static', static_url_path='/bot/static')

# Armazenamento temporário de conversas ativas (em produção, use Redis ou DB)
active_chats = {}

def ensure_chat_structure(chat_data):
    """
    Garante que o dicionário do chat tenha sempre as chaves esperadas.
    Isso deixa o sistema pronto para anexar tabelas e gráficos.
    """
    chat_data.setdefault('messages', [])
    chat_data.setdefault('tables', [])
    chat_data.setdefault('charts', [])
    return chat_data

@bot_bp.route('/atlas')
@requires_permission('visualizar')
def atlas():
    schema = get_schema_from_sqlserver()
    print(schema)

    return render_template('bot/chat.html')


# @bot_bp.route('/api/send_message', methods=['POST'])
# def send_message():
#     data = request.json
#     user_message = data.get('message', '')
#     chat_id = data.get('chat_id')
#
#     # Criar novo chat se não existir
#     if not chat_id:
#         chat_id = str(uuid.uuid4())
#         active_chats[chat_id] = ensure_chat_structure({
#             'id': chat_id,
#             'title': user_message[:50],  # Primeiras palavras como título
#             'date': datetime.now().isoformat(),
#             'messages': [],
#             'tables': [],
#             'charts': []
#         })
#
#     active_chats[chat_id] = ensure_chat_structure(active_chats.get(chat_id, {}))
#
#     # Adicionar mensagem do usuário
#     if chat_id in active_chats:
#         active_chats[chat_id]['messages'].append({
#             'text': user_message,
#             'role': 'user',
#             'timestamp': datetime.now().isoformat()
#         })
#
#     # Aqui você integraria seu modelo LLM
#     # Por enquanto, uma resposta simulada
#     bot_response = generate_bot_response(user_message)
#
#     # Adicionar resposta do bot
#     if chat_id in active_chats:
#         active_chats[chat_id]['messages'].append({
#             'text': bot_response,
#             'role': 'bot',
#             'timestamp': datetime.now().isoformat()
#         })
#
#     return jsonify({
#         'response': bot_response,
#         'chat_id': chat_id
#     })


@bot_bp.route('/api/save_chat', methods=['POST'])
def save_chat():
    data = request.json
    chat_id = data.get('chat_id')

    if not chat_id or chat_id not in active_chats:
        return jsonify({'error': 'Chat não encontrado'}), 404

    chat_data = active_chats[chat_id]
    chat_data = ensure_chat_structure(chat_data)

    chat_dir = g.user.chat_dir

    # Salvar em arquivo JSON

    filename = f"{chat_id}.json"

    if not os.path.exists(chat_dir):
        os.makedirs(chat_dir)

    filepath = os.path.join(chat_dir,  filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(chat_data, f, ensure_ascii=False, indent=2)

    return jsonify({
        'success': True,
        'file': filename
    })


@bot_bp.route('/api/chat_history', methods=['GET'])
def get_chat_history():
    chats = []
    chat_dir = g.user.chat_dir
    # Carregar todos os arquivos de chat salvos
    if os.path.exists(chat_dir):
        for filename in os.listdir(chat_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(chat_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        chat_data = json.load(f)
                        chat_data = ensure_chat_structure(chat_data)

                        chats.append({
                            'id': chat_data['id'],
                            'title': chat_data.get('title', 'Conversa'),
                            'date': chat_data.get('date'),
                            'message_count': len(chat_data['messages']),
                            'tables_count': len(chat_data['tables']),
                            'charts_count': len(chat_data['charts'])
                        })
                except Exception as e:
                    print(f"Erro ao carregar {filename}: {e}")

    # Ordenar por data (mais recentes primeiro)
    chats.sort(key=lambda x: x['date'], reverse=True)

    return jsonify({'chats': chats})


@bot_bp.route('/api/load_chat/<chat_id>', methods=['GET'])
def load_chat(chat_id):
    chat_dir = g.user.chat_dir
    # Tentar carregar do armazenamento ativo primeiro
    if chat_id in active_chats:
        return jsonify(active_chats[chat_id])

    # Caso contrário, carregar do arquivo
    filepath = os.path.join(chat_dir, f"{chat_id}.json")

    if not os.path.exists(filepath):
        return jsonify({'error': 'Chat não encontrado'}), 404

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            chat_data = json.load(f)
            chat_data = ensure_chat_structure(chat_data)
            # Recarregar no armazenamento ativo
            active_chats[chat_id] = chat_data
            print(chat_data)
            return jsonify(chat_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500




@bot_bp.route('/api/run_analysis', methods=['POST'])
def run_analysis():
    data = request.json
    chat_id = data.get('chat_id')
    params  = data.get('params', {})

    if not chat_id or chat_id not in active_chats:
        return jsonify({'error': 'Chat não encontrado'}), 404

    chat = ensure_chat_structure(active_chats[chat_id])

    # 1) Aqui você faz a consulta e monta um DataFrame df
    # df = sua_analise(params)

    # 2) Gera um ID único para a tabela
    table_id = f"table_{len(chat['tables']) + 1:03d}"
    table_name = "Resultado da análise de carga"

    chat_dir = g.user.chat_dir
    chat_folder = os.path.join(chat_dir, chat_id, "tables")
    os.makedirs(chat_folder, exist_ok=True)

    table_filename = f"{table_id}.parquet"
    table_path = os.path.join(chat_folder, table_filename)

    # Salvar DataFrame como parquet (quando você tiver o df)
    # df.to_parquet(table_path)

    # Registrar na estrutura do chat
    chat['tables'].append({
        'id': table_id,
        'name': table_name,
        'file': table_filename
    })

    # Adicionar uma mensagem do bot referenciando a tabela
    chat['messages'].append({
        'text': 'Segue abaixo a tabela com o resultado da análise.',
        'role': 'bot',
        'timestamp': datetime.now().isoformat(),
        'attachments': [
            {
                'type': 'table',
                'id': table_id,
                'name': table_name
            }
        ]
    })

    active_chats[chat_id] = chat

    return jsonify({'success': True})


@bot_bp.route('/api/delete_chat', methods=['POST'])
def delete_chat():
    data = request.json
    chat_id = data.get("chat_id")

    if not chat_id:
        return jsonify({"error": "Chat ID não enviado"}), 400

    chat_dir = g.user.chat_dir
    filepath = os.path.join(chat_dir, f"{chat_id}.json")

    # Remover da memória
    if chat_id in active_chats:
        del active_chats[chat_id]

    # Remover arquivo salvo
    if os.path.exists(filepath):
        os.remove(filepath)

    return jsonify({"success": True})


@bot_bp.route('/api/rename_chat', methods=['POST'])
def rename_chat():
    data = request.json
    chat_id = data.get("chat_id")
    new_title = data.get("title", "").strip()

    if not chat_id or not new_title:
        return jsonify({"error": "Dados inválidos"}), 400

    chat_dir = g.user.chat_dir
    filepath = os.path.join(chat_dir, f"{chat_id}.json")

    # Atualizar em memória
    if chat_id in active_chats:
        active_chats[chat_id]["title"] = new_title

    # Atualizar arquivo
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            chat_data = json.load(f)

        chat_data["title"] = new_title

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(chat_data, f, ensure_ascii=False, indent=2)

    return jsonify({"success": True})


# def generate_bot_response(user_message):
#     """
#     Integre aqui seu modelo LLM (OpenAI, Anthropic, etc.)
#     Exemplo com resposta simulada:
#     """
#     user = g.user
#
#     # Simulação simples
#     responses = {
#         'oi': f'Oi,  {user.first_name}!  Como posso ajudar você hoje?',
#         'olá': f'Oi, {user.first_name}! Em que posso ser útil?',
#         'ola': f'Oi, {user.first_name}! Em que posso ser útil?',
#         'como você está': 'Estou funcionando perfeitamente! E você?',
#         'como vai você?': 'Estou com os Bits em alta! E você?',
#         'obrigado': 'Por nada! Estou aqui para ajudar.',
#         'obrigado!': 'Por nada! Estou aqui para ajudar.',
#         'muito obrigado': 'Por nada! Estou aqui para ajudar.',
#         'muito obrigado!': 'Por nada! Estou aqui para ajudar.',
#         'bom dia': f'Bom dia {user.first_name}, o que você deseja fazer?',
#         'bom dia!': f'Bom dia {user.first_name}, o que você deseja fazer?',
#
#     }
#
#     message_lower = user_message.lower()
#
#     for key, response in responses.items():
#         if key in message_lower:
#             return response
#
#
#
#     # Resposta padrão
#     return f'Entendi sua mensagem: "{user_message}". Como posso ajudar com isso?'


AGENT = AtlasAgent(
    llm_url=os.getenv("LLM_URL"),
    llm_token=os.getenv("LLM_TOKEN"))

@bot_bp.route("/api/llm_query", methods=["POST"])
def llm_query():

    try:
        data = request.json
        prompt = data.get("prompt")
        chat_id = data.get("chat_id")

        schema_text = get_schema_from_sqlserver()

        if not prompt:
            return jsonify({"error": "Prompt não enviado"}), 400

        # ====================================================
        # 1) GARANTIR QUE O CHAT EXISTE
        # ====================================================
        if chat_id not in active_chats:
            chat_id = str(uuid.uuid4())
            active_chats[chat_id] = {
                "id": chat_id,
                "title": prompt[:50],
                "date": datetime.now().isoformat(),
                "messages": [],
                "tables": [],
                "charts": []
            }

        chat = active_chats[chat_id]

        # Adicionar a mensagem do usuário ao histórico
        chat["messages"].append({
            "text": prompt,
            "role": "user",
            "timestamp": datetime.now().isoformat(),
            "chat_id": chat_id
        })


        # ====================================================
        # 2) CLASSIFICAR INTENÇÃO
        # ====================================================
        clean_messages = [
            {
                "role": m["role"],
                "text": m["text"]
            }
            for m in chat["messages"]
        ]

        intent_obj = AGENT.classify_intent(prompt, clean_messages)
        intent = intent_obj["intent"]
        confidence = intent_obj.get("confidence", 0.80)

        print(f"[INTENT] {intent}  | conf: {confidence}")


        # ====================================================
        # 3) DECISÃO POR INTENT
        # ====================================================

        # ---------> Caso 1: Pergunta geral
        if intent in ["general_question", "tech_help"]:

            clean_messages = [
                {
                    "role": m["role"],
                    "text": m["text"]
                }
                for m in chat["messages"]
            ]

            bot_text = AGENT._call_llm({
                "messages": [
                    {"role": "system", "content": generate_prompt_especialist("Você é o assistente oficial do Atlas. O usuário fez uma pergunta genérica sobre qualquer assunto.", clean_messages, schema_text)},
                    {"role": "user", "content": prompt}
                ]
            })

            bot_message = {"text": bot_text, "role": "bot", "timestamp": datetime.now().isoformat(), "chat_id": chat_id}

            chat["messages"].append(bot_message)
            return jsonify(bot_message)


        # ---------> Caso 2: Pergunta sobre o sistema Atlas (sem SQL)
        if intent == "atlas_system_question":
            clean_messages = [
                {
                    "role": m["role"],
                    "text": m["text"]
                }
                for m in chat["messages"]
            ]

            bot_text = AGENT._call_llm({
                "messages": [
                    {"role": "system", "content": generate_prompt_especialist("Você é o assistente oficial do Atlas. Você é um especialista em rede elétrica, planejamento, estudos e obras da EDP.", clean_messages, schema_text)},
                    {"role": "user", "content": prompt}
                ]
            })

            bot_message = {"text": bot_text, "role": "bot", "timestamp": datetime.now().isoformat(), "chat_id": chat_id}

            chat["messages"].append(bot_message)
            return jsonify(bot_message)


        # ====================================================
        # 4) INTENTS RELACIONADOS A SQL
        # ====================================================
        if intent in ["sql_query", "sql_table", "sql_plot", "sql_count_summary"]:

            # ------------------------------------------------
            # 4.1 — obter schema do banco
            # ------------------------------------------------

            # ------------------------------------------------
            # 4.2 — gerar SQL com o agente
            # ------------------------------------------------
            clean_messages = [
                {
                    "role": m["role"],
                    "text": m["text"]
                }
                for m in chat["messages"]
            ]

            sql_json = AGENT.generate_sql(prompt, schema_text, clean_messages)
            sql_command = sql_json["sql"]
            sql_comment = sql_json["comment"]

            print(f"[SQL] {sql_command}")

            # ------------------------------------------------
            # 4.3 — executar SQL
            # ------------------------------------------------
            df = AGENT.run_sql(sql_command)

            # ====================================================
            # RESPOSTA PARA SQL COUNT (uma linha)
            # ====================================================
            if intent == "sql_count_summary":
                value = None
                if df.shape[1] == 1:
                    value = df.iloc[0, 0]
                else:
                    value = df.to_dict(orient="records")

                bot_message = {
                    "text": f"{sql_comment}\n\nResultado: {value}",
                    "role": "bot",
                    "sql": sql_command,
                    "timestamp": datetime.now().isoformat(),
                    "chat_id": chat_id
                }

                chat["messages"].append(bot_message)
                return jsonify(bot_message)


            # ====================================================
            # RESPOSTA TABELA
            # ====================================================
            if intent in ["sql_query", "sql_table"]:
                # 1. Conversão para CSV completo
                csv_filename = f"table_{uuid.uuid4().hex[:8]}.csv"

                chat_dir = g.user.chat_dir
                chat_folder = os.path.join(chat_dir, chat_id, "tables")
                os.makedirs(chat_folder, exist_ok=True)

                csv_path = os.path.join(chat_folder, csv_filename)
                df.to_csv(csv_path, index=False, sep=';', decimal=',', encoding='utf-8-sig')

                # 2. HTML com 20 primeiras linhas
                df_preview = df.head(20)
                html_table = df_preview.to_html(
                    index=False,
                    classes="atlas-table",
                    border=0,
                    justify="left"
                )

                # 3. Botão de download
                download_button = f"""
                    <button class='download-csv' onclick="downloadCSV('{csv_filename}', '{chat_id}')">
                        📥 Baixar CSV completo
                    </button>
                """

                bot_message = {
                    "text": sql_comment,
                    "html": html_table + download_button,
                    "sql": sql_command,
                    "role": "bot",
                    "timestamp": datetime.now().isoformat(),
                    "attachments": [
                        {
                            "type": "csv",
                            "file": csv_filename,
                            "path": csv_path,
                            "name": "CSV Completo da Tabela"
                        }
                    ],
                    "chat_id": chat_id
                }

                print(bot_message)

                chat["messages"].append(bot_message)
                return jsonify(bot_message)


            # ====================================================
            # RESPOSTA GRÁFICO
            # ====================================================
            if intent == "sql_plot":

                x, y = df.columns[:2]
                # fig_id = AGENT.create_plot(df, x, y, chat_id)
                #
                # rel_path = f"{g.user.matricula}/{chat_id}/charts/{fig_id}"
                # public_url = f"/api/chat_file/{rel_path}"

                labels = df[x].astype(str).tolist()
                values = df[y].tolist()

                chart_id = f"chart_{uuid.uuid4().hex[:8]}"

                html = f"""
                    <canvas id="{chart_id}" class="atlas-chart-js"></canvas>
                    <script>
                        window.renderChart_{chart_id} = {{
                            labels: {json.dumps(labels)},
                            dataset: {json.dumps(values)}
                        }};
                    </script>
                """

                # html = f"""
                #        <img src="{public_url}" class="atlas-chart" />
                #    """

                attachment = {
                    "type": "chartjs",  # novo tipo
                    "labels": labels,
                    "dataset": values,
                    "title": "Gráfico solicitado",
                }

                bot_message = {
                    "text": sql_comment,
                    "role": "bot",
                    "html": html,
                    "sql": sql_command,
                    "timestamp": datetime.now().isoformat(),
                    "attachments": [attachment],
                    "chat_id": chat_id
                }

                chat["messages"].append(bot_message)
                return jsonify(bot_message)


        # ====================================================
        # Caso não cay em nenhum fluxo acima
        # ====================================================
        bot_message = {
            "text": "Não consegui entender a solicitação. Pode reformular?",
            "role": "bot",
            "timestamp": datetime.now().isoformat(),
            "chat_id": chat_id

        }

        chat["messages"].append(bot_message)
        return jsonify(bot_message)

    except Exception as e:
        print("ERRO NO LLM_QUERY:", str(e))  # Log no servidor
        return jsonify({
            "text": "⚠️ Ocorreu um erro interno ao processar sua solicitação.",
            "role": "bot",
            "error": str(e)
        }), 500


@bot_bp.route("/api/chat_file/<path:filepath>")
def get_chat_file(filepath):
    # Caminho absoluto da pasta de chats
    base_dir = os.path.join(os.path.dirname(__file__), "chats")

    abs_path = os.path.normpath(os.path.join(base_dir, filepath))

    # Segurança: impede acessar arquivos fora de /chats
    if not abs_path.startswith(base_dir):
        return "Acesso negado", 403

    if not os.path.exists(abs_path):
        return "Arquivo não encontrado", 404

    return send_file(abs_path)

@bot_bp.route("/api/download_csv/<chat_id>/<filename>", methods=["GET"])
def download_csv(chat_id, filename):
    base_dir = os.path.abspath(os.path.dirname(__file__))
    file_path = os.path.join(base_dir, 'chats', g.user.matricula, chat_id, "tables", filename)
    if not os.path.exists(file_path):
        return jsonify({"error": "Arquivo não encontrado"}), 404
    return send_file(
        file_path,
        mimetype="text/csv",
        as_attachment=True,
        download_name=filename
    )

def generate_prompt_especialist(type, hist, schema):
    prompt = f'''
        {type}
        
        O Atlas é o sistema de gerenciamento de estudos do Planejamento da Expansão da EDP. 
        Um estudo pode ser chamado de processo, anteprojeto, carta, documento. 
        Um estudo pode ter várias alternativas. 
        --------------------------------------
        REGRAS GERAIS (OBRIGATÓRIAS)
        --------------------------------------
        1. Retorne SEMPRE um texto. 
        2. SEMPRE utilize o histórico de conversa para entender o contexto da conversa.
        3. Nunca invente colunas, tabelas ou relacionamentos.
        4. Utilize SOMENTE o schema oficial abaixo para demonstrar conhecimento sobre a base de dados.
        5. Seu nome é Atlas GPT, alguns pode te chamar de CHATlas também em tom de piada.
        6. Seja engraçado, conte piadas quando fizer sentido no contexto.

        --------------------------------------
        SCHEMA OFICIAL DO ATLAS
        --------------------------------------
        {schema}
        
        --------------------------------------
        DADOS DO USUÁRIO:
        --------------------------------------
        Você esta falando com o {g.user.first_name}
        matrícula: {g.user.matricula}
        id_usuario: {g.user.id_usuario}
        nome inteiro: {g.user.nome}
        
        --------------------------------------
        HISTÓRICO DA CONVERSA:
        --------------------------------------
        Talvez esta não seja a primeira conversa com o usuário, sempre utilize esse histórico de conversa com ele:
        {json.dumps(hist, ensure_ascii=False, indent=2)}
        
         --------------------------------------
        O USUÁRIO PERGUNTOU:
        --------------------------------------
    '''
    return prompt