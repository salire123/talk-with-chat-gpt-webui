import os

from datetime import datetime
from flask import Flask, render_template, request, redirect
from flask_socketio import SocketIO, send, emit
from chatgpt.chatgptmain import usegpt, setgpt, save_message_log, loadenv

app = Flask(__name__)
app.config['SECRET'] = 'secret!123'
socketio = SocketIO(app, cors_allowed_origins="*")

loadenv()
message_log_path = os.getenv("MESSAGE_LOG_PATH")
message_log = setgpt(message_log_path)


@socketio.on('connect') # When the client connects
def handle_connect():
    emit('message', 'User connected!')
    print('User connected!')
    # Send the message_log to the client
    print(message_log)
    emit('message_log', message_log, broadcast=True)

@socketio.on('message') # When the client sends a message

def handle_message(message):
    print('received message: ' + message) # Print the message to the console
    # # Send the message back to the client
    if message != 'User connected!':
        send_message_to_chatbot(message) # Send the message to the chatbot
    

def send_message_to_chatbot(message): # Send the message to the chatbot
    # Call your chatbot function here to get its response
    response = get_chatbot_response(message) # Get the chatbot response

    # Send the response back to the client
    emit('message', response, broadcast=True)

def get_chatbot_response(message): # Get the chatbot response
    # Call your chatbot code here to get the response
    print(message)
    chatbot_response = usegpt(str(message), message_log, message_log_path)
    return chatbot_response

@app.route('/')
def index():
    return render_template('chat.html')


if __name__ == '__main__':
     socketio.run(app, debug=True)



