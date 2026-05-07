import os

from langchain_classic import hub
from langchain_core.output_parsers import StrOutputParser
from langsmith import Client

from llm import llm

# os.environ["dangerously_pull_public_prompt"] = "true"
#
#
# prompt = hub.pull('rlm/rag-prompt')

client = Client()

# https://smith.langchain.com/hub/rlm/rag-prompt?organizationId=b09fa91a-f7d2-4fb7-b5f6-e9bd4b8a8fbd
prompt = client.pull_prompt("rlm/rag-prompt", dangerously_pull_public_prompt=True)


generation_chain = prompt | llm | StrOutputParser()


if __name__ == "__main__":
    print(prompt)
