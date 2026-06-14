import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load env from backend
load_dotenv(dotenv_path="backend/.env")

import sys
import sys
sys.path.append("backend")
import main

# Redefine get_schema with a required parameter
def get_schema(table_name: str):
    """
    Get database schema information.

    Args:
        table_name: The name of the table to get schema for. 
                   Pass an empty string "" to get schema for all tables.

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

# Update agent instructions
main.agent.instructions = """
You are a SQL assistant.

When users ask about tables, columns, or schema,
call get_schema. If they ask generally or for all tables, pass table_name="" (empty string).

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

main.CURRENT_ENGINE = engine


print("--- Testing normal chat ---")
resp1 = main.agent.run("Hi, who are you?")
print("Response 1:", resp1.content)

print("\n--- Testing schema query ---")
resp2 = main.agent.run("What tables are in the database?")
print("Response 2:", resp2.content)

print("\n--- Testing data query ---")
resp3 = main.agent.run("Find the email of Alice")
print("Response 3:", resp3.content)

