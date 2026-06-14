import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load env from backend
load_dotenv(dotenv_path="backend/.env")

import sys
sys.path.append("backend")

# Monkey-patch agno function call parser to handle null/None arguments
import agno.utils.functions
original_get_function_call = agno.utils.functions.get_function_call

def patched_get_function_call(name, arguments=None, call_id=None, functions=None):
    if arguments == "null" or arguments is None or arguments == "":
        arguments = "{}"
    return original_get_function_call(name, arguments, call_id, functions)

agno.utils.functions.get_function_call = patched_get_function_call

import main

import sys
sys.path.append("backend")
import main

# Redefine get_schema to have required table_name
def get_schema(table_name: str):
    """
    Get database schema information.

    Args:
        table_name: The table name. Pass an empty string "" to get all tables.

    Returns:
        Schema information including column names and types.
    """
    print(f"CALLING get_schema WITH table_name={repr(table_name)}")
    inspector = main.inspect(main.CURRENT_ENGINE)
    if table_name:
        columns = inspector.get_columns(table_name)
        return {
            "table": table_name,
            "columns": [{"name": col["name"], "type": str(col["type"])} for col in columns]
        }
    schema = {}
    for table in inspector.get_table_names():
        schema[table] = [
            {"name": col["name"], "type": str(col["type"])}
            for col in inspector.get_columns(table)
        ]
    return schema

main.get_schema = get_schema
main.agent.tools[0] = get_schema
main.agent.model.temperature = 0.0

main.agent.instructions = """
You are a SQL assistant.

When users ask about tables, columns, or schema,
call get_schema. If they ask generally or for all tables, you MUST pass table_name="" (empty string).

When users ask for data,
generate SQL and call execute_sql.

Never guess schema information.
Always use tools.
"""



# Create a test sqlite db
engine = create_engine("sqlite:///test_agent.db")
with engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS users"))
    conn.execute(text("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)"))
    conn.execute(text("INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com'), ('Bob', 'bob@example.com')"))
    conn.commit()

# We will test the query function directly which is called by /process_query
# It accepts a QueryRequest object
from pydantic import BaseModel

class QueryRequest(BaseModel):
    prompt: str
    connectionString: str

req_schema = QueryRequest(
    prompt="What tables are in the database?",
    connectionString="sqlite:///test_agent.db"
)

req_data = QueryRequest(
    prompt="Find the email of Alice",
    connectionString="sqlite:///test_agent.db"
)

print("--- Testing API Endpoint: Schema Query ---")
res1 = main.query(req_schema)
print("Response keys:", list(res1.keys()))
print("Answer:", res1.get("answer"))
print("Data:", res1.get("data"))

print("\n--- Testing API Endpoint: Data Query ---")
res2 = main.query(req_data)
print("Response keys:", list(res2.keys()))
print("Answer:", res2.get("answer"))
print("Data:", res2.get("data"))
