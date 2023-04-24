import os
import logging
import openai
from dotenv import load_dotenv

load_dotenv()

CHAT_GPT_WEB_MODEL = "gpt-3.5-turbo"
CHAT_GPT_DEFAULT_API_MODEL = "text-davinci-003"


def get_chatbot_response(
    prompt_text,
    max_tokens=500,
    model=CHAT_GPT_WEB_MODEL,
):
    logging.info(f"Creating chat completion request for model {model}")
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if model == CHAT_GPT_DEFAULT_API_MODEL:
        response = openai.Completion.create(
            engine=CHAT_GPT_DEFAULT_API_MODEL,
            # engine="gpt-3.5-turbo",
            prompt=prompt_text,
            temperature=0.7,
            max_tokens=max_tokens,
            n=1,  # Number of responses you want to generate
            top_p=1,  # Controls the nucleus sampling; 1 means no sampling is applied
            frequency_penalty=0,  # Penalizes new tokens based on their frequency in the dataset
            # presence_penalty=0,  # Penalizes tokens that are generated frequently within a response
            # top_p=1,
            # frequency_penalty=0,
            presence_penalty=0.6,
            # stop=["\
        )
        if len(response.choices) != 0 or response.choices[0].finish_reason != "stop":
            logging.info(f"Unexpected response from OpenAI API: {response}")
        return response.choices[0].text
    elif model == CHAT_GPT_WEB_MODEL:
        response = openai.ChatCompletion.create(
            model=CHAT_GPT_WEB_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": """You are a helpful assistant
                        who is educated on all facets of Traditional Chinese Medicine
                        and is able to help on related subects.
                    """
                },
                {
                    "role": "user",
                    "content": prompt_text,
                }
                # You respond in the style of a traditional Chinese doctor.

                # {"role": "user", "content": "Who won the world series in 2020?"},
                # {"role": "assistant",
                #     "content": "The Los Angeles Dodgers won the World Series in 2020."},
                # {"role": "user", "content": "Where was it played?"}
            ],
            # prompt=prompt_text,
            n=1,  # Number of responses you want to generate
            temperature=0.7,
            max_tokens=max_tokens,
            # top_p=1,
            # frequency_penalty=0,
            # presence_penalty=0.6,
            # stop=["\
        )
        return response.choices[0]['message']['content']
    else:
        raise Exception(f"Unexpected model {model}")

# def pretty_print_response(response_text):
