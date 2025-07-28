# rag_engine.py
import os
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ibm import WatsonxEmbeddings, WatsonxLLM
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from langchain.chains import RetrievalQA

# Load env vars
WATSONX_API_KEY = os.getenv("WATSONX_API_KEY")
WATSONX_REGION = os.getenv("WATSONX_REGION")
PROJECT_ID = os.getenv("PROJECT_ID")

# Load and split your documents (replace this with your real docs later)
def load_documents():
    loader = TextLoader("state_of_the_union.txt")  # or your own file
    docs = loader.load()
    splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    return splitter.split_documents(docs)

# Build embedding + Chroma vector DB
def get_retriever():
    embeddings = WatsonxEmbeddings(
        model_id="sentence-transformers/all-minilm-l6-v2",
        url=WATSONX_REGION,
        apikey=WATSONX_API_KEY,
        project_id=PROJECT_ID
    )
    texts = load_documents()
    docsearch = Chroma.from_documents(texts, embeddings)
    return docsearch.as_retriever()

# Setup LangChain LLM
def get_llm():
    return WatsonxLLM(
        model_id="meta-llama/llama-3-2-3b-instruct",
        url=WATSONX_REGION,
        apikey=WATSONX_API_KEY,
        project_id=PROJECT_ID,
        params={
            GenParams.DECODING_METHOD: "greedy",
            GenParams.MAX_NEW_TOKENS: 300
        }
    )

# Final callable function for Flask
def ask_with_rag(user_query):
    retriever = get_retriever()
    llm = get_llm()
    qa_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever)
    result = qa_chain.invoke(user_query)
    return result["result"]
