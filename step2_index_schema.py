# step2_index_schema.py

import os
from sqlalchemy import create_engine
from llama_index.core import SQLDatabase
from llama_index.llms.openai import OpenAI
from llama_index.core.query_engine import NLSQLTableQueryEngine

# -----------------------------
# 1. Conectar ao banco
# -----------------------------
DB_FILENAME = "local_pitchbook.db"
if not os.path.exists(DB_FILENAME):
    raise FileNotFoundError(f"Arquivo {DB_FILENAME} não encontrado. Execute o Passo 1 primeiro!")

engine = create_engine(f"sqlite:///{DB_FILENAME}", echo=False)

# Podemos listar as tabelas que queremos disponibilizar ao LLM.
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
    "company_vertical_relation"
]

# Criamos a instância do SQLDatabase
sql_database = SQLDatabase(engine, include_tables=tables)

# -----------------------------
# 2. Definir o LLM (GPT 3.5, etc.)
# -----------------------------
# Ajuste para sua chave de API do OpenAI:
# (você também pode setar via os.environ["OPENAI_API_KEY"] = "sk-..."
llm = OpenAI(
    model="gpt-3.5-turbo",
    temperature=0.0,
    max_tokens=512
)

# -----------------------------
# 3. Criar nosso "NLSQLTableQueryEngine"
# -----------------------------
query_engine = NLSQLTableQueryEngine(
    sql_database=sql_database,
    tables=tables,  # quais tabelas o LLM pode usar
    llm=llmcle
)

# -----------------------------
# 4. Fazer queries de teste
# -----------------------------
test_queries = [
    "Quais empresas foram fundadas no ano de 2015?",
    "Liste as 5 empresas com mais funcionários, se houver."
]

if __name__ == "__main__":
    for q in test_queries:
        print(f"\n=== Pergunta: {q} ===")
        response = query_engine.query(q)
        print("Resposta:\n", response)
