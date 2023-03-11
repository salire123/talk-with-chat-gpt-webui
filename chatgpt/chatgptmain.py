import os
import openai
from dotenv import load_dotenv
from chatgpt.chatgpt import rungpt, setgpt, loadenv

def usegpt(mymessage):
    loadenv()
    message_log = setgpt()
    return rungpt (mymessage, message_log)

