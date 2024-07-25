from fast_dash import FastDash, dmc

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_together import ChatTogether

from dotenv import load_dotenv
load_dotenv()

import time

from utils import derive_streaming_dash_app, add_streaming

# Define a prompt globally
prompt = ChatPromptTemplate.from_template("You are a helpful and kind AI assistant. Respond in less than 100 words. {user_prompt}")


# Define a dummy Fast Dash app. We only need the automated layout
# This app currenrly has a single string input and a single string output, but can be easily modified

response_component = dmc.Text(ta="left", size="lg")

def streaming_responses_with_fast_dash(prompt: str) -> (response_component,
                                                        response_component,
                                                        response_component):
    "Template for streaming responses with Fast Dash and LangChain"
    gpt_4_turbo = gpt_4o = llama_3_1_7B = "None"
    return gpt_4_turbo, gpt_4o, llama_3_1_7B

app = FastDash(streaming_responses_with_fast_dash, theme="sandstone")
app = derive_streaming_dash_app(app)


# Streaming function 1
def prompt_gpt_4_turbo(user_prompt):

    model = ChatOpenAI(model="gpt-4-turbo", temperature=0)
    parser = StrOutputParser()

    chain = prompt | model | parser

    return chain.stream({"user_prompt": user_prompt})

def prompt_gpt_4_turbo(user_prompt):

    model = ChatOpenAI(model="gpt-4o", temperature=0)
    parser = StrOutputParser()

    chain = prompt | model | parser

    return chain.stream({"user_prompt": user_prompt})


def prompt_llama3_1(user_prompt):

    model = ChatTogether(model="meta-llama/Llama-3-70b-chat-hf")
    parser = StrOutputParser()

    chain = prompt | model | parser
    
    return chain.stream({"user_prompt": user_prompt})


# Enable streaming in the app
add_streaming(app, prompt_gpt_4_turbo, 1)
add_streaming(app, prompt_gpt_4_turbo, 2)
add_streaming(app, prompt_llama3_1, 3)


if __name__ == "__main__":
    app.run(port=8080)