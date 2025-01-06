# step1_create_tables.py

"""
Schema creation script for Pitchbook database (enriquecido com docstrings).
This script defines and creates all tables and their relationships,
optionally dropping existing tables first.
"""

from sqlalchemy import (
    create_engine, MetaData, Table, Column, String, Integer, Float, Date,
    ForeignKey, Index, Text, Numeric
)
from sqlalchemy.dialects.sqlite import DATE as SQLITE_DATE

# ----------------------------------------------------
# 1. Database configuration
# ----------------------------------------------------
DB_FILENAME = "local_pitchbook.db"
engine = create_engine(f"sqlite:///{DB_FILENAME}", echo=False)
metadata_obj = MetaData()


# ----------------------------------------------------
# 2. Tabela: company
# ----------------------------------------------------
company = Table(
    "company",
    metadata_obj,
    Column("CompanyID", String(20),
           primary_key=True,
           doc="Primary key for the company (PitchBook ID). e.g. '55780-93'"),
    Column("CompanyName", String(255),
           index=True,
           doc="Name of the company. e.g. 'Urban Inc.'"),
    Column("CompanyAlsoKnownAs", Text,
           index=True,
           doc="Other/alternative names for the company (comma-separated). e.g. 'Urban, Inc., Urban Co.'"),
    Column("CompanyFormerName", Text,
           doc="Former official name(s) of the company."),
    Column("CompanyLegalName", String(255),
           doc="Legal registered name of the company."),
    Column("Description", Text,
           doc="Text description of the company's business and offerings."),
    Column("Keywords", Text,
           index=True,
           doc="Keywords describing the business; comma-separated. e.g. 'algorithmic discovery, real estate analytics'"),
    Column("CompanyFinancingStatus", String(50),
           doc="Indicates type of investors backing the company. e.g. 'Venture Capital-backed'"),
    Column("TotalRaised", Numeric(precision=10, scale=2),
           index=True,
           doc="Total capital injected into the company (in millions). e.g. 713 (=$713M)"),
    Column("BusinessStatus", String(50),
           index=True,
           doc="Current operating status. e.g. 'Product Development', 'Operating', 'Closed'"),
    Column("OwnershipStatus", String(50),
           doc="Summary of how the company is held. e.g. 'Privately Held (backing)'."),
    Column("Universe", String(200),
           doc="Broad classification based on investor types or search scope. e.g. 'Venture Capital'"),
    Column("Website", Text,
           doc="Company website URL. e.g. 'http://www.urbaninc.com'"),
    Column("Employees", Integer,
           index=True,
           doc="Current number of employees. e.g. 50"),
    Column("Exchange", String(50),
           doc="Stock exchange if publicly traded. e.g. 'NASDAQ'"),
    Column("Ticker", String(100),
           index=True,
           doc="Stock ticker symbol. e.g. 'UBRN'"),
    Column("YearFounded", Integer,
           index=True,
           doc="Year the company was founded. e.g. 2012"),
    Column("ParentCompanyID", String(20),
           ForeignKey("company.CompanyID"),
           doc="PitchBook ID of the parent company, if any."),
    Column("PrimaryIndustrySector", String(100),
           index=True,
           doc="Broad industry category. e.g. 'Consumer Products and Services (B2C)'"),
    Column("PrimaryIndustryGroup", String(100),
           doc="Industry sub-category. e.g. 'Real Estate Services (B2C)'"),
    Column("PrimaryIndustryCode", String(100),
           doc="Primary industry code. e.g. 'Software'"),
    Column("AllIndustries", Text,
           doc="Comma-separated list of all industries the company operates in."),
    Column("Verticals", Text,
           doc="Comma-separated list of verticals (e.g. 'Mobility, Mobile Health Tech, IoT')."),
    Column("EmergingSpaces", String(255),
           doc="Emerging technology spaces. e.g. 'AI, Machine Learning'"),
    Column("HQLocation", String(100),
           doc="Geographical location or city, country for headquarters."),
    Column("HQAddressLine1", String(100),
           doc="Address line 1 of the HQ."),
    Column("HQAddressLine2", String(100),
           doc="Address line 2 of the HQ."),
    Column("HQCity", String(100),
           index=True,
           doc="City where the company is headquartered. e.g. 'New York'"),
    Column("HQState_Province", String(100),
           doc="State or province of the HQ. e.g. 'NY'"),
    Column("HQPostCode", String(30),
           doc="Postal code for the HQ. e.g. '10003'"),
    Column("HQCountry", String(50),
           index=True,
           doc="Country where the company is headquartered. e.g. 'USA'"),
    Column("HQPhone", String(50),
           doc="Phone number of the company's headquarters. e.g. '+1 (212) 915-xxxx'"),
    Column("HQFax", String(255),
           doc="Fax number of the company's headquarters."),
    Column("HQEmail", String(100),
           doc="Email address for the company's headquarters."),
    Column("LastFinancingSize", Numeric(precision=10, scale=2),
           doc="Value of the most recent financing event (in millions). e.g. 250.0"),
    Column("LastFinancingStatus", String(50),
           doc="Stage or status of the last financing round. e.g. 'Series B'"),
    Column("RowID", String(255),
           unique=True,
           doc="Unique identifier for the row in this CSV. e.g. 'b2a87e536808...'"),
    Column("LastUpdated", Date,
           index=True,
           doc="Date showing the time any data point in this row was last updated. e.g. '2019-01-01'")
)


# ----------------------------------------------------
# 3. Tabela: company_employee_history_relation
# ----------------------------------------------------
company_employee_history_relation = Table(
    "company_employee_history_relation",
    metadata_obj,
    Column("RowID", String(255),
           primary_key=True,
           doc="Unique identifier for this row. e.g. 'b2a87e...'"),
    Column("CompanyID", String(20),
           ForeignKey("company.CompanyID", onupdate="CASCADE", ondelete="CASCADE"),
           index=True,
           doc="Links to company.CompanyID. e.g. '55780-93'"),
    Column("EmployeeCount", Integer,
           index=True,
           doc="Historical count of employees. e.g. 3000"),
    Column("Date", Date,
           index=True,
           doc="Date of the employee count record. e.g. '2013-03-31'"),
    Column("LastUpdated", Date,
           doc="Date showing the time any data point in this row was last updated. e.g. '2019-01-01'")
)


# ----------------------------------------------------
# 4. Tabela: company_entity_type_relation
# ----------------------------------------------------
company_entity_type_relation = Table(
    "company_entity_type_relation",
    metadata_obj,
    Column("RowID", String(255),
           primary_key=True,
           doc="Unique identifier for the row."),
    Column("CompanyID", String(20),
           ForeignKey("company.CompanyID", onupdate="CASCADE", ondelete="CASCADE"),
           index=True,
           doc="Links to company.CompanyID, e.g. '11295-73'"),
    Column("EntityType", String(255),
           index=True,
           doc="Type of entity. e.g. 'Company', 'Non-profit', 'Government'"),
    Column("IsPrimary", String(10),
           doc="Indicates if this entity type is the primary one. e.g. 'Yes' or 'No'"),
    Column("LastUpdated", Date,
           doc="Date showing the time any data point in this row was last updated.")
)


# ----------------------------------------------------
# 5. Tabela: company_industry_relation
# ----------------------------------------------------
company_industry_relation = Table(
    "company_industry_relation",
    metadata_obj,
    Column("RowID", String(255),
           primary_key=True,
           doc="Unique identifier for the row."),
    Column("CompanyID", String(20),
           ForeignKey("company.CompanyID", onupdate="CASCADE", ondelete="CASCADE"),
           index=True,
           doc="Links to company.CompanyID, e.g. '55780-93'"),
    Column("IndustrySector", String(100),
           index=True,
           doc="A broad industry category. e.g. 'Consumer Products and Services (B2C)'"),
    Column("IndustryGroup", String(100),
           index=True,
           doc="A sub-category providing more specific classification. e.g. 'Services (Non-Financial)'"),
    Column("IndustryCode", String(100),
           index=True,
           doc="The primary industry code the company operates in. e.g. 'Real Estate Services (B2C)'"),
    Column("IsPrimary", String(10),
           doc="'Yes' if it's the company's primary industry, 'No' otherwise."),
    Column("LastUpdated", Date,
           doc="Date showing the time any data point in this row was last updated.")
)


# ----------------------------------------------------
# 6. Tabela: company_investor_relation
# ----------------------------------------------------
company_investor_relation = Table(
    "company_investor_relation",
    metadata_obj,
    Column("RowID", String(255),
           primary_key=True,
           doc="Unique identifier for the row."),
    Column("CompanyID", String(20),
           index=True,
           doc="Links to company.CompanyID. e.g. '55780-93'"),
    Column("CompanyName", String(255),
           doc="Name of the company. e.g. 'Compass'"),
    Column("InvestorID", String(20),
           doc="Unique identifier for the investor (PbID). e.g. '13240-18'"),
    Column("InvestorName", String(255),
           doc="Formal name of the investor. e.g. 'Fidelity Investments'"),
    Column("InvestorStatus", String(50),
           doc="Status values: 'Active', 'Former', 'Add-on Sponsor', etc."),
    Column("Holding", String(255),
           doc="Investor's stake in the company. e.g. 'Minority'"),
    Column("InvestorSince", Date,
           doc="Earliest investment date by the investor. e.g. '2013-01-23'"),
    Column("InvestorExit", Date,
           doc="Date of investor exit from target. e.g. '2023-01-23'"),
    Column("InvestorWebsite", Text,
           doc="URL of investor's site. e.g. 'http://www.fidelity.com'"),
    Column("LastUpdated", Date,
           doc="Date showing the time any data point in this row was last updated.")
)


# ----------------------------------------------------
# 7. Tabela: company_market_analysis_relation
# ----------------------------------------------------
company_market_analysis_relation = Table(
    "company_market_analysis_relation",
    metadata_obj,
    Column("RowID", String(255),
           primary_key=True,
           doc="Unique identifier for the row."),
    Column("CompanyID", String(20),
           ForeignKey("company.CompanyID", onupdate="CASCADE", ondelete="CASCADE"),
           index=True,
           doc="Links to company.CompanyID, e.g. '55780-93'"),
    Column("AnalystCuratedVertical", Text,
           index=True,
           doc="Company vertical curated by PitchBook's Emerging Tech Analyst team. e.g. 'Artificial Intelligence & Machine Learning'"),
    Column("Segment", Text,
           index=True,
           doc="Main category grouping companies within a market map. e.g. 'Software'"),
    Column("Subsegment", Text,
           index=True,
           doc="Additional layer of grouping within segments. e.g. 'Software Development Applications'"),
    Column("ACVReportLastUpdated", Text,
           doc="Date/quarter when the analyst curated vertical was last updated. e.g. 'Q2 2023'"),
    Column("LastUpdated", Date,
           doc="Date showing the time any data point in this row was last updated.")
)


# ----------------------------------------------------
# 8. Tabela: company_morningstar_code_relation
# ----------------------------------------------------
company_morningstar_code_relation = Table(
    "company_morningstar_code_relation",
    metadata_obj,
    Column("RowID", String(255),
           primary_key=True,
           doc="Unique identifier for the row."),
    Column("CompanyID", String(20),
           ForeignKey("company.CompanyID", onupdate="CASCADE", ondelete="CASCADE"),
           index=True,
           doc="Links to company.CompanyID, e.g. '55780-93'"),
    Column("MorningstarCode", String(100),
           index=True,
           doc="Morningstar numeric industry classifier. e.g. '31165133'"),
    Column("MorningstarDescription", String(200),
           doc="Text description of the classifier. e.g. 'Software - Application'"),
    Column("LastUpdated", Date,
           doc="Date showing the time any data point in this row was last updated.")
)


# ----------------------------------------------------
# 9. Tabela: company_naics_code_relation
# ----------------------------------------------------
company_naics_code_relation = Table(
    "company_naics_code_relation",
    metadata_obj,
    Column("RowID", String(255),
           primary_key=True,
           doc="Unique identifier for the row."),
    Column("CompanyID", String(20),
           ForeignKey("company.CompanyID", onupdate="CASCADE", ondelete="CASCADE"),
           index=True,
           doc="Links to company.CompanyID, e.g. '55780-93'"),
    Column("NaicsSectorCode", String(20),
           index=True,
           doc="2-digit NAICS sector code. e.g. '51'"),
    Column("NaicsSectorDescription", Text,
           doc="Description for the 2-digit NAICS sector. e.g. 'Information'"),
    Column("NaicsIndustryCode", String(20),
           index=True,
           doc="Up to 6-digit NAICS industry code. e.g. '511210'"),
    Column("NaicsIndustryDescription", Text,
           doc="Description of the 6-digit NAICS code. e.g. 'Software Publishers'"),
    Column("LastUpdated", Date,
           doc="Date showing the time any data point in this row was last updated.")
)


# ----------------------------------------------------
# 10. Tabela: company_sic_code_relation
# ----------------------------------------------------
company_sic_code_relation = Table(
    "company_sic_code_relation",
    metadata_obj,
    Column("RowID", String(255),
           primary_key=True,
           doc="Unique identifier for the row."),
    Column("CompanyID", String(20),
           ForeignKey("company.CompanyID", onupdate="CASCADE", ondelete="CASCADE"),
           index=True,
           doc="Links to company.CompanyID, e.g. '55780-93'"),
    Column("SicCode", String(40),
           index=True,
           doc="Standard Industrial Classification code (4-digit). e.g. '7371'"),
    Column("SicDescription", String(255),
           doc="Text description of the 4-digit SIC code. e.g. 'Services-computer programming services'"),
    Column("LastUpdated", Date,
           doc="Date showing the time any data point in this row was last updated.")
)


# ----------------------------------------------------
# 11. Tabela: company_vertical_relation
# ----------------------------------------------------
company_vertical_relation = Table(
    "company_vertical_relation",
    metadata_obj,
    Column("RowID", String(255),
           primary_key=True,
           doc="Unique identifier for the row."),
    Column("CompanyID", String(20),
           ForeignKey("company.CompanyID", onupdate="CASCADE", ondelete="CASCADE"),
           index=True,
           doc="Links to company.CompanyID, e.g. '55780-93'"),
    Column("Vertical", String(255),
           index=True,
           doc="Classifiers that may span across multiple industries. e.g. 'Real Estate Technology'"),
    Column("LastUpdated", Date,
           doc="Date showing the time any data point in this row was last updated.")
)


# ----------------------------------------------------
# 12. Optional: create indexes to optimize queries
# ----------------------------------------------------
Index('idx_company_search', company.c.CompanyName, company.c.CompanyAlsoKnownAs)
Index('idx_company_metrics', company.c.Employees, company.c.TotalRaised, company.c.YearFounded)
Index('idx_company_location', company.c.HQCountry, company.c.HQCity)
Index('idx_employee_history', company_employee_history_relation.c.CompanyID, company_employee_history_relation.c.Date)
Index('idx_industry_analysis', company_industry_relation.c.CompanyID, company_industry_relation.c.IndustrySector)
Index('idx_market_analysis', company_market_analysis_relation.c.CompanyID, company_market_analysis_relation.c.AnalystCuratedVertical)


# ----------------------------------------------------
# 13. Function to create/drop schema
# ----------------------------------------------------
def create_schema(drop_existing=False):
    """
    Creates all tables in the database.
    If drop_existing=True, it will drop all existing tables before creating them.
    """
    if drop_existing:
        print("[INFO] Dropping existing tables...")
        metadata_obj.drop_all(engine)
        print("[INFO] Existing tables dropped.")

    metadata_obj.create_all(engine)
    print("[SUCCESS] Database schema created successfully")


if __name__ == "__main__":
    # Ajuste conforme necessidade.
    # Por exemplo, "drop_existing=True" para limpar o BD antes de criar o schema.
    create_schema(drop_existing=True)
