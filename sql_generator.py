import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key = os.getenv("ANTHROPIC_API_KEY"))

def build_prompt(question, relevant_tables):
    # format the retrieved tables into readable schema context

    schema_context = ""
    for table in relevant_tables:
        schema_context += f"Table: {table['table']}\n"
        schema_context += f"Description: {table['description']}\n\n"
    
    prompt = f"""You are a SQL expert working with an e-commerce database.
    Given the following schema context, write a SQL query to answer the user's question.

    Schema Context:
    {schema_context}
    Question: {question}
     
    Rules:
    - Return ONLY the SQL query, no explanation
    - Use standard SQL syntax
    - Use proper table and column names from the schema

    SQL Query:"""

    return prompt

def generate_sql(question, relevant_tables):
    prompt = build_prompt(question, relevant_tables)

    # call Claude via Anthropic API
    message = client.messages.create(
        model = "claude-sonnet-4-6",
        max_tokens = 1024,
        messages = [
            {"role": "user", "content": prompt}
        ]
    )

    # extract just the text from the response
    sql_query = message.content[0].text.strip()

    # remove markdown code fences if Claude added them
    sql_query = sql_query.replace("```sql","").replace("```","").strip()
    #print(repr(sql_query))
    return sql_query

"""The messages parameter is how you structure the conversation history you send to Claude. It's a list of turns, where each turn has two things:

role — who is speaking. Either "user" (the human) or "assistant" (Claude)
content — what they said"""


if __name__ == "__main__":
    # import the RAG function built earlier
    from schema_rag import get_relevant_tables

    test_question = "Show me all orders that haven't been delivered yet"

    # step 1 - get relevant tables
    relevant_tables = get_relevant_tables(test_question)

    # step 2 - generate sql
    sql = generate_sql(test_question, relevant_tables)

    print(f"Question: {test_question}")
    print(f"\nGenerated SQL:\n{sql}")