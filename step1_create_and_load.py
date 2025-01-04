# step1_create_and_load.py

# CRIAR TABELAS E CARREGAR DADOS DE CSVs PARA UM BANCO LOCAL (SQLite)
# Este script cria tabelas no SQLite e carrega dados de CSVs para cada tabela do PitchBook.


import os
import pandas as pd
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    String,
    Integer,
    Float,
    Date,
    ForeignKey
)
from sqlalchemy.dialects.sqlite import DATE as SQLITE_DATE

# ----------------------------------------------------------------------
# 1) Configurações iniciais
# ----------------------------------------------------------------------
# Nome do arquivo do banco local (SQLite). Se preferir, use ":memory:".
DB_FILENAME = "local_pitchbook.db"
CSV_FOLDER = "UPLOADVENTURES_20241216"  # Pasta onde estão os CSVs

# Cria engine e Metadata
engine = create_engine(f"sqlite:///{DB_FILENAME}", echo=False)
metadata_obj = MetaData()

# ----------------------------------------------------------------------
# 2) Definição das Tabelas (Schema)
# ----------------------------------------------------------------------
"""
Para simplificar, vamos:
 - Usar String sem tamanho fixo (ou com um limite genérico).
 - Atribuir primary_key onde faz sentido (p. ex., CompanyID na tabela principal).
 - Definir RowID como PK nas tabelas de relação, quando existir.
 - Inferir foreign keys (por exemplo, CompanyID => company.CompanyID).
 - Usar Float para colunas do tipo double.
 - Usar Date (ou String) para colunas de data, lembrando que no SQLite
   isso será tratado como TEXT, mas vamos manter a semântica em SQLAlchemy.
"""

company = Table(
    "company",
    metadata_obj,
    Column("CompanyID", String, primary_key=True),
    Column("CompanyName", String),
    Column("CompanyAlsoKnownAs", String),
    Column("CompanyFormerName", String),
    Column("CompanyLegalName", String),
    Column("Description", String),
    Column("Keywords", String),
    Column("CompanyFinancingStatus", String),
    Column("TotalRaised", Float),
    Column("BusinessStatus", String),
    Column("OwnershipStatus", String),
    Column("Universe", String),
    Column("Website", String),
    Column("Employees", Integer),
    Column("Exchange", String),
    Column("Ticker", String),
    Column("YearFounded", Integer),
    Column("ParentCompany", String),
    Column("ParentCompanyID", String),
    Column("PrimaryIndustrySector", String),
    Column("PrimaryIndustryGroup", String),
    Column("PrimaryIndustryCode", String),
    Column("AllIndustries", String),
    Column("Verticals", String),
    Column("EmergingSpaces", String),
    Column("HQLocation", String),
    Column("HQAddressLine1", String),
    Column("HQAddressLine2", String),
    Column("HQCity", String),
    Column("HQState_Province", String),
    Column("HQPostCode", String),
    Column("HQCountry", String),
    Column("HQPhone", String),
    Column("HQFax", String),
    Column("HQEmail", String),
    Column("HQGlobalRegion", String),
    Column("HQGlobalSubRegion", String),
    Column("LastFinancingDealID", String),
    Column("LastFinancingDate", Date),
    Column("LastFinancingSize", Float),
    Column("LastFinancingSizeStatus", String),
    Column("LastFinancingValuation", Float),
    Column("LastFinancingValuationStatus", String),
    Column("LastFinancingDealType", String),
    Column("LastFinancingDealType2", String),
    Column("LastFinancingDealType3", String),
    Column("LastFinancingDealClass", String),
    Column("LastFinancingDebt", String),
    Column("LastFinancingDebtSize", Float),
    Column("LastFinancingDebtDate", Date),
    Column("LastFinancingStatus", String),
    Column("LastInvestmentInvestorOwnership", String),
    Column("FinancingStatusNote", String),
    Column("FinancingStatusNoteAsOfDate", Date),
    Column("RowID", String),
    Column("LastUpdated", Date),
)

company_employee_history_relation = Table(
    "company_employee_history_relation",
    metadata_obj,
    Column("RowID", String, primary_key=True),
    Column("CompanyID", String, ForeignKey("company.CompanyID")),
    Column("EmployeeCount", Integer),
    Column("Date", Date),
    Column("LastUpdated", Date),
)

company_entity_type_relation = Table(
    "company_entity_type_relation",
    metadata_obj,
    Column("RowID", String, primary_key=True),
    Column("CompanyID", String, ForeignKey("company.CompanyID")),
    Column("EntityType", String),
    Column("IsPrimary", String),
    Column("LastUpdated", Date),
)

company_industry_relation = Table(
    "company_industry_relation",
    metadata_obj,
    Column("RowID", String, primary_key=True),
    Column("CompanyID", String, ForeignKey("company.CompanyID")),
    Column("IndustrySector", String),
    Column("IndustryGroup", String),
    Column("IndustryCode", String),
    Column("IsPrimary", String),
    Column("LastUpdated", Date),
)

company_investor_relation = Table(
    "company_investor_relation",
    metadata_obj,
    Column("RowID", String, primary_key=True),
    Column("CompanyID", String, ForeignKey("company.CompanyID")),
    Column("CompanyName", String),
    Column("InvestorID", String),        # se você tiver a tabela investor, crie FK
    Column("InvestorName", String),
    Column("InvestorStatus", String),
    Column("Holding", String),
    Column("InvestorSince", Date),
    Column("InvestorExit", Date),
    Column("InvestorWebsite", String),
    Column("LastUpdated", Date),
)

company_market_analysis_relation = Table(
    "company_market_analysis_relation",
    metadata_obj,
    Column("RowID", String, primary_key=True),
    Column("CompanyID", String, ForeignKey("company.CompanyID")),
    Column("AnalystCuratedVertical", String),
    Column("Segment", String),
    Column("Subsegment", String),
    Column("ACVReportLastUpdated", Date),
    Column("LastUpdated", Date),
)

company_morningstar_code_relation = Table(
    "company_morningstar_code_relation",
    metadata_obj,
    Column("RowID", String, primary_key=True),
    Column("CompanyID", String, ForeignKey("company.CompanyID")),
    Column("MorningstarCode", String),
    Column("MorningstarDescription", String),
    Column("LastUpdated", Date),
)

company_naics_code_relation = Table(
    "company_naics_code_relation",
    metadata_obj,
    Column("RowID", String, primary_key=True),
    Column("CompanyID", String, ForeignKey("company.CompanyID")),
    Column("NaicsSectorCode", String),
    Column("NaicsSectorDescription", String),
    Column("NaicsIndustryCode", String),
    Column("NaicsIndustryDescription", String),
    Column("LastUpdated", Date),
)

company_sic_code_relation = Table(
    "company_sic_code_relation",
    metadata_obj,
    Column("RowID", String, primary_key=True),
    Column("CompanyID", String, ForeignKey("company.CompanyID")),
    Column("SicCode", String),
    Column("SicDescription", String),
    Column("LastUpdated", Date),
)

company_vertical_relation = Table(
    "company_vertical_relation",
    metadata_obj,
    Column("RowID", String, primary_key=True),
    Column("CompanyID", String, ForeignKey("company.CompanyID")),
    Column("Vertical", String),
    Column("LastUpdated", Date),
)

# Cria todas as tabelas no banco
metadata_obj.create_all(engine)

# ----------------------------------------------------------------------
# 3) Função para carregar dados de CSV para cada tabela
# ----------------------------------------------------------------------
def load_csv_to_table(csv_filename, table_name):
    csv_path = os.path.join(CSV_FOLDER, csv_filename)
    print(f"[INFO] Carregando CSV: {csv_path} → Tabela: {table_name}")

    # Lista de colunas candidatas a data:
    date_candidates = [
        "LastFinancingDate", "LastFinancingDebtDate", "Date",
        "InvestorSince", "InvestorExit", "ACVReportLastUpdated",
        "LastUpdated", "FinancingStatusNoteAsOfDate",
    ]

    # 1) Lemos o CSV apenas 1 linha para descobrir colunas existentes
    df_temp = pd.read_csv(csv_path, dtype=str, nrows=1)
    existing_cols = set(df_temp.columns)

    # 2) Filtramos colunas de data que realmente existem nesse CSV
    actual_parse_dates = [col for col in date_candidates if col in existing_cols]

    # 3) Agora lemos o CSV completo, fazendo parse apenas das datas existentes
    df = pd.read_csv(
        csv_path,
        dtype=str,
        parse_dates=actual_parse_dates,
        keep_default_na=False
    )

    # Converte colunas numéricas (double) para float
    float_cols = [
        "TotalRaised", "LastFinancingSize", "LastFinancingValuation",
        "LastFinancingDebtSize",
    ]
    for col in float_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Converte colunas de int caso necessário
    int_cols = ["Employees", "YearFounded", "EmployeeCount"]
    for col in int_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce", downcast="integer")

    # Salva no banco
    df.to_sql(table_name, con=engine, if_exists="append", index=False)


# ----------------------------------------------------------------------
# 4) Lista de arquivos e carregamento
#    Ajuste os nomes dos CSV conforme a pasta.
# ----------------------------------------------------------------------
CSV_MAPPING = {
    "Company.csv": "company",
    "CompanyEmployeeHistoryRelation.csv": "company_employee_history_relation",
    "CompanyEntityTypeRelation.csv": "company_entity_type_relation",
    "CompanyIndustryRelation.csv": "company_industry_relation",
    "CompanyInvestorRelation.csv": "company_investor_relation",
    "CompanyMarketAnalysisRelation.csv": "company_market_analysis_relation",
    "CompanyMorningstarCodeRelation.csv": "company_morningstar_code_relation",
    "CompanyNaicsCodeRelation.csv": "company_naics_code_relation",
    "CompanySicCodeRelation.csv": "company_sic_code_relation",
    "CompanyVerticalRelation.csv": "company_vertical_relation",
}

def main():
    for csv_file, table_name in CSV_MAPPING.items():
        load_csv_to_table(csv_file, table_name)

    print("[INFO] Carregamento concluído.")

if __name__ == "__main__":
    main()
