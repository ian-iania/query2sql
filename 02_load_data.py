# 02_load_data.py

"""
Script para inserir (carregar) dados das tabelas definidas no step1_create_tables.py.
Pressupõe-se que as tabelas já foram criadas e estão vazias (caso tenhamos rodado create_schema(drop_existing=True)).

Fluxo principal:
1) Mapeia cada arquivo CSV a uma tabela no DB.
2) Lê os CSVs (usando csv.DictReader).
3) Faz o de-para (CSV columns -> Tabela columns) conforme MAPs.
4) Executa INSERT via SQLAlchemy, possivelmente em blocos (chunks) se necessário.

Por padrão, não faz DELETE, pois assumimos que as tabelas já estão vazias.
"""

import csv
import os
from sqlalchemy import create_engine, text

# -----------------------------------------------------
# 1) Configurações / Paths
# -----------------------------------------------------
DB_FILENAME = "local_pitchbook.db"
UPLOAD_FOLDER = "UPLOADVENTURES_20241216"  # pasta onde estão os CSVs

engine = create_engine(f"sqlite:///{DB_FILENAME}", echo=False)

# -----------------------------------------------------
# 2) Mapeamento de "arquivo CSV" -> "tabela no BD"
# -----------------------------------------------------
CSV_TO_TABLE_MAP = {
    "Company.csv":                         "company",
    "CompanyEmployeeHistoryRelation.csv":  "company_employee_history_relation",
    "CompanyEntityTypeRelation.csv":       "company_entity_type_relation",
    "CompanyIndustryRelation.csv":         "company_industry_relation",
    "CompanyInvestorRelation.csv":         "company_investor_relation",
    "CompanyMarketAnalysisRelation.csv":   "company_market_analysis_relation",
    "CompanyMorningstarCodeRelation.csv":  "company_morningstar_code_relation",
    "CompanyNaicsCodeRelation.csv":        "company_naics_code_relation",
    "CompanySicCodeRelation.csv":          "company_sic_code_relation",
    "CompanyVerticalRelation.csv":         "company_vertical_relation",
}

# -----------------------------------------------------
# 3) Mapeamento de colunas CSV -> colunas do DB
#    (um dicionário por tabela)
# -----------------------------------------------------
TABLE_COLUMN_MAP = {
    "company": {
        "CompanyID": "CompanyID",
        "CompanyName": "CompanyName",
        "CompanyAlsoKnownAs": "CompanyAlsoKnownAs",
        "CompanyFormerName": "CompanyFormerName",
        "CompanyLegalName": "CompanyLegalName",
        "Description": "Description",
        "Keywords": "Keywords",
        "CompanyFinancingStatus": "CompanyFinancingStatus",
        "TotalRaised": "TotalRaised",
        "BusinessStatus": "BusinessStatus",
        "OwnershipStatus": "OwnershipStatus",
        "Universe": "Universe",
        "Website": "Website",
        "Employees": "Employees",
        "Exchange": "Exchange",
        "Ticker": "Ticker",
        "YearFounded": "YearFounded",
        "ParentCompanyID": "ParentCompanyID",
        "PrimaryIndustrySector": "PrimaryIndustrySector",
        "PrimaryIndustryGroup": "PrimaryIndustryGroup",
        "PrimaryIndustryCode": "PrimaryIndustryCode",
        "AllIndustries": "AllIndustries",
        "Verticals": "Verticals",
        "EmergingSpaces": "EmergingSpaces",
        "HQLocation": "HQLocation",
        "HQAddressLine1": "HQAddressLine1",
        "HQAddressLine2": "HQAddressLine2",
        "HQCity": "HQCity",
        "HQState_Province": "HQState_Province",
        "HQPostCode": "HQPostCode",
        "HQCountry": "HQCountry",
        "HQPhone": "HQPhone",
        "HQFax": "HQFax",
        "HQEmail": "HQEmail",
        "LastFinancingSize": "LastFinancingSize",
        "LastFinancingStatus": "LastFinancingStatus",
        "RowID": "RowID",
        "LastUpdated": "LastUpdated",
    },
    "company_employee_history_relation": {
        "RowID": "RowID",
        "CompanyID": "CompanyID",
        "EmployeeCount": "EmployeeCount",
        "Date": "Date",
        "LastUpdated": "LastUpdated",
    },
    "company_entity_type_relation": {
        "RowID": "RowID",
        "CompanyID": "CompanyID",
        "EntityType": "EntityType",
        "IsPrimary": "IsPrimary",
        "LastUpdated": "LastUpdated",
    },
    "company_industry_relation": {
        "RowID": "RowID",
        "CompanyID": "CompanyID",
        "IndustrySector": "IndustrySector",
        "IndustryGroup": "IndustryGroup",
        "IndustryCode": "IndustryCode",
        "IsPrimary": "IsPrimary",
        "LastUpdated": "LastUpdated",
    },
    "company_investor_relation": {
        "RowID": "RowID",
        "CompanyID": "CompanyID",
        "CompanyName": "CompanyName",
        "InvestorID": "InvestorID",
        "InvestorName": "InvestorName",
        "InvestorStatus": "InvestorStatus",
        "Holding": "Holding",
        "InvestorSince": "InvestorSince",
        "InvestorExit": "InvestorExit",
        "InvestorWebsite": "InvestorWebsite",
        "LastUpdated": "LastUpdated",
    },
    "company_market_analysis_relation": {
        "RowID": "RowID",
        "CompanyID": "CompanyID",
        "AnalystCuratedVertical": "AnalystCuratedVertical",
        "Segment": "Segment",
        "Subsegment": "Subsegment",
        "ACVReportLastUpdated": "ACVReportLastUpdated",
        "LastUpdated": "LastUpdated",
    },
    "company_morningstar_code_relation": {
        "RowID": "RowID",
        "CompanyID": "CompanyID",
        "MorningstarCode": "MorningstarCode",
        "MorningstarDescription": "MorningstarDescription",
        "LastUpdated": "LastUpdated",
    },
    "company_naics_code_relation": {
        "RowID": "RowID",
        "CompanyID": "CompanyID",
        "NaicsSectorCode": "NaicsSectorCode",
        "NaicsSectorDescription": "NaicsSectorDescription",
        "NaicsIndustryCode": "NaicsIndustryCode",
        "NaicsIndustryDescription": "NaicsIndustryDescription",
        "LastUpdated": "LastUpdated",
    },
    "company_sic_code_relation": {
        "RowID": "RowID",
        "CompanyID": "CompanyID",
        "SicCode": "SicCode",
        "SicDescription": "SicDescription",
        "LastUpdated": "LastUpdated",
    },
    "company_vertical_relation": {
        "RowID": "RowID",
        "CompanyID": "CompanyID",
        "Vertical": "Vertical",
        "LastUpdated": "LastUpdated",
    },
}

# -----------------------------------------------------
# 4) Função para inserir um CSV em uma tabela
# -----------------------------------------------------
def load_csv_to_table(csv_filename: str, table_name: str):
    """
    Lê um CSV (csv_filename) e insere na tabela table_name.
    Assume que TABLE_COLUMN_MAP[table_name] define o mapeamento CSV->DB columns.

    :param csv_filename: nome do arquivo CSV (ex: "Company.csv")
    :param table_name: nome da tabela (ex: "company")
    """
    csv_path = os.path.join(UPLOAD_FOLDER, csv_filename)

    # 1) Recupera o dicionário de mapeamento para a tabela
    col_map = TABLE_COLUMN_MAP.get(table_name)
    if not col_map:
        print(f"[WARNING] Não existe mapeamento de colunas para a tabela '{table_name}'. Ignorando.")
        return

    # 2) Ler o CSV em uma lista de dicionários
    records = []
    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                print(f"[WARNING] CSV '{csv_filename}' sem cabeçalho ou vazio.")
                return

            for row in reader:
                mapped_row = {}
                for csv_col, db_col in col_map.items():
                    # Lê o valor do CSV e atribui à coluna do DB
                    mapped_row[db_col] = row.get(csv_col)
                records.append(mapped_row)
    except FileNotFoundError:
        print(f"[ERROR] Arquivo CSV '{csv_filename}' não encontrado em '{UPLOAD_FOLDER}'.")
        return

    if not records:
        print(f"[INFO] CSV '{csv_filename}' não possui linhas de dados. Nada a inserir.")
        return

    # 3) Montar o INSERT dinâmico
    columns_db = list(records[0].keys())
    col_names = ", ".join(columns_db)
    col_placeholders = ", ".join([f":{col}" for col in columns_db])

    insert_sql = text(f"""
        INSERT INTO {table_name} ({col_names})
        VALUES ({col_placeholders})
    """)

    # 4) Inserir no DB
    with engine.begin() as conn:
        conn.execute(insert_sql, records)

    print(f"[SUCCESS] Inseridos {len(records)} registros na tabela '{table_name}' a partir do CSV '{csv_filename}'.")


# -----------------------------------------------------
# 5) Função principal para carregar todos os CSVs
# -----------------------------------------------------
def main():
    """
    Percorre CSV_TO_TABLE_MAP e para cada par (arquivo, tabela),
    carrega o CSV na tabela correspondente.
    """
    if not os.path.exists(DB_FILENAME):
        print(f"[ERROR] O banco '{DB_FILENAME}' não foi encontrado. Execute step1_create_tables.py antes.")
        return

    # Valida se a pasta com CSV existe
    if not os.path.exists(UPLOAD_FOLDER):
        print(f"[ERROR] A pasta '{UPLOAD_FOLDER}' não foi encontrada.")
        return

    # Para cada CSV -> Tabela
    for csv_file, table_name in CSV_TO_TABLE_MAP.items():
        print(f"[INFO] Carregando '{csv_file}' -> Tabela '{table_name}'")
        load_csv_to_table(csv_file, table_name)

    print("[SUCCESS] Todos os dados foram carregados com sucesso.")


if __name__ == "__main__":
    main()
