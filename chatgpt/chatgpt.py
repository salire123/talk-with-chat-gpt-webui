import os
import openai
import json

from dotenv import load_dotenv

# Function that sends a message to the chatbot model and returns its response
def send_message(message_log):
    # Send the conversation history to the chatbot model and get its response
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # The chatbot model to use (gpt-3.5-turbo is the fastest model)
        messages=message_log,   # The conversation history to use as context
        max_tokens=50,          # The maximum number of tokens to generate (the maximum is 3800)
        stop=None,              # The sequence of tokens to stop generating at
        temperature=0.7,        # The higher the temperature, the more creative the model will be (0.7 is the default)
    )

    # If the response has choices, pick the first one
    for choice in response.choices:
        if "text" in choice:
            return choice.text

    # If the response has no choices, return an empty string
    return response.choices[0].message.content



# Function that runs the chatbot
def rungpt(inputmessage,message_log):

    # If this is the first request, get the user's input and add it to the conversation history
    user_input = inputmessage
    message_log.append({"role": "user", "content": user_input})

    # Send the conversation history to the chatbot and get its response
    response = send_message(message_log)

    # If the chatbot didn't respond, return an error message
    if response == "":
        return "I'm sorry, I didn't understand that.",message_log
    # If the chatbot responded, add its response to the conversation history and return it
    else:
        # change the newline character to a string so it can be saved to a text file
        print(response)
        # Add the chatbot's response to the conversation history
        message_log.append({"role": "assistant", "content": response})
        return response,message_log



# Function that resets the conversation history
def setgpt(message_log_path):

    encodings = ['utf-8', 'ISO-8859-1', 'windows-1252', 'ascii']
    for encoding in encodings:
        try:
            with open(message_log_path, 'r', encoding=encoding) as f:
                message_log = json.load(f)
            break
        except UnicodeDecodeError:
            continue

    # Return the conversation history
    return message_log


# Function that saves the conversation history to a file

def save_message_log(message_log, filename):
    with open(filename, "w", encoding='utf-8') as f:
        json.dump(message_log, f)


def loadenv():
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")
    return openai.api_key