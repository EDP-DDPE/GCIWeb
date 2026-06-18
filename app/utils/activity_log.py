"""Histórico de atividades dos usuários gravado em arquivo (append-only).

Optou-se por arquivo em vez de banco porque o banco já é gargalo de
performance e o log roda em ações do dia a dia. A escrita é um append de
uma linha JSON (JSONL), barata e sem round-trip com o SQL Server.

Cada dia gera um arquivo `logs/atividade-AAAA-MM-DD.log`. A página de
administração lê os arquivos dos últimos dias, filtra e pagina em memória.
"""

import os
import json
import threading
from datetime import datetime, date

from flask import request, g, current_app

# Serializa as escritas dentro do processo. Entre processos (múltiplos
# workers) o append em modo texto de linhas curtas é suficientemente atômico.
_lock = threading.Lock()


def _log_dir():
    """Pasta `logs/` na raiz do projeto (mesmo nível da pasta `app/`)."""
    base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    caminho = os.path.join(base, 'logs')
    os.makedirs(caminho, exist_ok=True)
    return caminho


def _arquivo_do_dia(dia=None):
    dia = dia or date.today()
    return os.path.join(_log_dir(), f'atividade-{dia.isoformat()}.log')


def registrar_log(acao, entidade=None, entidade_id=None, descricao=None, usuario=None):
    """Registra uma ação importante do usuário no arquivo do dia.

    Resiliente: qualquer falha é silenciada (apenas logada) para nunca
    quebrar a request principal.

    Args:
        acao: identificador curto da ação (ex.: 'criar_estudo').
        entidade: tipo do objeto afetado (ex.: 'estudo', 'anexo').
        entidade_id: id do objeto afetado, quando houver.
        descricao: texto legível do que aconteceu.
        usuario: instância de Usuario; se omitido usa g.user (necessário
                 passar explicitamente no login, quando g.user ainda não
                 reflete a nova sessão).
    """
    try:
        u = usuario if usuario is not None else getattr(g, 'user', None)
        registro = {
            'data': datetime.now().isoformat(timespec='seconds'),
            'id_usuario': getattr(u, 'id_usuario', None),
            'matricula': getattr(u, 'matricula', None),
            'nome': getattr(u, 'nome', None),
            'acao': acao,
            'entidade': entidade,
            'entidade_id': entidade_id,
            'descricao': descricao,
            'ip': request.remote_addr if request else None,
        }
        linha = json.dumps(registro, ensure_ascii=False) + '\n'
        with _lock:
            with open(_arquivo_do_dia(), 'a', encoding='utf-8') as f:
                f.write(linha)
    except Exception as e:  # nunca propaga
        try:
            current_app.logger.error(f"Falha ao registrar log de atividade ({acao}): {e}")
        except Exception:
            pass


def ler_logs(dias=7, matricula=None, acao=None, busca=None, page=1, per_page=50):
    """Lê os logs dos últimos `dias`, aplica filtros e pagina.

    Retorna os mais recentes primeiro.
    """
    registros = []
    hoje = date.today()

    for i in range(max(dias, 1)):
        dia = date.fromordinal(hoje.toordinal() - i)
        caminho = _arquivo_do_dia(dia)
        if not os.path.isfile(caminho):
            continue
        try:
            with open(caminho, 'r', encoding='utf-8') as f:
                for linha in f:
                    linha = linha.strip()
                    if not linha:
                        continue
                    try:
                        registros.append(json.loads(linha))
                    except (ValueError, json.JSONDecodeError):
                        continue
        except Exception:
            continue

    # Filtros
    if matricula:
        registros = [r for r in registros if r.get('matricula') == matricula]
    if acao:
        registros = [r for r in registros if r.get('acao') == acao]
    if busca:
        b = busca.lower()
        registros = [r for r in registros
                     if b in json.dumps(r, ensure_ascii=False).lower()]

    # Mais recentes primeiro
    registros.sort(key=lambda r: r.get('data') or '', reverse=True)

    total = len(registros)
    per_page = max(per_page, 1)
    page = max(page, 1)
    inicio = (page - 1) * per_page
    itens = registros[inicio:inicio + per_page]

    return {
        'logs': itens,
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page,
    }
