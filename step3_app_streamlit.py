import streamlit as st
import os
import csv
import json
import re
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, text

# LlamaIndex imports
from llama_index.core import SQLDatabase
from llama_index.llms.openai import OpenAI
from llama_index.core.query_engine import NLSQLTableQueryEngine

# ---------------------------------------------------------
# 1) Database/Logs configuration
# ---------------------------------------------------------
DB_FILENAME = "local_pitchbook.db"
LOG_FILENAME = "query-logs.csv"

if not os.path.exists(DB_FILENAME):
    st.error(f"Banco de dados {DB_FILENAME} não encontrado. Execute o Passo 1 e 2 primeiro!")
    st.stop()

# ---------------------------------------------------------
# 2) Base Prompt
# ---------------------------------------------------------
BASE_PROMPT = """
Você é um assistente de geração de consultas SQL sobre o banco de dados Pitchbook.
Sempre que o usuário mencionar o nome de uma empresa ou quiser filtrar por 'nome da empresa',
use a coluna 'companyAlsoKnownAs' (não 'companyName'), aplicando LOWER(...) e LIKE, 
por exemplo:
   LOWER(companyAlsoKnownAs) LIKE LOWER('%TextoDoUsuario%').

Use sempre LIKE ao invés de '=', e lembre-se de ignorar case (use LOWER(...)).
Nunca use '=' quando estiver filtrando pelo nome da empresa, sempre use LIKE.

Leve em consideração o histórico da conversa para responder de forma consistente e contextual.

Schema do banco de dados:
{schema}

Histórico do chat:
{chat_history}

Pergunta do usuário:
{query_str}

Gere SOMENTE a consulta SQL válida (ou seja, nada de texto adicional além do SQL).
"""

# ---------------------------------------------------------
# 3) Build QueryEngine
# ---------------------------------------------------------
def build_query_engine(chat_history: str):
    engine = create_engine(f"sqlite:///{DB_FILENAME}", echo=False)
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

    sql_db = SQLDatabase(engine, include_tables=tables)

    # Use "gpt-4o-mini" in both calls
    llm = OpenAI(model="gpt-4o-mini", temperature=0.0, max_tokens=512)

    final_prompt = BASE_PROMPT.replace("{chat_history}", chat_history)

    query_engine = NLSQLTableQueryEngine(
        sql_database=sql_db,
        tables=tables,
        llm=llm,
        sql_prompt_template=final_prompt
    )
    return query_engine

# ---------------------------------------------------------
# 4) Post-process the SQL (force usage of LIKE)
# ---------------------------------------------------------
def post_process_sql(query: str) -> str:
    if not query or "WHERE" not in query:
        return query

    pattern_eq = r"(?i)WHERE\s+CompanyName\s*=\s*'([^']+)'"
    def repl_eq(match):
        text_val = match.group(1)
        return f"WHERE LOWER(companyAlsoKnownAs) LIKE LOWER('%{text_val}%')"

    query = re.sub(pattern_eq, repl_eq, query)

    pattern_like = r"(?i)WHERE\s+CompanyName\s+LIKE\s*'([^']+)'"
    def repl_like(match):
        text_val = match.group(1)
        if not text_val.startswith('%'):
            text_val = '%' + text_val
        if not text_val.endswith('%'):
            text_val += '%'
        return f"WHERE LOWER(companyAlsoKnownAs) LIKE LOWER('{text_val}')"

    query = re.sub(pattern_like, repl_like, query)

    return query

# ---------------------------------------------------------
# 5) Second call to LLM for a final natural-language answer
# ---------------------------------------------------------
def generate_natural_answer(llm: OpenAI, question: str, rows, columns):
    """
    A second call to the LLM to produce a final text answer
    based on the user's question and the rows returned.
    """
    if not rows:
        prompt_text = f"""
Você é um assistente. O usuário fez a pergunta: "{question}"
Não foi encontrado nenhum dado no banco de dados.
Responda em português de forma curta.
"""
        res = llm.complete(prompt_text)
        # Use .text instead of .response
        answer_str = res.text
        return answer_str.strip()
    else:
        sample_rows = rows[:3]
        col_str = ", ".join(columns)
        row_text = "\n".join(str(r) for r in sample_rows)

        prompt_text = f"""
O usuário perguntou: "{question}"
Você obteve do banco de dados as colunas: {col_str}
Eis um trecho das primeiras linhas retornadas: 
{row_text}

Gere uma explicação em português, resumindo de forma clara os dados 
e respondendo à pergunta do usuário.
"""
        res = llm.complete(prompt_text)
        answer_str = res.text  # Changed from .response to .text
        return answer_str.strip()

# ---------------------------------------------------------
# 6) Load CSV (to rebuild chat history)
# ---------------------------------------------------------
def load_chat_from_csv():
    if not os.path.exists(LOG_FILENAME):
        return "", []
    chat_text = ""
    simple_history = []
    with open(LOG_FILENAME, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            question = row.get("question", "")
            response_text = row.get("response_text", "")
            chat_text += f"Usuário: {question}\nAssistente: {response_text}\n"
            simple_history.append(question)
    return chat_text, simple_history

# ---------------------------------------------------------
# 7) Session state initialization
# ---------------------------------------------------------
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = ""

if "history" not in st.session_state:
    st.session_state["history"] = []

if "user_question" not in st.session_state:
    st.session_state["user_question"] = ""

if "response_text" not in st.session_state:
    st.session_state["response_text"] = ""

if "sql_query" not in st.session_state:
    st.session_state["sql_query"] = ""

if "result_data" not in st.session_state:
    st.session_state["result_data"] = None

if "chat_loaded" not in st.session_state:
    st.session_state["chat_loaded"] = False

if not st.session_state["chat_loaded"]:
    csv_chat_text, csv_history = load_chat_from_csv()
    st.session_state["chat_history"] += csv_chat_text
    st.session_state["history"].extend(csv_history)
    st.session_state["chat_loaded"] = True

# ---------------------------------------------------------
# 8) Sidebar: Query History
# ---------------------------------------------------------
st.sidebar.title("Query History")
if len(st.session_state["history"]) == 0:
    st.sidebar.write("Nenhuma query realizada ainda.")
else:
    for idx, h in enumerate(st.session_state["history"], start=1):
        st.sidebar.markdown(f"**{idx}.** {h}")

if st.sidebar.button("Clear History"):
    st.session_state["chat_history"] = ""
    st.session_state["history"] = []
    st.session_state["user_question"] = ""
    st.session_state["response_text"] = ""
    st.session_state["sql_query"] = ""
    st.session_state["result_data"] = None
    if hasattr(st, "rerun"):
        st.rerun()

# ---------------------------------------------------------
# 9) Main Layout
# ---------------------------------------------------------
st.title("Query your data on Pitchbook")

user_question = st.text_area(
    "Digite sua pergunta (ex.: 'Quais empresas foram fundadas em 2015?')",
    value=st.session_state["user_question"],
    height=100,
    max_chars=None
)

col_a, col_b = st.columns(2)

# ---------------------------------------------------------
# 10) "Consultar" button
# ---------------------------------------------------------
with col_a:
    if st.button("Consultar"):
        st.session_state["user_question"] = user_question
        if user_question.strip():
            # 1) Build QueryEngine, get raw SQL
            engine_llama = build_query_engine(st.session_state["chat_history"])
            with st.spinner("Gerando SQL..."):
                response = engine_llama.query(user_question)

            raw_sql = response.metadata.get("sql_query", "(Não disponível)")

            # 2) Post-process to ensure LIKE
            fixed_sql = post_process_sql(raw_sql)

            # 3) Execute DB query
            engine_conn = create_engine(f"sqlite:///{DB_FILENAME}").connect()
            rows = []
            columns = []
            try:
                if "SELECT" in fixed_sql.upper():
                    result_proxy = engine_conn.execute(text(fixed_sql))
                    columns = list(result_proxy.keys())
                    fetched = result_proxy.fetchall()
                    rows = [list(r) for r in fetched]
            finally:
                engine_conn.close()

            # 4) Second LLM call for final text
            # Note we're using the same "gpt-4o-mini" model for consistency
            llm = OpenAI(model="gpt-4o-mini", temperature=0.0)
            final_answer = generate_natural_answer(llm, user_question, rows, columns)

            # 5) Store in session
            st.session_state["response_text"] = final_answer
            st.session_state["sql_query"] = fixed_sql
            st.session_state["result_data"] = rows

            # 6) Display results
            container = st.container()
            with container:
                st.markdown("### Resposta (Linguagem Natural)")
                st.text_area(
                    label="Resposta em texto",
                    value=final_answer,
                    height=150,
                    disabled=True,
                    label_visibility="collapsed",
                    key="response_area"
                )

                st.markdown("### Query SQL Gerada (Corrigida)")
                st.text_area(
                    label="Query SQL",
                    value=fixed_sql,
                    height=150,
                    disabled=True,
                    label_visibility="collapsed",
                    key="sql_area"
                )

                st.markdown("### Dados Retornados")
                if rows:
                    df_result = pd.DataFrame(rows, columns=columns)
                    st.dataframe(df_result, use_container_width=True)
                else:
                    st.write("Nenhum dado retornado ou query sem resultado.")

            st.markdown("### Dados Retornados")
            if rows:
                df_result = pd.DataFrame(rows, columns=columns)
                # Aumentando a largura da tabela de dados
                st.dataframe(df_result, use_container_width=True)
            else:
                st.write("Nenhum dado retornado ou query sem resultado.")

            # 7) Update chat_history
            st.session_state["chat_history"] += f"Usuário: {user_question}\n"
            st.session_state["chat_history"] += f"Assistente: {final_answer}\n"

            # 8) Update question history
            st.session_state["history"].append(user_question)

            # 9) Write logs to CSV
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            result_data_str = json.dumps(rows) if rows else ""
            
            # Lê o arquivo existente se existir, senão cria uma lista vazia
            existing_data = []
            if os.path.exists(LOG_FILENAME):
                try:
                    with open(LOG_FILENAME, "r", newline="", encoding="utf-8") as f:
                        reader = csv.DictReader(f)
                        existing_data = list(reader)
                except Exception as e:
                    st.error(f"Erro ao ler o arquivo de logs: {str(e)}")
                    existing_data = []

            # Adiciona a nova entrada
            new_entry = {
                "timestamp": now_str,
                "question": user_question,
                "response_text": final_answer,
                "sql_query": fixed_sql,
                "result_data": result_data_str
            }
            
            # Garante que a nova entrada seja adicionada mesmo se houver erro na leitura
            existing_data.append(new_entry)
            
            # Escreve todas as entradas de volta no arquivo
            try:
                with open(LOG_FILENAME, "w", newline="", encoding="utf-8") as f:
                    fieldnames = ["timestamp", "question", "response_text", "sql_query", "result_data"]
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    for row in existing_data:
                        # Garante que todas as colunas existam
                        sanitized_row = {
                            "timestamp": row.get("timestamp", ""),
                            "question": row.get("question", ""),
                            "response_text": row.get("response_text", ""),
                            "sql_query": row.get("sql_query", ""),
                            "result_data": row.get("result_data", "")
                        }
                        writer.writerow(sanitized_row)
                        
            except Exception as e:
                st.error(f"Erro ao salvar o arquivo de logs: {str(e)}")
                
            # Registra a operação no console para debug
            print(f"Query logged at {now_str}: {fixed_sql}")
        else:
            st.warning("Por favor, insira uma pergunta antes de clicar em Consultar.")

# ---------------------------------------------------------
# 11) "New Query" button
# ---------------------------------------------------------
with col_b:
    if st.button("New Query"):
        st.session_state["user_question"] = ""
        st.session_state["response_text"] = ""
        st.session_state["sql_query"] = ""
        st.session_state["result_data"] = None
        if hasattr(st, "rerun"):
            st.rerun()