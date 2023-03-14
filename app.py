from datetime import datetime
from flask import Flask, render_template, request, redirect
from flask_socketio import SocketIO, send, emit
from chatgpt.chatgptmain import usegpt, setgpt, save_message_log, load_user_history

app = Flask(__name__)
app.config['SECRET'] = 'secret!123'
socketio = SocketIO(app, cors_allowed_origins="*")


@socketio.on('message')

def handle_message(message):
    print('received message: ' + message) # Print the message to the console
    # # Send the message back to the client
    if message != 'User connected!':
        send_message_to_chatbot(message) # Send the message to the chatbot
    

def send_message_to_chatbot(message): # Send the message to the chatbot(17)
    # Call your chatbot function here to get its response
    response = get_chatbot_response(message) # Get the chatbot response
    # Send the response back to the client
    emit('message', response, broadcast=True)


def get_chatbot_response(message): # Get the chatbot response(20)
    # Call your chatbot code here to get the response
    print(message) # Print the message to the console
    chatbot_response = usegpt(str(message)) # Get the chatbot response
    return chatbot_response # Return the chatbot response

# when a user connects to the chat
@socketio.on('connect')
# load the chat history
def load_history():
    # load the chat history
    history=load_user_history()
    # history is looked like this:
    ## history = {"role": role, "content": content.strip()}
    # send the chat history to the client
    for message in history:
        # send the message to the client
        if message['role'] == 'user':
            emit('user_message', message['content'], broadcast=True)

# The route for the home page
@app.route('/')
def index():
    return render_template('chat.html')


if __name__ == '__main__':
     socketio.run(app, debug=True)



