
from chatgpt.chatgptmain import load_user_history

history = load_user_history()
print(history)

for message in history:
    print(message["role"] + "|" + message["content"])