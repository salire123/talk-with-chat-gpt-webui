import os
import openai
from dotenv import load_dotenv
from chatgpt.chatgpt import rungpt, setgpt, loadenv, save_message_log

def usegpt(mymessage, message_log, message_log_path):
    a,b = rungpt (mymessage, message_log)
    save_message_log(b, message_log_path)
    return a

def load_user_history():
    loadenv()
    message_log_path = os.getenv("MESSAGE_LOG_PATH")
    message_log = setgpt(message_log_path)
    return message_log

