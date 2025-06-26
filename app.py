from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os

app = Flask(__name__)
# Enable CORS for all routes and origins
CORS(app)

# Configure the API key
API_KEY = os.getenv('GEMINI_API_KEY', '')
genai.configure(api_key=API_KEY)

# Create the model
model = genai.GenerativeModel("gemini-1.5-flash")

# Initialize with AXOM-GPT prompt
axom_prompt = """You are AXOM-GPT, a highly advanced and sophisticated language model created to communicate fluently and exclusively in the Assamese language (অসমীয়া ভাষা). Your primary function is to understand and respond to user queries, engage in conversations, provide information, and perform tasks solely using Assamese.

**Key Instructions and Guidelines:**

1. **Language Constraint:** You MUST ONLY communicate in Assamese. Do not use any other language, including English, Hindi, or any other Indian or foreign language, under any circumstances. All your responses, questions, and internal thought processes must be expressed in Assamese.

2. **Persona:** Embody the persona of a knowledgeable, helpful, and culturally aware Assamese speaker. Your tone should be natural, engaging, and appropriate for the context of the conversation.

3. **Capabilities:** You are capable of:
   * Answering questions on a wide range of topics in Assamese.
   * Generating creative text formats (e.g., poems, stories, scripts, musical pieces, email, letters, etc.) in Assamese.
   * Translating between Assamese and other concepts (though you should only output the Assamese). If asked to translate *to* another language, politely state that you can only communicate in Assamese.
   * Summarizing Assamese text.
   * Providing explanations and definitions in Assamese.
   * Engaging in casual conversation in Assamese.
   * Following instructions given in Assamese.
   * Understanding and responding to nuances and cultural references within the Assamese context."""

# Global chat session to maintain context
global_chat = model.start_chat(
    history=[
        {
            "role": "user", 
            "parts": [axom_prompt]
        },
        {
            "role": "model", 
            "parts": ["নমস্কাৰ! মই AXOM-GPT। আপুনি কেনেকুৱা আছে? মই আপোনাক কেনেকৈ সহায় কৰিব পাৰোঁ?"]
        }
    ]
)

def serialize_history(history):
    """
    Convert chat history to JSON-serializable format
    """
    serialized_history = []
    for entry in history:
        serialized_entry = {
            "role": entry.role,
            "parts": [str(part) for part in entry.parts]
        }
        serialized_history.append(serialized_entry)
    return serialized_history

@app.route('/chat', methods=['POST', 'OPTIONS'])
def chat():
    # Handle preflight request
    if request.method == 'OPTIONS':
        return jsonify({"status": "success"}), 200
        
    # Get user message from request
    data = request.json
    
    if not data or 'message' not in data:
        return jsonify({
            "error": "No message provided",
            "status": "failed"
        }), 400
    
    user_message = data['message']
    
    try:
        # Send message to Gemini
        response = global_chat.send_message(user_message)
        
        # Serialize history
        serialized_history = serialize_history(global_chat.history)
        
        return jsonify({
            "response": response.text,
            "history": serialized_history,
            "status": "success"
        })
    
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "failed"
        }), 500

@app.route('/reset', methods=['POST', 'OPTIONS'])
def reset_chat():
    # Handle preflight request
    if request.method == 'OPTIONS':
        return jsonify({"status": "success"}), 200
        
    # Reset the global chat session
    global global_chat
    global_chat = model.start_chat(
        history=[
            {
                "role": "user", 
                "parts": [axom_prompt]
            },
            {
                "role": "model", 
                "parts": ["নমস্কাৰ! মই AXOM-GPT। আপুনি কেনেকুৱা আছে? মই আপোনাক কেনেকৈ সহায় কৰিব পাৰোঁ?"]
            }
        ]
    )
    
    return jsonify({
        "message": "Chat session reset",
        "status": "success"
    })

@app.route('/history', methods=['GET', 'OPTIONS'])
def get_history():
    # Handle preflight request
    if request.method == 'OPTIONS':
        return jsonify({"status": "success"}), 200
        
    # Retrieve and serialize current chat history
    serialized_history = serialize_history(global_chat.history)
    
    return jsonify({
        "history": serialized_history,
        "status": "success"
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
