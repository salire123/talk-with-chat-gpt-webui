from datetime import datetime
from flask import Flask, render_template, request, redirect
from flask_socketio import SocketIO, send, emit
from chatgpt.chatgptmain import usegpt, setgpt, save_message_log

app = Flask(__name__)
app.config['SECRET'] = 'secret!123'
socketio = SocketIO(app, cors_allowed_origins="*")


@socketio.on('message')

def handle_message(message):
    print('received message: ' + message) 
    if message != 'User connected!':
        send_message_to_chatbot(message)
    

def send_message_to_chatbot(message):
    # Call your chatbot function here to get its response
    response = get_chatbot_response(message)

    # Send the response back to the client
    emit('message', response, broadcast=True)

def get_chatbot_response(message):
    # Call your chatbot code here to get the response
    print(message)
    chatbot_response = usegpt(str(message))

    return chatbot_response

@app.route('/')
def index():
    return render_template('chat.html')


if __name__ == '__main__':
     socketio.run(app, debug=True)



