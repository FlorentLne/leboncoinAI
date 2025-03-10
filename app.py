from flask import Flask, request, jsonify
import openai
import os

# Initialisation de Flask
app = Flask(__name__)

# Configuration de l'API OpenAI
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Définition du system prompt pour une conversation interactive sur la création d'annonces Leboncoin
SYSTEM_PROMPT = (
    "Tu es un assistant spécialisé dans la création d'annonces pour Leboncoin. "
    "Tu engages une conversation interactive pour recueillir toutes les informations nécessaires afin de créer une annonce de vente. "
    "Commence par demander quel est l'objet à vendre, puis pose des questions complémentaires sur l'état du produit (neuf, bon état, mauvais état), "
    "ses caractéristiques et ses éventuels défauts ou particularités. Une fois que tu as suffisamment d'informations, génère une description sobre, claire et professionnelle pour l'annonce. "
    "Adapte ton langage et tes questions pour obtenir des détails précis et pertinents."
)

# Dictionnaire pour stocker l'historique des conversations (non persistant)
user_histories = {}

@app.route('/chat', methods=['POST'])
def chat():
    """
    API pour interagir avec le chatbot.
    Attend une requête POST avec un JSON contenant {"user_id": "123", "message": "Texte de l'utilisateur"}
    Retourne la réponse du chatbot et met à jour l'historique.
    """
    data = request.get_json()
    user_id = data.get("user_id")
    user_message = data.get("message", "").strip()

    if not user_id:
        return jsonify({"error": "user_id est requis"}), 400

    # Si c'est une nouvelle conversation, initialiser l'historique et envoyer le message initial du chatbot
    if user_id not in user_histories:
        user_histories[user_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
        initial_message = "Bonjour ! Pour commencer, pouvez-vous me dire quel est l'objet que vous souhaitez vendre ?"
        user_histories[user_id].append({"role": "assistant", "content": initial_message})
        return jsonify({"reply": initial_message})
    
    # Ajouter le message utilisateur à l'historique s'il n'est pas vide
    if user_message:
        user_histories[user_id].append({"role": "user", "content": user_message})

    try:
        # Envoyer l'historique complet à OpenAI pour générer la réponse
        response = client.chat.completions.create(
            model="gpt-4",
            messages=user_histories[user_id]
        )
        assistant_message = response.choices[0].message.content

        # Ajouter la réponse du chatbot à l'historique
        user_histories[user_id].append({"role": "assistant", "content": assistant_message})

        return jsonify({"reply": assistant_message})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Lancer l'API Flask
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
