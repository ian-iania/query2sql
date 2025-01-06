# Revised Scripts

## Step 1

Create tables

## Step 2

Load tabels

## Step 3

Index

## Step 4 

Fully executable Streamlit script that:

- Loads and uses your BASE_PROMPT.md (which contains all table details and usage logic).
- Maintains chat memory in st.session_state, so each new question has context of prior user/assistant pairs.
- Performs post-processing on the LLM-generated SQL to ensure CompanyName = '...' is converted to LOWER(companyAlsoKnownAs) LIKE ....
- Executes queries on local_pitchbook.db, displaying results in Streamlit.
- Logs each interaction (question, SQL, response) to a CSV.
- This merges all previous functionalities (loading CSV logs, large table logic, NLSQL engine approach) plus the new memory feature.

Prerequisites:

- You already have local_pitchbook.db in the same directory.
- You have BASE_PROMPT.md in the same directory, containing your full instructions/table details (the final version you generated earlier).
- You installed required libraries: streamlit, pandas, sqlalchemy, llama-index, openai, etc.

## BASE_PROMPT.md

File with the BASE_PROMPT for RAG2SQL LlammaIndex framework, to instruct the LLM on how to understand the data and build the queries