# Compare LLMs with Fast Dash and LangChain

Template to compare LLM responses with Fast Dash and LangChain. LangChain has many direct closed-source LLM integrations and it supports open-source integrations through Together AI.

## Running this app

Clone this repository and create a new virtual environment with the dependencies from requirements.txt

Include your API keys in a `.env` file as shown below.

```
OPENAI_API_KEY="sk-xx"
ANTHROPIC_API_KEY="sk-xx"
TOGETHER_API_KEY="xx"
```

## Change LLMs

Adding a new LLM is very easy.

1. Create a new variable in the function `streaming_responses_with_fast_dash`.
2. Write a new function that uses LangChain to stream responses with this new LLM.
3. Add streaming from this new function to your app `add_streaming(app, <your_function>, n)`.
