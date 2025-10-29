import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from search import search_prompt
import argparse
load_dotenv()

def main():

    for k in ("GOOGLE_API_KEY",
              "DATABASE_URL",
              "PG_VECTOR_COLLECTION_NAME",
              "PDF_PATH"):
        if not os.getenv(k):
            raise RuntimeError(f"Environment variable {k} is not set")

    parser = argparse.ArgumentParser(description="Chat CLI")
    parser.add_argument('-q', '--user-question', help='Pergunta do usuário', required=False)
    args = parser.parse_args()
    user_question = args.user_question
    if not user_question:
        try:
            user_question = input("Qual sua pergunta?\n").strip()
        except EOFError:
            user_question = None

    contextualized_prompt = search_prompt(question=user_question)

    # print(f"Pergunta recebida: {user_question}")
    # print(f"contextualized_prompt: {contextualized_prompt}")

    model = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0)
    response = model.invoke(contextualized_prompt)

    print(f"Resposta: {response.content}")

if __name__ == "__main__":
    main()