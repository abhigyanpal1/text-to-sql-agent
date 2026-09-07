# 'os' lets us read environment variables (like API keys) from the system.this imports Python's built-in operating system library
import os
# loads secret variables from a .env file into the program's environment
from dotenv import load_dotenv
# chromadb is our vector store — it stores and searches embeddings
import chromadb
# embedding_functions helps us convert text descriptions into embeddings
from chromadb.utils import embedding_functions
# importing the 12 table descriptions we wrote in schema_descriptions.py
from schema_descriptions import schema_descriptions

# actually reads the .env file and makes the API key available to the program
load_dotenv()




#Chunk 2 — connecting ChromaDB with Hugging face embeddings



# creates a free, local embedding function using a small open-source model
# this model converts text into vectors without needing any API key
"""all-MiniLM-L6-v2 is the actual name of a pre-trained model that lives on HuggingFace (a platform that hosts open-source AI models, similar to how GitHub hosts code). This specific model is popular because it's small (fast, lightweight) but still produces good quality embeddings — a good tradeoff for a learning project like this.
When you run your code for the first time, it will automatically download this model (a few hundred MB) from HuggingFace onto your machine. After that first download, it runs completely locally — no internet needed, no API key, no cost."""
embedding_function = embedding_functions.DefaultEmbeddingFunction()
#  creates a ChromaDB client that stores data in a local folder called 'chroma_db'
client = chromadb.PersistentClient(path = "./chroma_db")

# creates (or loads if it already exists) a collection named 'schema_store'
# a collection is like a table specifically for storing embeddings

collection = client.get_or_create_collection(name = "schema_store",
                                             embedding_function = embedding_function)





#Chunk 3 — Storing the table descriptions as embeddings.


# converting the dictionary into two separate lists ChromaDB expects:
# one list of table names (used as IDs), one list of descriptions (text to embed)

table_names = list(schema_descriptions.keys())
table_texts = list(schema_descriptions.values())


# adds all 12 entries into the collection in a single call
# chromadb automatically converts each description into an embedding using
# the embedding_function we set up earlier

collection.add(
    ids = table_names,
    documents = table_texts
)

#One important thing to understand: if you run this script multiple times, it'll try to add the same IDs again, which can cause errors or duplicates. For now, add this print statement at the end so you can confirm it worked:

print(f"Added {collection.count()} tables to the vector store.")






#Chunk 4 — The actual retrieval function.





"""
get_relevant_tables(question, n_results=3, distance_threshold=0.8)

Retrieves the most semantically relevant tables from ChromaDB for a given
natural language question.

How it works:
- ChromaDB embeds the question using the same embedding function used to
  store the table descriptions, then finds the closest matches using
  cosine similarity (lower distance = more similar)

- ChromaDB is designed to handle multiple questions at once, so it always
  returns nested lists even for a single question. The [0] unwraps the
  outer layer to get flat lists we can actually iterate over.

- zip(ids, documents, distances) stitches the three separate lists together
  column by column, so each loop iteration gives us one table's name,
  description, and distance score — all aligned.

- distance_threshold filters out weak matches. Only tables with a distance
  below the threshold are kept, so we don't blindly pass irrelevant tables
  to the LLM just because they were the "least irrelevant" of the batch.

Parameters:
  question           — the user's natural language question
  n_results          — max number of results to fetch from ChromaDB (default 3)
  distance_threshold — cutoff above which results are considered too far
                       away to be relevant (default 0.8)

Returns:
  A list of dicts, each containing 'table', 'description', and 'distance'
"""

# This is the piece that makes it "RAG." Given a user's question, we want to query the collection and get back the most relevant table(s).

def get_relevant_tables(question, n_results = 3, distance_threshold = 0.8):
    # queries the collection using the question text
    # chromadb embeds the question the same way it embedded the descriptions,
    # then finds the closest matches using vector similarity
    results = collection.query(
        query_texts = [question],
        n_results = n_results
    )

    # extracting the nested lists chromadb returns
    ids = results["ids"][0]
    documents = results["documents"][0]
    distances = results["distances"][0]

    # only keep tables whose distance is below our threshold (i.e. genuinely relevant)
    relevant_tables = []
    for table_name, description, distance in zip(ids, documents, distances):
        if distance <= distance_threshold:
            relevant_tables.append({
                "table": table_name,
                "description": description,
                "distance": distance
            })
    return relevant_tables

"""Why 3 instead of 1? Some questions span multiple tables. For example, "show me orders with their payment status" genuinely needs both orders AND payments. If we only fetched 1, we'd miss that. But if we fetched all 12, we'd defeat the whole purpose of RAG — sending irrelevant tables to the LLM. 3 is a reasonable middle ground for a project like this."""

if __name__ == "__main__":
    test_questions = ["Show me all the orders that haven't been delivered yet",
                      "Which products have the best reviews?",
                      "What is in a customer's cart right now?"
                    ]
    
    for question in test_questions:
        print(f"Question: {question}")
        print("-" * 60)
        results = get_relevant_tables(question)
        for r in results:
            print(f"Table: {r['table']} | Distance: {r['distance']:.3f}")
            print(f"Description: {r['description']}")
            print()


