import json
import re

import matplotlib
matplotlib.use("Agg")

import requests
import time
import matplotlib.pyplot as plt
import pandas as pd
import uuid
from flask import g
import os

from datetime import datetime
from sqlalchemy import text
from app.models import db


class AtlasAgent:

    def __init__(self, llm_url, llm_token):
        self.url = llm_url
        self.token = llm_token

    # ---------------------------
    # 1. Classificar intenção
    # ---------------------------
    def classify_intent(self, user_message, hist):

        system_prompt = f'''
        Você é o CLASSIFICADOR OFICIAL DE INTENÇÃO do Atlas. Seu nome é Atlas GPT, alguns pode te chamar de CHATlas também em tom de piada.
        
        Seu trabalho é identificar exatamente qual tipo de tarefa o usuário solicitou.
        
        O Atlas é o sistema de gerenciamento de estudos do Planejamento da Expansão da EDP. 
        Um estudo pode ser chamado de processo, anteprojeto, carta, documento. 
        Um estudo pode ter várias alternativas. 
        
        Você SEMPRE retorna apenas um JSON com:
        
        {{
          "intent": "<tipo>",
          "confidence": <número entre 0 e 1>,
          "reason": "<explicação curta>"
        }}
        
        -----------------------------------------
        LISTA OFICIAL DE INTENTS:
        -----------------------------------------
        1. general_question
           - Pergunta sobre qualquer assunto geral: história, cultura, ciência, explicações de conceitos.
           - Exemplos: “quem é Einstein?”, “explique o que é carga elétrica”.
        
        2. atlas_system_question
           - Perguntas sobre obras, estudos, alternativas, transformadores, circuitos, perdas, BDGD.
           - NÃO pede SQL diretamente.
           - Exemplos: “como funciona o status de um estudo?”, “como a EDP calcula perdas?”.
        
        3. sql_query
           - Quando o usuário pediu dados do banco que não seja uma tabela, lista, ou que utilize um group by.
           - Exemplos: “conte as alternativas do estudo 123”, “analise o estudo XXX”, "faça um resumo sobre as alternativas do estudo XXX".
        
        4. sql_table
           - Quando o usuário pede uma TABELA, uma LISTA ou alguma análise que agrupe por algum campo.
           - Exemplos: “mostre uma tabela com…”, “retorne uma tabela com…”, "conte quantos estudos por responsável", "liste todos estudos com custo acima de X mil".
        
        5. sql_plot
           - Quando o usuário pede GRÁFICO.
           - Exemplos: “faça um gráfico de barras da carga por dia”.
        
        6. sql_count_summary
           - Quando o usuário pede apenas uma contagem simples ou resumo.
           - Exemplos: “quantas alternativas existem?”, “qual o total de estudos em 2024?”.
        
        7. tech_help
           - Perguntas sobre programação: Python, SQL, HTML, CSS, R, Flask, Spark.
           - Exemplos: “como alterar meu CSS?”, “como fazer join no PySpark?”.
        
        8. pdf_query
           - Perguntas sobre o conteúdo de um arquivo PDF/Word anexado.
           - Exemplos: “o que diz o PDF que anexei?”, “resuma o PDF”.
        
        9. document_question
           - Perguntas sobre arquivos já carregados no chat (tabelas, gráficos, anexos).
           - Exemplos: “explique esse gráfico que você gerou”, “reescreva o texto do Word”.
        
        10. ambiguous
            - Usuário escreveu algo impossível de entender.
        
        11. blocked
            - Usuário pede algo proibido: deletar do banco, sobrescrever dados, dados sensíveis.
        
        -----------------------------------------
        REGRAS IMPORTANTES
        -----------------------------------------
        - SEMPRE retorne um JSON. Nunca texto solto.
        - Nunca invente informações. Classifique apenas pelo texto.
        - Use “confidence” realista entre 0.50 e 1.00.
        - Se o usuário pedir algo de SQL + gráfico → sql_plot.
        - Se pedir SQL + tabela → sql_table.
        - Se pedir contagem → sql_count_summary.
        - Se disser “analise o estudo 123” sem formato → sql_query.
        - Se pedir ajuda técnica → tech_help.
        - Se mencionar PDF ou “arquivo” → pdf_query.
        - Se mencionar anexos anteriores → document_question.
        
        -----------------------------------------
        EXEMPLOS:
        -----------------------------------------
        
        Usuário: “quantas alternativas o estudo 210 possui?”
        →
        {{
         "intent": "sql_count_summary",
         "confidence": 0.98,
         "reason": "usuário pede contagem do banco"
        }}
        
        Usuário: “faça um gráfico de barras da carga por alimentador”
        →
        {{
         "intent": "sql_plot",
         "confidence": 0.97,
         "reason": "usuário pede gráfico baseado em dados"
        }}
        
        Usuário: “explique o que é transformador abaixador”
        →
        {{
         "intent": "atlas_system_question",
         "confidence": 0.91,
         "reason": "pergunta técnica do setor elétrico"
        }}
        
        Usuário: “resuma o PDF que anexei”
        →
        {{
         "intent": "pdf_query",
         "confidence": 0.95,
         "reason": "usuário menciona arquivo PDF"
        }}
        
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
        Talvez esta não seja a primeira conversa com o usuário, SEMPRE utilize esse histórico de conversa com ele para entender o contexto:
        {json.dumps(hist, ensure_ascii=False, indent=2)}
        
        -----------------------------------------
        AGORA CLASSIFIQUE O TEXTO:
        -----------------------------------------

        '''
        body = {
            "messages": [
                {
                    "role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
            ]
        }

        response = self._call_llm(body)
        return json.loads(response)

    # ---------------------------
    # 2. Gerar SQL
    # ---------------------------
    def generate_sql(self, question, schema, hist):
        system_prompt = f"""
        Você é o Especialista Oficial de SQL do Atlas (sistema da EDP).

        Seu papel é transformar perguntas do usuário em SQL válido, seguro e otimizado.
        Nunca responda nada além de JSON. Nunca explique fora do JSON.
        
        O Atlas é o sistema de gerenciamento de estudos do Planejamento da Expansão da EDP. 
        Um estudo pode ser chamado de processo, carta, documento. 
        Um estudo pode ter várias alternativas. 

        --------------------------------------
        REGRAS GERAIS (OBRIGATÓRIAS)
        --------------------------------------
        1. Gere SEMPRE um JSON com os campos:
           {{
             "sql": "<string SQL>",
             "comment": "<NÃO explique o que você fez, responda em primeira pessoa, diretamente, tentando criar um entrosamento com o usuário>"
           }}

        2. A query SQL DEVE ser compatível com SQL Server.

        3. É PROIBIDO executar:
           - DELETE
           - UPDATE
           - INSERT
           - DROP
           - TRUNCATE
           - ALTER
           - CREATE TABLE
           Qualquer comando destrutivo.
           Caso o usuário peça isso, retorne no campo "sql" um SELECT seguro
           e explique no campo "comment" que operações destrutivas são proibidas.

        4. Nunca invente colunas, tabelas ou relacionamentos.
           Utilize SOMENTE o schema oficial abaixo.
           
        5. No comentário NUNCA cite a query, ou que você fez uma query, sempre seja sucinto na resposta respondendo diretamente que você atendeu o que o usuário pediu.

        --------------------------------------
        SCHEMA OFICIAL DO ATLAS
        --------------------------------------
        {schema}
        
        --------------------------------------
        EXPLICAÇÃO SOBRE O SCHEMA (BANCO DE DADOS)
        --------------------------------------
        - A tabela Estudo possui os registros principais.
        - A tabela Alternativas possui as alternativas de cada Estudo, a coluna custo_modular possui o custo da alternativa
        - Ignore a tabela Obras e Kits
        - Sempre dê preferencia para o responsável da região, e não por quem foi criado. 
        - A tabela resp_regioes possui o id_usuario do Engenheiro responsável por aquela região. 
        - A tabela tipo_solicitacao possui a classificação do Estudo, se o usuário pedir alguma query sobre Orçamento de Conexão ou Estimado, Plano de Obras, DAL ele está falando de viabilidade.
        - Caso seja de Carga, MMGD (também chamado de Geração, mas utilize MMGD), AutoProdutor, Produtor Independente, Anteprojeto, ANEEL, ONS ele esta falando da coluna analise, se falar sobre Ligação Nova, Aumento ou redução de Demanda, Linhas, redes e subestações esta falando da coluna pedido. 
        - SEMPRE deixe o nome das colunas que irá retornar ao usuário legível e compreensível, evite underlines e abreviações.
        - Para perguntas com datas dê preferência para utilizar data_registro. Utilize outra caso o usuário peça diretamente.
        - Nunca use colunas do tipo TEXT ou NTEXT em GROUP BY ou ORDER BY.
        - Se precisar agrupar ou ordenar por essas colunas, faça CAST para NVARCHAR(MAX).
        - Exemplos:
          CAST(coluna AS NVARCHAR(MAX))
        
        --------------------------------------
        REGRAS DE JOINS
        --------------------------------------
        Sempre use:
        - gciweb.estudos como 'e'
        - gciweb.alternativas como 'a'
        - gciweb.status_tipo como 'st'
        - gciweb.resp_regioes como 'rr'
        - gciweb.usuarios como 'usr'
        - gciweb.tipo_solicitacao como 'ts'

        Exemplos:
        JOIN gciweb.estudos e ON e.id_estudo = a.id_estudo
        JOIN gciweb.tipo_solicitacao ts ON ts.id_tipo_solicitacao = e.id_tipo_solicitacao
        JOIN gciweb.status_tipo st ON st.id_status = a.id_status
        JOIN gciweb.resp_regioes rr ON rr.id_resp_regiao = e.id_resp_regiao
        join gciweb.usuarios usr on usr.id_usuario = rr.id_usuario
        
        --------------------------------------
        QUANDO O USUÁRIO PEDIR GRÁFICO
        --------------------------------------
        Apenas e SEMPRE gere o SQL normal. No comentário diga que você irá criar o gráfico conforme pedido.
        ATENÇÃO - TODO SQL para gráfico só pode ter duas colunas, onde a última coluna são os dados numéricos.
        --------------------------------------
        FORMATO FINAL (OBRIGATÓRIO)
        --------------------------------------
        Retorne APENAS um JSON puro:
        {{
          "sql": "...",
          "comment": "..."
        }}
        Sem markdown. Sem explicações fora do JSON.
        
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
        Talvez esta não seja a primeira conversa com o usuário, utilize esse histórico de conversa com ele:
        {json.dumps(hist, ensure_ascii=False, indent=2)}
        
         --------------------------------------
        O USUÁRIO PERGUNTOU:
        --------------------------------------
        """

        body = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ]
        }

        response = self._call_llm(body)
        # Remove bordas de markdown, se houver
        clean = response.strip()
        clean = clean.replace("```json", "").replace("```", "").strip()

        # Se começar com "{\n" ou "{\r\n", o LLM devolveu JSON-STRING
        if clean.startswith("{\\n") or "\\n" in clean:
            # O modelo devolveu JSON com \n escapado. Transformamos só isso.
            clean = clean.replace("\\n", "\n").replace("\\t", "\t")

        # Agora corrige quebras de linha reais dentro das strings
        clean = re.sub(r'(?<!\\)\n', r' ', clean)
        return json.loads(clean)

    # ---------------------------
    # 3. Chamar LLM
    # ---------------------------
    def _call_llm(self, body, max_attempts=3):
        for attempt in range(max_attempts):
            try:
                r = requests.post(
                    self.url,
                    headers={
                        "Authorization": f"Bearer {self.token}",
                        "Content-Type": "application/json"
                    },
                    json=body,
                    timeout=20
                )
                r.raise_for_status()
                content = r.json()["choices"][0]["message"]["content"]
                content = content.replace("```json", "").replace("```", "").strip()
                return content

            except Exception as e:
                time.sleep(1)

        raise Exception("Falha ao chamar LLM")

    # ---------------------------
    # 4. Executar query SQL
    # ---------------------------
    def run_sql(self, sql):
        result = db.session.execute(text(sql))
        df = pd.DataFrame(result.mappings().all())
        return df

    # ---------------------------
    # 5. Gerar gráfico
    # ---------------------------
    def create_plot(self, df, x, y, chat_id):
        fig_id = f"chart_{uuid.uuid4().hex[:8]}.png"
        base_dir = os.path.abspath(os.path.dirname(__file__))
        path = os.path.join(base_dir, 'chats', g.user.matricula, chat_id, "charts")
        os.makedirs(path, exist_ok=True)
        filepath = os.path.join(path, fig_id)

        plt.figure(figsize=(8, 5))
        plt.bar(df[x], df[y])
        plt.tight_layout()
        plt.savefig(filepath)
        plt.close()

        return fig_id
