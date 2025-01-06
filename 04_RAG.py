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

# ----------------------------------------------
# 1) Configurações e caminhos
# ----------------------------------------------
DB_FILENAME = "local_pitchbook.db"
LOG_FILENAME = "query-logs.csv"

# Aqui apontamos para o arquivo de prompt no formato Markdown
BASE_PROMPT_FILE = "BASE_PROMPT.md"

# Verificações iniciais
if not os.path.exists(DB_FILENAME):
    st.error(f"Database {DB_FILENAME} not found. Please run Steps 1 and 2 first!")
    st.stop()

if not os.path.exists(BASE_PROMPT_FILE):
    st.error(f"Base prompt file '{BASE_PROMPT_FILE}' not found in the current directory!")
    st.stop()

# ----------------------------------------------
# 2) Ler o conteúdo do BASE_PROMPT.md
# ----------------------------------------------
with open(BASE_PROMPT_FILE, "r", encoding="utf-8") as f:
    BASE_PROMPT = f.read()

# ----------------------------------------------
# 3) Função para construir o QueryEngine
# ----------------------------------------------
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
    llm = OpenAI(model="gpt-4o-mini", temperature=0.0, max_tokens=1024)

    # Substituir placeholders no prompt
    final_prompt = BASE_PROMPT.replace("{chat_history}", chat_history)

    query_engine = NLSQLTableQueryEngine(
        sql_database=sql_db,
        tables=tables,
        llm=llm,
        sql_prompt_template=final_prompt
    )
    return query_engine

# ----------------------------------------------
# 4) Pós-processamento de SQL (exemplo)
# ----------------------------------------------
def post_process_sql(query: str) -> str:
    """
    Exemplo: forçar LOWER(companyAlsoKnownAs) LIKE em vez de CompanyName.
    Ajuste conforme suas necessidades.
    """
    if not query:
        return query

    # Substituir (alias.)?CompanyName = 'XYZ' => LOWER(companyAlsoKnownAs) LIKE ...
    pattern_eq = r"(?i)WHERE\s+(?:\w+\.)?CompanyName\s*=\s*'([^']+)'"
    def repl_eq(match):
        text_val = match.group(1)
        return f"WHERE LOWER(companyAlsoKnownAs) LIKE LOWER('%{text_val}%')"
    query = re.sub(pattern_eq, repl_eq, query)

    # Substituir (alias.)?CompanyName LIKE 'XYZ'
    pattern_like = r"(?i)WHERE\s+(?:\w+\.)?CompanyName\s+LIKE\s*'([^']+)'"
    def repl_like(match):
        text_val = match.group(1)
        if not text_val.startswith('%'):
            text_val = '%' + text_val
        if not text_val.endswith('%'):
            text_val += '%'
        return f"WHERE LOWER(companyAlsoKnownAs) LIKE LOWER('{text_val}')"
    query = re.sub(pattern_like, repl_like, query)

    return query

# ----------------------------------------------
# 5) Geração de resposta em linguagem natural
# ----------------------------------------------
def generate_natural_answer(llm: OpenAI, question: str, rows, columns):
    if not rows:
        prompt_text = f"""
You are an assistant. The user asked: "{question}"
No data was found in the database.
Answer briefly.
"""
        res = llm.complete(prompt_text)
        return res.text.strip()
    else:
        sample_rows = rows[:3]
        col_str = ", ".join(columns)
        row_text = "\n".join(str(r) for r in sample_rows)

        prompt_text = f"""
The user asked: "{question}"
Database columns: {col_str}
First rows returned: 
{row_text}

Generate a clear explanation summarizing the data
and answering the user's question.
"""
        res = llm.complete(prompt_text)
        return res.text.strip()

# ----------------------------------------------
# 6) Carregar histórico de chat
# ----------------------------------------------
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
            chat_text += f"User: {question}\nAssistant: {response_text}\n"
            simple_history.append(question)
    return chat_text, simple_history

# ----------------------------------------------
# 7) Session state initialization
# ----------------------------------------------
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

# ----------------------------------------------
# 8) Sidebar: histórico de queries
# ----------------------------------------------
st.sidebar.title("Query History")
if len(st.session_state["history"]) == 0:
    st.sidebar.write("No queries yet.")
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
    st.rerun()

# ----------------------------------------------
# 9) Layout principal
# ----------------------------------------------
st.title("Query your data on Pitchbook (with external BASE_PROMPT.md)")

st.markdown("""
<style>
    .stTextArea textarea {
        width: 250% !important;
    }
    .element-container {
        width: 250% !important;
    }
</style>
""", unsafe_allow_html=True)

user_question = st.text_area(
    "Please type your question",
    value=st.session_state.get("current_input", ""),
    key="user_input",
    height=100
)

if st.button("Submit"):
    q_strip = user_question.strip()
    if q_strip:
        with st.spinner("Processing..."):
            # 1) Montar engine e gerar query
            engine_llama = build_query_engine(st.session_state["chat_history"])
            response = engine_llama.query(q_strip)

            raw_sql = response.metadata.get("sql_query", "(Not available)")
            fixed_sql = post_process_sql(raw_sql)

            # 2) Executar query no DB
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

            # 3) Resposta natural
            llm2 = OpenAI(model="gpt-4o-mini", temperature=0.0)
            final_answer = generate_natural_answer(llm2, q_strip, rows, columns)

            # 4) Exibir resultados
            st.markdown("### Natural Language Response")
            st.markdown(final_answer)

            st.markdown("### Generated SQL Query")
            st.markdown(f"```sql\n{fixed_sql}\n```")

            st.markdown("### Returned Data")
            if rows:
                df_result = pd.DataFrame(rows, columns=columns)
                st.dataframe(df_result, use_container_width=True)
            else:
                st.markdown("*No data returned.*")

            # 5) Atualizar histórico
            st.session_state["chat_history"] += f"User: {q_strip}\nAssistant: {final_answer}\n"
            st.session_state["history"].append(q_strip)

            # 6) Registrar logs
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            result_data_str = json.dumps(rows) if rows else ""

            existing_data = []
            if os.path.exists(LOG_FILENAME):
                try:
                    with open(LOG_FILENAME, "r", newline="", encoding="utf-8") as f:
                        reader = csv.DictReader(f)
                        existing_data = list(reader)
                except Exception as e:
                    st.error(f"Error reading log file: {str(e)}")
                    existing_data = []

            new_entry = {
                "timestamp": now_str,
                "question": q_strip,
                "response_text": final_answer,
                "sql_query": fixed_sql,
                "result_data": result_data_str
            }
            existing_data.append(new_entry)

            try:
                with open(LOG_FILENAME, "w", newline="", encoding="utf-8") as f:
                    fieldnames = ["timestamp", "question", "response_text", "sql_query", "result_data"]
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    for rowd in existing_data:
                        sanitized_row = {
                            "timestamp": rowd.get("timestamp", ""),
                            "question": rowd.get("question", ""),
                            "response_text": rowd.get("response_text", ""),
                            "sql_query": rowd.get("sql_query", ""),
                            "result_data": rowd.get("result_data", "")
                        }
                        writer.writerow(sanitized_row)
            except Exception as e:
                st.error(f"Error saving to log file: {str(e)}")

            print(f"Query logged at {now_str}: {fixed_sql}")
            st.session_state["current_input"] = ""
    else:
        st.warning("Please type a question before submitting.")
