# Pitchbook Query App

This repository contains a **Streamlit** application that allows users to query data from a **Pitchbook**-style database using natural language. The app utilizes OpenAI's language model for natural language understanding and SQL query generation, with advanced handling for company name lookups and chat session memory.

## Features

1. **Natural Language Querying**:
   - Users can input queries in plain language, such as:
     - *"What are the top 5 companies founded in 2015?"*
     - *"Tell me about Wildlife"*
   - The app translates these queries into SQL and executes them against a SQLite database.

2. **Advanced SQL Generation**:
   - Automatically uses `LIKE` and `LOWER` for case-insensitive company name searches in the `companyAlsoKnownAs` column.
   - Post-processes SQL queries to ensure compliance with database schema and query optimization.

3. **Chat Memory**:
   - The app retains chat history for consistent and contextual responses.
   - Chat history is displayed in a sidebar for easy reference.

4. **Logging**:
   - All queries, responses, and results are saved to a CSV file (`query-logs.csv`) for auditing and debugging.

5. **Dynamic Prompting**:
   - The app uses a base prompt that incorporates the database schema, chat history, and user query for context-aware SQL generation.

## Technologies Used

- **Python**
- **Streamlit** for the web interface
- **SQLAlchemy** for database interactions
- **LlamaIndex** for integrating OpenAI's language model
- **OpenAI API** for GPT-powered query generation

## Prerequisites

1. Python 3.12 or later.
2. Dependencies listed in `requirements.txt` (see installation instructions below).
3. A valid OpenAI API Key.

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd <repository-folder>
```

### 2. Install Dependencies

Create a virtual environment and install the required Python packages:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Export OpenAI API Key

Set your OpenAI API Key as an environment variable:

```bash
export OPENAI_API_KEY="your-openai-api-key"
```

### 4. Prepare the Database

Ensure the SQLite database (`local_pitchbook.db`) exists in the root directory. If not, follow these steps:

1. Populate the database with your schema and data.
2. Confirm the database matches the schema used in the app.

### 5. Run the Application

Launch the Streamlit app:

```bash
streamlit run step3_app_streamlit.py
```

### 6. Access the App

Visit `http://localhost:8501` in your browser to interact with the application.

## How It Works

1. **Query Processing**:
   - User inputs a natural language question.
   - The app uses OpenAI's GPT model to generate a corresponding SQL query.
   - Post-processing ensures company name lookups are done using `LIKE` and `LOWER`.

2. **Database Execution**:
   - The SQL query is executed against the SQLite database.
   - Results are retrieved and displayed in tabular form.

3. **Natural Language Response**:
   - A second GPT call generates a human-readable explanation of the query results.

4. **Logging and History**:
   - Query details are logged in `query-logs.csv`.
   - Chat history is preserved and displayed in the app sidebar.

## File Structure

```plaintext
├── local_pitchbook.db     # SQLite database file
├── query-logs.csv         # Log file for query history
├── step3_app_streamlit.py # Main Streamlit application script
├── requirements.txt       # Python dependencies
```

## Key Features in Detail

### Dynamic SQL Querying
- The app ensures robust SQL generation with handling for:
  - Case-insensitive company lookups.
  - Use of `LIKE` for partial matches.

### Chat Memory
- The chat history ensures continuity and context-awareness for multi-step queries.

### Logging
- Comprehensive logging tracks user inputs, SQL queries, responses, and results for auditing.

## Troubleshooting

### Common Issues

1. **API Key Not Set**:
   - Ensure the `OPENAI_API_KEY` environment variable is correctly set.

2. **Database Not Found**:
   - Verify `local_pitchbook.db` exists in the project directory.

3. **Dependency Errors**:
   - Ensure all packages in `requirements.txt` are installed in your virtual environment.

4. **Streamlit Version**:
   - The app is tested with Streamlit version `1.41.1`. Ensure compatibility.

## Future Enhancements

- Add support for multiple databases.
- Enhance error handling and user feedback.
- Integrate visualization for query results.

---

For any issues or feature requests, feel free to open an issue in the repository.
