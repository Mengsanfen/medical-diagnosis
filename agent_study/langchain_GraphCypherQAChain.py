from langchain.graphs import Neo4jGraph
from langchain.chains import GraphCypherQAChain
from langchain_openai.chat_models.base import BaseChatOpenAI
from dotenv import load_dotenv
load_dotenv()
llm = BaseChatOpenAI(
    model="deepseek-chat",
    openai_api_base='https://api.deepseek.com')
graph = Neo4jGraph(
    'bolt://localhost:7687',
    'neo4j',
)

chain = GraphCypherQAChain.from_llm(
    llm = llm,
    graph = graph,
    verbose = True
)

result = chain.run('How many doctors are there in the graph?')