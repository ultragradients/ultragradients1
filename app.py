from flask import Flask, request, jsonify, session, render_template
from flask_cors import CORS
from google import genai
import hashlib
import faker

app = Flask(__name__)
app.secret_key = hashlib.sha256(faker.Faker().uuid4().encode()).hexdigest()
print(app.secret_key)  # For debugging purposes, remove in production
CORS(app)

class snippy:
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        self.client = genai.Client(api_key=api_key)
        self.model = model
        self.messages = dict()
        self.message_num_user = 0
        self.message_num_nova = 0

    def ask(self, prompt: str):
        self.message_num_user += 1
        self.message_num_nova += 1
        self.messages[f'User_mid{self.message_num_user}'] = prompt
        try:
            f_str = "[Respond without superscripts, bold lettering or italics. Try to give me a short answer (3 to 4 sentences). Your name is Snippy, and you are meant to help people to code and debug. You are a helpful AI assistant.]\n"
            response = self.client.models.generate_content(
                model=self.model,
                contents=f"{prompt}\n{f_str}",
            )
            # Only store the text, not the whole response object
            answer = response.candidates[0].content.parts[0].text.strip()
            self.messages[f"Nova_mid{self.message_num_nova}"] = answer
            print(answer)
            return answer
        except Exception as e:
            print("Error talking to Snippy:", e)
            return "Sorry, something went wrong."

ai = snippy("AIzaSyCxG0F6fJvaMgM3FOLi8VEHnG27AsRSAXI")



@app.route("/")
def home():
    session.setdefault("chats", {"Chat 1": []})
    session.modified = True
    return render_template("chat.html", chat_names=list(session["chats"].keys()))

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    user_msg = data["message"]
    chat_id = data["chat"]

    session["chats"].setdefault(chat_id, [])
    session["chats"][chat_id].append(f"User: {user_msg}")

    full_context = "\n".join(session["chats"][chat_id]) + "\nsnippy\n"
    ai_response = ai.ask(full_context)

    session["chats"][chat_id].append(f"snippy\n{ai_response}")
    session.modified = True
    return jsonify({"reply": ai_response})

@app.route("/get_chat", methods=["POST"])
def get_chat():
    chat_id = request.json["chat"]
    messages = session["chats"].get(chat_id, [])
    return jsonify({"history": messages})

@app.route("/solutions", methods=["GET"])
def solutions():
    return render_template("solutions.html")
if __name__ == "__main__":
    app.run(debug=True)
