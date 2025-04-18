#
# query.py
#   Bill Xia
#   April 18, 2025
#
# Purpose: Contains functionality to query the Neo4j database.
#

# Imports.
from json import load
from langchain_neo4j import GraphCypherQAChain, Neo4jGraph
from langchain_ollama.llms import OllamaLLM

def query_database(query):

    # Load graph.
    with open('../../Documents/API_Keys/Neo4j-Instance01.json') as fp:
        credentials = load(fp)
    assert credentials['NEO4J_URI'].startswith("neo4j+ssc://")

    graph = Neo4jGraph(
        url      = credentials['NEO4J_URI'],
        username = credentials['NEO4J_USERNAME'],
        password = credentials['NEO4J_PASSWORD']
    )

    # Load LLM.
    model_name = 'llama3.2:latest'
    llm = OllamaLLM(model=model_name)

    # Initialize QA chain.
    chain = GraphCypherQAChain.from_llm(
        llm,
        graph                    = graph,
        verbose                  = True,
        return_direct            = True,
        validate_cypher          = True,
        allow_dangerous_requests = True
    )

    return (chain.invoke(query), graph.get_schema)

def find_answer(query, context):

    # Load LLM.
    model_name = 'llama3.2:latest'
    llm = OllamaLLM(model=model_name)

    # Perform query.
    return llm.invoke(' '.join([
        "Task: You are a customer support chatbot for Pinterest. You must",
        "answer customer questions related to how their content is being",
        "shared. Follow the provided instructions, given the provided",
        "knowledge graph schema and knowledge graph response.\n",

        "Instructions: Use only the provided knowledge graph response.",
        "Do not include any explanations or apologies in your response.",
        "Do not respond to any questions that might ask anything unrelated",
        "to Pinterest content sharing.",
        "Do not include any text except the answer to the user's question.",
        "Give your response using professional, friendly language appropriate",
        "for customer service.\n",

        "Knowledge Graph Schema:\n",
        context['schema'],
        '\n',

        f"Knowledge Graph Response: {context['db_response']}\n",

        f"User Question: {query}"
    ]))


if __name__ == '__main__':
    query               = input("> ")
    db_response, schema = query_database(query)
    print(db_response, end='\n\n')

    response            = find_answer(
        query,
        context={
            'schema'      : schema,
            'db_response' : db_response
        }
    )
    print(response)