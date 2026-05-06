import os
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.document_loaders import WebBaseLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv(override=True)

os.environ["USER_AGENT"] = "rag-chroma"

urls = [
    "https://lilianweng.github.io/posts/2023-06-23-agent/",
    "https://lilianweng.github.io/posts/2023-03-15-prompt-engineering/",
    "https://lilianweng.github.io/posts/2023-10-25-adv-attack-llm/",
]

# loader
documents_list = [WebBaseLoader(url).load() for url in urls]
documents = [document for item in documents_list for document in item]

# 分块
text_splitter = RecursiveCharacterTextSplitter(chunk_size=250, chunk_overlap=0)

all_splits = text_splitter.split_documents(documents)

print(f"Split blog post into {len(all_splits)} sub-documents.")

embeddings = OpenAIEmbeddings(
    model="text-embedding-bge-m3",
    base_url=os.getenv("openai_base_url"),
    api_key=os.getenv("OPENAI_API_KEY"),
    # 控制 LangChain 是否在发送请求前检查输入文本是否超过模型的 token 上下文长度限制。
    #
    #   - True（默认）：LangChain 会先计算 token 数，超长则自动截断或拆分批次
    #   - False：跳过检查，直接把原文发给 API
    check_embedding_ctx_length=False,
    # dimensions=1024
)
# print(embeddings.embed_documents(["你好 世界"]))

vector_store = Chroma(
    collection_name="rag-chroma",
    embedding_function=embeddings,
    persist_directory=f'{Path(__file__).resolve().parent / ".chromadb"}',
)

#  检索器
retriever = vector_store.as_retriever()


if __name__ == "__main__":
    print(Path(__file__).resolve().parent)
    uuids = [str(uuid4()) for _ in range(len(documents))]

    vector_store.add_documents(documents=documents, ids=uuids)
    print("加载完毕...")
