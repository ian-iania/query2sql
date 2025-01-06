# FORMER step2_index_schema.py

import os
from sqlalchemy import create_engine
from llama_index.core import SQLDatabase
from llama_index.llms.openai import OpenAI
from llama_index.core.query_engine import NLSQLTableQueryEngine

"""
Script para indexar (via LlamaIndex) as tabelas do banco 'local_pitchbook.db'.
Enriquecido com metadados e instruções adicionais para melhorar consultas em LN.
"""

# ---------------------------------------------------
# 1. Conexão ao banco
# ---------------------------------------------------
DB_FILENAME = "local_pitchbook.db"
if not os.path.exists(DB_FILENAME):
    raise FileNotFoundError(f"Arquivo {DB_FILENAME} não encontrado. Execute o Passo 1 primeiro!")

engine = create_engine(f"sqlite:///{DB_FILENAME}", echo=False)

# ---------------------------------------------------
# 2. Definir as tabelas que serão incluídas no índice
# ---------------------------------------------------
tables = [
    "company",
    "company_employee_history_relation",
    "company_entity_type_relation",
    "company_industry_relation",
    "company_investor_relation",
    "company_market_analysis_relation",
    "company_morningstar_code_relation",
    "company_naics_code_relation",
    "company_sic_code_relation",
    "company_vertical_relation",
]

# ---------------------------------------------------
# 3. Metadados / Contexto das Tabelas
#    (Opcional: complementa docstrings do schema)
# ---------------------------------------------------
TABLE_CONTEXT = {
    "company": """
    Tabela principal com dados de empresas.
    - Colunas principais: 
        CompanyID (PK), CompanyName, Employees, YearFounded, ...
    - 'Employees' indica a contagem atual de funcionários.
    - 'Description' e 'Keywords' para buscas textuais.
    - 'PrimaryIndustrySector' e 'OwnershipStatus' ajudam a filtrar por setor/estrutura.
    """,
    "company_employee_history_relation": """
    Registros históricos de número de funcionários.
    - CompanyID (FK -> company.CompanyID).
    - EmployeeCount indica a contagem de funcionários na data (Date).
    """,
    "company_entity_type_relation": """
    Define o tipo de entidade (Ex.: 'Company', 'Non-profit', etc.).
    - CompanyID (FK -> company.CompanyID).
    - 'IsPrimary' indica se é o tipo principal.
    """,
    "company_industry_relation": """
    Mapeia setores/indústrias em que a empresa opera.
    - CompanyID (FK -> company.CompanyID).
    - Ex.: 'IndustrySector' = 'Consumer Products', 'IsPrimary' = 'Yes'.
    """,
    "company_investor_relation": """
    Relação entre a empresa e seus investidores.
    - CompanyID (sem FK explícito nesse script, mas referencia 'company.CompanyID').
    - InvestorID, InvestorName, InvestorSince, InvestorExit, ...
    - InvestorStatus = 'Active', 'Former', etc.
    """,
    "company_market_analysis_relation": """
    Segmentações e verticais definidas por analistas (PitchBook).
    - CompanyID (FK -> company.CompanyID).
    - AnalystCuratedVertical, Segment, Subsegment, ...
    """,
    "company_morningstar_code_relation": """
    Códigos de classificação Morningstar.
    - CompanyID (FK -> company.CompanyID).
    - MorningstarCode (numérico), MorningstarDescription.
    """,
    "company_naics_code_relation": """
    Códigos NAICS (até 6 dígitos).
    - CompanyID (FK -> company.CompanyID).
    - NaicsSectorCode (2 dígitos), NaicsIndustryCode (6 dígitos).
    """,
    "company_sic_code_relation": """
    Códigos SIC (4 dígitos).
    - CompanyID (FK -> company.CompanyID).
    - SicCode, SicDescription.
    """,
    "company_vertical_relation": """
    Verticals adicionais.
    - CompanyID (FK -> company.CompanyID).
    - Vertical (texto), ex.: 'Real Estate Technology'.
    """,
}

# ---------------------------------------------------
# 4. Criar a instância do SQLDatabase (LlamaIndex)
# ---------------------------------------------------
# Podemos passar 'include_tables' para limitar somente às tabelas acima.
# 'sample_rows_in_table_info' (opcional) extrai exemplos de dados para o LLM.
sql_database = SQLDatabase(
    engine,
    include_tables=tables,
    sample_rows_in_table_info=2  # por exemplo, pega 2 linhas de cada tabela
)

# ---------------------------------------------------
# 5. Definir o LLM
# ---------------------------------------------------
# Ajuste o model e a API Key conforme seu ambiente:
llm = OpenAI(
    model="gpt-4o-mini",
    temperature=0.0,
    max_tokens=512
)

# ---------------------------------------------------
# 6. Prompt de contexto (Opcional)
# ---------------------------------------------------
BASE_PROMPT = """
Você é um assistente especializado em gerar queries SQL (NLSQL) no banco Pitchbook.
Use as seguintes informações de contexto para compreender cada tabela:

{table_context}

A seguir está o schema e alguns exemplos de linhas de cada tabela:
{schema}

Quando o usuário fizer perguntas em linguagem natural, retorne APENAS a query SQL, sem explicações adicionais.
"""

# ---------------------------------------------------
# 7. Criar nosso "NLSQLTableQueryEngine"
#    - Passamos metadados extras em table_context_dict
# ---------------------------------------------------
query_engine = NLSQLTableQueryEngine(
    sql_database=sql_database,
    tables=tables,  # Quais tabelas o LLM pode acessar
    llm=llm,
    # table_context_dict: dicionário {nome_da_tabela: string com contexto}
    # sql_prompt_template: caso queira injetar um prompt-base customizado
    table_context_dict=TABLE_CONTEXT,
    sql_prompt_template=BASE_PROMPT
)

# ---------------------------------------------------
# 8. Queries de teste
# ---------------------------------------------------
test_queries = [
    "Quais empresas foram fundadas no ano de 2015?",
    "Liste as 5 empresas com mais funcionários, se houver."
]

if __name__ == "__main__":
    # A) Fazer algumas queries e imprimir a resposta
    for q in test_queries:
        print(f"\n=== Pergunta: {q} ===")
        response = query_engine.query(q)
        print("Resposta (SQL):\n", response)

    # B) Se desejarmos, podemos também exibir o SQL gerado separadamente
    #    O "metadata" costuma vir em response.metadata.get("sql_query")
    #    Exemplo:
    #    raw_sql = response.metadata.get("sql_query", "(Not available)")
    #    print("SQL Gerado:", raw_sql)
