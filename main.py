from dotenv import load_dotenv

from app.graph.graph import app

load_dotenv()



if __name__ == "__main__":
    print("Hello Advanced RAG")
    print(app.invoke({'question': '披萨是什么材料做的'}))
