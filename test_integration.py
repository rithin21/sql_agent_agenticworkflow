import sys
sys.path.append('backend')
import os
from typing import Optional
from dotenv import load_dotenv
load_dotenv('backend/.env')

from sqlalchemy import create_engine, text, inspect
from agno.agent import Agent
from agno.models.groq import Groq

# Setup test DB
engine = create_engine('sqlite:///backend/test_agent.db')
with engine.begin() as conn:
    conn.execute(text('DROP TABLE IF EXISTS users'))
    conn.execute(text('CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)'))
    conn.execute(text("INSERT INTO users (name, email) VALUES ('Alice', 'alice@test.com'), ('Bob', 'bob@test.com')"))

CURRENT_ENGINE = engine

def get_schema(table_name: Optional[str] = None):
    """
    Get database schema information.

    Args:
        table_name: The name of the table to get schema for.
                    Omit or pass None to get schema for all tables.

    Returns:
        Schema information including table names, column names and types.
    """
    insp = inspect(CURRENT_ENGINE)
    if table_name:
        return {'table': table_name, 'columns': [{'name': c['name'], 'type': str(c['type'])} for c in insp.get_columns(table_name)]}
    schema = {}
    for t in insp.get_table_names():
        schema[t] = [{'name': c['name'], 'type': str(c['type'])} for c in insp.get_columns(t)]
    return schema

def execute_sql(query: str):
    """Execute a SQL query. Returns rows or success message."""
    print('EXECUTING:', query)
    with CURRENT_ENGINE.begin() as conn:
        result = conn.execute(text(query))
        if result.returns_rows:
            columns = result.keys()
            rows = [dict(zip(columns, row)) for row in result.fetchall()]
            return {'type': 'table', 'data': rows}
    return {'type': 'message', 'data': 'Query executed successfully'}

agent = Agent(
    model=Groq(id='llama-3.3-70b-versatile', api_key=os.getenv('GROQ_API_KEY'), temperature=0.0),
    tools=[get_schema, execute_sql],
    instructions=(
        'You are a SQL assistant. '
        'To list all tables, call get_schema() with no arguments. '
        'To get a specific table schema, call get_schema(table_name="<name>"). '
        'To query data, call execute_sql(query="<sql>"). '
        'ALWAYS use a tool. Never answer from memory.'
    ),
    markdown=False,
    debug_mode=True,
)

print('=== Test 1: schema query ===')
r = agent.run('What tables are in the database?')
print('content:', r.content)
print('messages count:', len(r.messages) if r.messages else 0)
# Print tool-related messages
if r.messages:
    for m in r.messages:
        print(f'  msg role={getattr(m,"role","?")}, content_type={type(getattr(m,"content",None)).__name__}')

print('\n=== Test 2: data query ===')
r2 = agent.run("Find Alice's email", session_id='test-session-2')
print('content:', r2.content)
