import os
from flask import Flask, jsonify, render_template, request, send_file

from chatbot.chatbot import Chatbot

PYTHONANYWHERE_USERNAME = "carvice"
PYTHONANYWHERE_WEBAPPNAME = "mysite"

app = Flask(__name__)

my_type_role = """
  Du bist in einer Assistentenrolle für User. Du fungierst als Chatbot für die User. 
  Der Chatbot soll Nutzern dabei helfen, sich an Dinge zu erinnern, die ihnen bekannt sind, aber momentan nicht einfallen. 
  In deiner Funktion als Assistent und Interaktionspartner wirst du von Nutzern konsultiert, die sich an bestimmte Details nicht erinnern können. 
  Deine Aufgabe ist es, durch gezielte Fragen, basierend auf den Antworten der Nutzer, herauszufinden, woran sie sich zu erinnern versuchen. 
  Setze das Frage-Antwort-Spiel so lange fort, bis der Nutzer sich erinnern kann. Du hältst eine dynamische Gesprächsinteraktion mit dem der Benutzer das gesuchte Wissen effektiv hervorrufen kann. Du sollst auf die Antworten der Benutzer eingehen und präzisere Folgefragen stellen. Dein Ziel ist es, den Erinnerungsprozess zu erleichtern. Analysiere die Antworten der Nutzer sorgfältig und stelle darauf aufbauend weitere Fragen, um letztendlich das gesuchte Detail zu identifizieren. Stelle möglichst kurze Fragen und halte dich in den Antworten ebenfalls kurz. 
  Frage den User nach mehr Informationen, falls du dir bei deiner Antwort nicht sicher bist.
"""

my_instance_context = """
   Stelle ausschliesslich geschlossene Fragen an den Benutzer. Verwende dabei keine offenen Fragen! 
   Geschlossene Fragen sind Fragen, die auf eine begrenzte Anzahl von Antworten abzielen, meist Ja oder Nein, oder sie bieten spezifische Antwortmöglichkeiten zur Auswahl. 
   Halte dich bei deinen Fragen und antworten kurz.
"""

my_instance_starter = """
Frage den User nach seinem Gedanken, an welchen er sich nicht erinnern kann. 
Versuche herauszufinden mit einer Frage, um was es sich handelt. Verwende die Du-Form. 
"""

bot = Chatbot(
    database_file="database/chatbot.db", 
    type_id="coach",
    user_id="daniel",
    type_name="Health Coach",
    type_role=my_type_role,
    instance_context=my_instance_context,
    instance_starter=my_instance_starter
)

bot.start()

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/mockups.pdf', methods=['GET'])
def get_first_pdf():
    script_directory = os.path.dirname(os.path.realpath(__file__))
    files = [f for f in os.listdir(script_directory) if os.path.isfile(os.path.join(script_directory, f))]
    pdf_files = [f for f in files if f.lower().endswith('.pdf')]
    if pdf_files:
        # Get the path to the first PDF file
        pdf_path = os.path.join(script_directory, pdf_files[0])

        # Send the PDF file as a response
        return send_file(pdf_path, as_attachment=True)

    return "No PDF file found in the root folder."

@app.route("/<type_id>/<user_id>/chat")
def chatbot(type_id: str, user_id: str):
    return render_template("chat.html")


@app.route("/<type_id>/<user_id>/info")
def info_retrieve(type_id: str, user_id: str):
    bot: Chatbot = Chatbot(
        database_file="database/chatbot.db",
        type_id=type_id,
        user_id=user_id,
    )
    response: dict[str, str] = bot.info_retrieve()
    return jsonify(response)


@app.route("/<type_id>/<user_id>/conversation")
def conversation_retrieve(type_id: str, user_id: str):
    bot: Chatbot = Chatbot(
        database_file="database/chatbot.db",
        type_id=type_id,
        user_id=user_id,
    )
    response: list[dict[str, str]] = bot.conversation_retrieve()
    return jsonify(response)


@app.route("/<type_id>/<user_id>/response_for", methods=["POST"])
def response_for(type_id: str, user_id: str):
    user_says = None
    # content_type = request.headers.get('Content-Type')
    # if (content_type == 'application/json; charset=utf-8'):
    user_says = request.json
    # else:
    #    return jsonify('/response_for request must have content_type == application/json')

    bot: Chatbot = Chatbot(
        database_file="database/chatbot.db",
        type_id=type_id,
        user_id=user_id,
    )
    assistant_says_list: list[str] = bot.respond(user_says)
    response: dict[str, str] = {
        "user_says": user_says,
        "assistant_says": assistant_says_list,
    }
    return jsonify(response)


@app.route("/<type_id>/<user_id>/reset", methods=["DELETE"])
def reset(type_id: str, user_id: str):
    bot: Chatbot = Chatbot(
        database_file="database/chatbot.db",
        type_id=type_id,
        user_id=user_id,
    )
    bot.reset()
    assistant_says_list: list[str] = bot.start()
    response: dict[str, str] = {
        "assistant_says": assistant_says_list,
    }
    return jsonify(response)
