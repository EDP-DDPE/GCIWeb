# Sistema GCI Web - Flask + SQL Server

Sistema web para gerenciamento de estudos de viabilidade elétrica, desenvolvido em Flask com SQL Server.

## 🚀 Características

- **Performance Otimizada**: Evita o problema N+1 através de relacionamentos SQLAlchemy bem configurados
- **SQL Server Nativo**: Conexão otimizada com SQL Server usando pyodbc
- **API RESTful**: Endpoints JSON para integração e frontend
- **Pool de Conexões**: Gerenciamento inteligente de conexões com banco
- **Configuração Flexível**: Suporte a múltiplos ambientes via variáveis de ambiente

## 📋 Pré-requisitos

### Sistema
- Python 3.8+
- SQL Server 2016+ ou SQL Server Express
- Driver ODBC do SQL Server

### Driver ODBC

#### Windows
```bash
# Baixe e instale de:
# https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install -y curl

# Adicionar repositório Microsoft
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list > /etc/apt/sources.list.d/mssql-release.list

# Instalar driver
sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql17
sudo apt-get install -y unixodbc-dev
```

#### macOS
```bash
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
brew update
HOMEBREW_NO_ENV_FILTERING=1 ACCEPT_EULA=Y brew install msodbcsql17 mssql-tools
```

## ⚡ Instalação Rápida

### Opção 1: Setup Automatizado
```bash
# Clone o repositório
git clone <repository-url>
cd gci-web

# Execute o setup automatizado
python setup.py

# Edite as configurações
nano .env

# Ative o ambiente virtual
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Execute a aplicação
python app.py
```

### Opção 2: Instalação Manual
```bash
# 1. Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate (Windows)

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Configurar variáveis de ambiente
cp .env.example .env
nano .env  # Editar configurações

# 4. Testar conexão
python database.py

# 5. Criar tabelas
flask init-db

# 6. Executar aplicação
python app.py
```

## ⚙️ Configuração

### Variáveis de Ambiente Principais

Edite o arquivo `.env` com suas configurações:

```env
# SQL Server
SQLSERVER_HOST=localhost
SQLSERVER_PORT=1433
SQLSERVER_DATABASE=gciweb_db
SQLSERVER_USERNAME=sa
SQLSERVER_PASSWORD=YourPassword123!

# Driver (ajuste conforme sua instalação)
SQLSERVER_DRIVER=ODBC Driver 17 for SQL Server

# Flask
SECRET_KEY=sua-chave-secreta-aqui
FLASK_DEBUG=false
```

### Configurações Avançadas

```env
# Pool de conexões
SQLALCHEMY_POOL_SIZE=10
SQLALCHEMY_MAX_OVERFLOW=20
SQLALCHEMY_POOL_TIMEOUT=30
SQLALCHEMY_POOL_RECYCLE=3600

# SSL/Certificados
TRUST_SERVER_CERTIFICATE=yes
SQLSERVER_ENCRYPT=no

# Timeouts
CONNECTION_TIMEOUT=30
COMMAND_TIMEOUT=30
```

## 🗄️ Estrutura do Banco de Dados

O sistema utiliza o schema `gciweb` no SQL Server com as seguintes tabelas principais:

- **estudos**: Estudos de viabilidade
- **empresas**: Empresas solicitantes
- **usuarios**: Usuários do sistema
- **regionais**: Regionais da empresa
- **alternativas**: Alternativas técnicas
- **anexos**: Arquivos anexados
- **status_estudo**: Histórico de status

### Criação do Schema

```sql
-- Execute no SQL Server
CREATE DATABASE gciweb_db;
USE gciweb_db;

-- O schema será criado automaticamente pelo Flask
-- Ou execute o arquivo gciweb_schema.sql
```

## 🔧 Comandos Disponíveis

### Flask CLI
```bash
# Testar conexão
flask test-db

# Informações do banco
flask db-info

# Criar/recriar tabelas
flask init-db
```

### Scripts Python
```bash
# Teste standalone de conexão
python database.py

# Verificar apenas requisitos
python setup.py --check

# Instalar apenas dependências
python setup.py --deps
```

## 📚 API Endpoints

### Estudos
```http
GET    /api/estudos              # Listar estudos (paginado)
GET    /api/estudos/{id}         # Obter estudo específico
POST   /api/estudos              # Criar estudo
PUT    /api/estudos/{id}         # Atualizar estudo
DELETE /api/estudos/{id}         # Remover estudo
```

### Dashboard
```http
GET    /api/dashboard/stats      # Estatísticas gerais
```

### Sistema
```http
GET    /                         # Status da aplicação
GET    /health                   # Health check
```

### Exemplos de Uso

#### Listar estudos com paginação
```bash
curl "http://localhost:5000/api/estudos?page=1&per_page=20"
```

#### Obter estudo específico
```bash
curl "http://localhost:5000/api/estudos/123"
```

## 🚀 Performance e Otimizações

### Prevenção do Problema N+1

O sistema utiliza estratégias otimizadas para evitar o problema N+1:

```python
# ❌ Problemático - gera N+1 queries
estudos = Estudo.query.all()
for estudo in estudos:
    print(estudo.regional.regional)  # Query para cada estudo

# ✅ Otimizado - apenas 1 query
estudos = Estudo.query.options(
    db.joinedload(Estudo.regional)
).all()
for estudo in estudos:
    print(estudo.regional.regional)  # Dados já carregados
```

### Métodos Otimizados

```python
# Carregar estudo com todos relacionamentos
estudo = Estudo.get_with_all_relations(estudo_id)

# Listar com relacionamentos básicos
estudos = Estudo.get_list_with_basic_relations().all()

# Paginação otimizada
from models import get_estudos_com_paginacao
estudos = get_estudos_com_paginacao(page=1, per_page=20)
```

## 🔒 Segurança

### Conexão com Banco
- Pool de conexões com timeout
- Parâmetros escapados automaticamente
- Isolamento de transações
- Conexões SSL configuráveis

### Aplicação
- Chave secreta para sessões
- Validação de entrada
- CORS configurável
- Headers de segurança

## 📊 Monitoramento

### Logs
```python
# Habilitar logs SQL (apenas desenvolvimento)
SQLALCHEMY_ECHO=true

# Configurar nível de log
LOG_LEVEL=INFO
```

### Health Check
```bash
curl http://localhost:5000/health
```

### Métricas do Pool de Conexões
```python
# No código da aplicação
from database import db_manager
info = db_manager.db.engine.pool.status()
```

## 🐳 Deploy

### Docker (Opcional)
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:create_app()"]
```

### Produção
```bash
# Usar Gunicorn para produção
pip install gunicorn
gunicorn --workers 4 --bind 0.0.0.0:5000 "app:create_app()"
```

## 🛠️ Desenvolvimento

### Estrutura do Projeto
```
gci-web/
├── app.py              # Aplicação Flask principal
├── models.py           # Modelos SQLAlchemy
├── database.py         # Conexão SQL Server
├── setup.py            # Script de instalação
├── requirements.txt    # Dependências Python
├── .env.example        # Exemplo de configuração
├── gciweb_schema.sql   # Schema do banco
└── README.md          # Esta documentação


├── app/
│ ├── alternativa
│ │ ├── templates
│ │ │ ├── alternativa
│ │ │ │ └── alternativa.html
│ │ ├── __init__.py
│ │ ├── forms.py
│ │ └── routes.py
│ ├── api
│ │ ├── __init__.py  (Não tem nada)
│ │ └── routes.py
│ ├── auth
│ │ ├── templates
│ │ │ ├── auth
│ │ │ │ └── login.html
│ │ ├── __init__.py
│ │ └── routes.py
│ ├── cadastro
│ │ ├── templates
│ │ │ ├── cadastro
│ │ │ │ ├── cadastrar_estudo.html
│ │ │ │ └── editar_estudo.html
│ │ ├── __init__.py
│ │ ├── forms.py
│ │ └── routes.py
│ ├── circuitos
│ │ ├── __init__.py
│ │ ├── forms.py
│ │ └── routes.py
│ ├── deploy
│ │ ├── __init__.py
│ │ ├── restart_atlas.sh
│ │ └── routes.py
│ ├── listar
│ │ ├── static
│ │ │ ├── css
│ │ │ │ └── listar_estudos.css
│ │ │ └── js
│ │ │ │ └── listar_estudos.js
│ │ ├── templates
│ │ │ ├── listar
│ │ │ │ └── listar.html
│ │ ├── __init__.py
│ │ ├── forms.py
│ │ └── routes.py
│ ├── main
│ │ ├── static
│ │ │ ├── css
│ │ │ │ └── listar.css
│ │ │ ├── images
│ │ │ │ └── background.png
│ │ │ └── js
│ │ │ │ └── listar.js
│ │ ├── templates
│ │ │ ├── main
│ │ │ │ └── index.html
│ │ ├── __init__.py
│ │ └── routes.py
│ ├── municipios
│ │ ├── templates
│ │ │ └── municipios.html
│ │ ├── __init__.py
│ │ ├── forms.py
│ │ └── routes.py
│ ├── static
│ │ ├── css
│ │ │ └── listar_unificado.css
│ │ ├── js
│ │ │ └── listar_unificado.js
│ ├── status
│ │ ├── templates
│ │ │ ├── status
│ │ │ │ └── status.html
│ │ ├── __init__.py
│ │ └── routes.py
│ ├── subestacoes
│ │ ├── templates
│ │ │ ├── editar_subestacao.html
│ │ │ ├── listar.html
│ │ │ ├── nova_subestacao.html
│ │ │ └── subestacoes.html
│ │ ├── __init__.py
│ │ ├── forms.py
│ │ └── routes.py
│ ├── templates
│ │ ├── base.html
│ │ ├── lista_generica.html
│ │ └── listar_unificado.html
│ ├── user
│ │ ├── templates
│ │ │ ├── user
│ │ │ │ └── user.html
│ │ ├── __init__.py
│ │ ├── forms.py
│ │ └── routes.py
│ ├── __init__.py
│ ├── config.py
│ ├── database.py
│ ├── gciweb_schema.sql
│ ├── insert into tables.sql
│ ├── models.py
│ ├── schema.sql
├── run.py
├── .env
├── .gitignore
├── LICENSE
├── README.md
├── todo.py
├── wsgi.py

```

### Adicionando Novos Models
```python
# Em models.py
class NovoModel(db.Model):
    __tablename__ = 'nova_tabela'
    __table_args__ = {'schema': 'gciweb'}
    
    id = db.Column(db.BigInteger, primary_key=True)
    # ... outros campos
```

### Executando Testes
```bash
# Instalar dependências de teste
pip install pytest pytest-flask

# Executar testes
pytest
```

## 🔧 Troubleshooting

### Problemas Comuns

#### Erro: "Driver not found"
```bash
# Verifique drivers instalados
python -c "import pyodbc; print(pyodbc.drivers())"

# Instale driver correto (veja seção pré-requisitos)
```

#### Erro: "Login failed"
```bash
# Verifique credenciais no .env
# Teste conexão manual no SQL Server
sqlcmd -S localhost -U sa -P YourPassword123!
```

#### Erro: "Connection timeout"
```bash
# Verifique se SQL Server aceita conexões TCP/IP
# SQL Server Configuration Manager > Protocols > TCP/IP = Enabled
# Reinicie o serviço SQL Server
```

#### Performance lenta
```bash
# Habilite logs para investigar
SQLALCHEMY_ECHO=true

# Verifique índices no banco
# Use métodos otimizados dos models
```

### Logs Úteis
```bash
# Ver logs de conexão
tail -f app.log

# Logs do SQL Server
# Windows: Event Viewer > Windows Logs > Application
# Linux: /var/log/mssql/
```

## 📞 Suporte

Para dúvidas e problemas:

1. Verifique a documentação acima
2. Execute o diagnóstico: `python setup.py --check`
3. Teste a conexão: `flask test-db`
4. Verifique os logs da aplicação

## 📄 Licença

[Adicione informações de licença aqui]

---

**🎯 Sistema GCI Web** - Desenvolvido para máxima performance com SQL Server
