# Festa IFC Blumenau

Aplicação web para organizar a festa do IFC Campus Blumenau. A equipe pode
cadastrar alimentos e seus preços de venda, insumos doados e seus doadores,
além das pessoas que trabalharão no evento (alunos, familiares e servidores).

## Funcionalidades

- CRUD de alimentos, com descrição, preço e composição por insumos.
- CRUD de insumos doados, unidade de medida e fornecedor/doador.
- CRUD de fornecedores/doadores.
- CRUD de trabalhadores, com categoria e contato.
- SQLite para desenvolvimento e testes locais; MySQL para produção.

## Requisitos

- Python 3.10 ou superior
- [uv](https://docs.astral.sh/uv/)

## Executar localmente

Na raiz do projeto:

```powershell
uv sync
uv run streamlit run src/app.py
```

Na primeira execução, o sistema cria `data/festa_ifc.db` automaticamente.
SQLite é o banco padrão e não exige configuração adicional.

## Configuração do MySQL

Defina `DATABASE_URL` com uma URL SQLAlchemy e o driver PyMySQL. Não versione
credenciais. Exemplo para PowerShell:

```powershell
$env:DATABASE_URL = "mysql+pymysql://usuario:senha@host:3306/festa_ifc?charset=utf8mb4"
uv run streamlit run src/app.py
```

Para produção, configure essa variável no ambiente de execução. No Streamlit
Community Cloud, também é possível inserir `DATABASE_URL` em **App settings >
Secrets**; a aplicação lê esse segredo quando a variável de ambiente não está
definida. O banco MySQL e o usuário precisam existir antes de iniciar o app.

## Estrutura

```text
src/
  app.py        # Interface Streamlit e operações CRUD
  database.py   # Configuração de engine e sessões SQLAlchemy
  models.py     # Entidades persistentes e relacionamentos
```

## Deploy no Streamlit Community Cloud

1. Envie o repositório para um provedor Git suportado pelo Streamlit.
2. Crie uma aplicação em <https://share.streamlit.io/> apontando para
   `src/app.py`.
3. Configure `DATABASE_URL` nas configurações de Secrets da aplicação com a URL
   do MySQL de produção.
4. Verifique se o servidor MySQL permite conexões do ambiente de deploy e se o banco de dados
informado já foi criado. As tabelas da aplicação são criadas ao iniciar.

O `pyproject.toml` e o `uv.lock` registram as dependências utilizadas. Para
atualizar o lockfile após alterar dependências, execute `uv lock`.
