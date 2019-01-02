# Load with %load SQL.py
import pandas as pd
import os
import pyodbc

pyodbc.lowercase = True
pd.set_option('max_columns', 180)
pd.set_option('max_rows', 500)
pd.set_option('max_colwidth', 5000)

# These two functions are just dictionaries to quickly get the server and db names that are hard to remember
def get_db_name(alias):
    databases = {
        'quant': 'QuantDB',
        'cust': 'CUSTDM_10012018',
        'loan': 'RDM_loan'
    }

    if alias in databases:
        return databases[alias]
    else:
        return alias

def get_server_name(alias):
    servers = {
        'quant': 'DC1Q2PSQLFE1V',
        'sand': 'vdbedcisandbox',
        'vision': 'vdbeaglevision'
    }

    if alias in servers:
        return servers[alias]
    else:
        return alias

# Run commands, like dropping temp tables
# run_command("IF OBJECT_ID('tempdb..##temp_table','U') IS NOT NULL DROP TABLE ##temp_table;")
def run_command(c, database='QuantDB', server='DC1Q2PSQLFE1V'):
    database = get_db_name(database)
    server = get_server_name(server)

    with pyodbc.connect(
                        "Driver={SQL Server};"
                        f"Server={server};"
                        f"Database={database};",
                        autocommit=True
                     ) as conn:
        crsr = conn.cursor()
        crsr.execute(c)

# Run query through Pandas
def run_query(q, database='QuantDB', server='DC1Q2PSQLFE1V'):
    database = get_db_name(database)
    server = get_server_name(server)

    with pyodbc.connect(
                        "Driver={SQL Server};"
                        f"Server={server};"
                        f"Database={database};",
                        autocommit=True
                     ) as conn:
        return pd.read_sql(q, conn)

# Show all tables in database
def show_tables(database='QuantDB', server='DC1Q2PSQLFE1V'):

    q = """
    SELECT
        name
    FROM SYSOBJECTS
    WHERE xtype = 'U'
    ORDER BY 1;
    """
    return run_query(q=q, database=database, server=server)

# Search for columns in database and return tables they belong to
def find_cols(search_terms, database='QuantDB', server='DC1Q2PSQLFE1V'):

    q = f"""
    SELECT
        c.name column_name,
        t.name table_name
    FROM sys.columns c
    INNER JOIN sys.tables t ON c.object_id = t.object_id
    WHERE c.name LIKE '%{search_terms[0]}%'
    """

    for term in search_terms[1:]:
        q += f" AND c.name LIKE '%{term}%'"
    q += ";"

    return run_query(q=q, database=database, server=server)

# Search for tables in database
def find_tables(search_terms, database='QuantDB', server='DC1Q2PSQLFE1V'):

    q = f"""
    SELECT
        name table_name
    FROM sys.tables
    WHERE name LIKE '%{search_terms[0]}%'
    """

    for term in search_terms[1:]:
        q += f" AND c.name LIKE '%{term}%'"
    q += ";"

    return run_query(q=q, database=database, server=server)

# Search for definition of column in data dictionary
def get_def(search_term, database="RDM", server='vdbedcisandbox'):

    q = f"""
    SELECT
        RDM_COLUMN_NAME column_name,
        RDM_TABLE_NAME table_name,
        RDM_BUSINESS_DEFINITION definition
    FROM Data_Dictionary
    WHERE RDM_COLUMN_NAME LIKE '%{search_term}%';
    """

    return run_query(q=q, database=database, server=server)

# Take a peak at the first couple of rows in a table
def head(table_name, rows=5, database='QuantDB', server='DC1Q2PSQLFE1V'):

    rows = str(rows)
    q = f"""
    SELECT TOP {rows}
        *
    FROM {table_name};
    """

    return run_query(q=q, database=database, server=server)

# Get list of columns from table
def get_cols(table_name, database='QuantDB', server='DC1Q2PSQLFE1V'):

    q = f"""
    SELECT TOP 1
        *
    FROM {table_name};
    """

    return run_query(q=q, database=database, server=server).columns.tolist()

# Make a temp table with this class
# loan_sample = TempTable("SELECT TOP 10 * INTO ##temp_table FROM loan;")
# loan_sample.close() when done
class TempTable:
    def __init__(self, c, database='QuantDB', server='DC1Q2PSQLFE1V'):
        database = get_db_name(database)
        server = get_server_name(server)
        self.conn = pyodbc.connect(
                                    "Driver={SQL Server};"
                                    f"Server={server};"
                                    f"Database={database};",
                                    autocommit=True
                                    )
        crsr = self.conn.cursor()
        crsr.execute(c)
        crsr.close()

    def close(self):
        self.conn.close()