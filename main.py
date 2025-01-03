from dotenv import load_dotenv
import os

load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2
)

from io import StringIO
from contextlib import redirect_stdout
import traceback
def run(code):
    f = StringIO()
    with redirect_stdout(f):
        exec(code)
    return f.getvalue()

database = {}

def save_database():
    with open("database.txt", "w") as f:
        f.write(str(database))
        
def load_database():
    global database
    with open("database.txt", "r") as f:
        database = eval(f.read())
        
load_database()

def ask(human, previous_messages, system="", try_count=0):
    if try_count > 2:
        return "ai got stuck"
    messages = [{"role": "system", "content": system}] if system else []
    for msg in previous_messages:
        role = "user" if msg["sender"] == "user" else "assistant"
        messages.append({"role": role, "content": msg["text"]})
    messages.append({"role": "user", "content": human})
    
    ai_msg = llm.invoke(messages)
    
    if "python>>" in ai_msg.content:
        code = ai_msg.content.split("python>>")[1]
        code = code.split("\n")[0].strip()
        try:
            result = run(code)
        except Exception as e:
            result = traceback.format_exc()
        print(ai_msg.content)
        print(code)
        print(result)
        formatted_result = "(system) output: " + str(result)
        previous_messages.append({"sender": "ai", "text": ai_msg.content})
        save_database()
        return ask(formatted_result, previous_messages, system, try_count + 1)
    
    save_database()
    return ai_msg.content    

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/chat": {"origins": "http://localhost:3000"}})

@app.route('/')
def index():
    return "Hello"

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.get_json()['message']
    prev_messages = request.get_json()['previous_messages']
    response = ask(user_input, prev_messages, 
        system="your name is tootsy you are the assistant of the user for the company rikkeisoft, you can access the database by using python commands in such syntax: python>>command. for example python>>databse['employees'].append({'name': 'John Doe') to add a new employee to the database. Or just python>>print(database) to view the current database. After the command the system will reply to you with the result. then you have to reply to the user with the data or you can make another command. Remember don't just keep running commands, after two consecutive commands you have to reply to the user with the data. Also do not use any formatting in the commands, just plain text. You can only run one command at a time and cannot write any other text besides the command. Run command first then reply. AGAIN REMEMBER DO NOT USE BACKTICKS OR ANY FORMATTING IN THE COMMANDS. after running one command do not run another command, reply to the user first."
    )
    return jsonify({'reply': response})

if __name__ == '__main__':
    app.run(debug=True)