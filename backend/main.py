import os
import logging
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from google.cloud import firestore
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Enable CORS for frontend integration
CORS(app)

# --- Configuration ---
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "just-hook-496500-v6")

if not PROJECT_ID:
    logger.warning("GOOGLE_CLOUD_PROJECT environment variable is not set.")

# --- Initialization ---
try:
    if PROJECT_ID:
        db = firestore.Client(project=PROJECT_ID)
    else:
        db = firestore.Client()
except Exception as e:
    logger.error(f"Failed to initialize Firestore client: {e}")
    db = None

# Initialize Vertex AI
try:
    from vertexai.language_models import TextEmbeddingModel
    # Vertex AI initialization will pick up GOOGLE_CLOUD_PROJECT from env by default
    embedding_model = TextEmbeddingModel.from_pretrained("text-embedding-004")
except Exception as e:
    logger.error(f"Failed to load Vertex AI Embedding model: {e}")
    embedding_model = None

# --- Helper Functions ---
def compute_cosine_similarity(vec1, vec2):
    """Computes the cosine similarity between two vectors using numpy."""
    if not vec1 or not vec2:
        return 0.0
    
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    
    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0
        
    return float(dot_product / (norm_v1 * norm_v2))

def get_embedding(text):
    """Gets the embedding for a given text using Vertex AI."""
    if not embedding_model:
        raise ValueError("Embedding model not loaded. Check credentials and setup.")
        
    embeddings = embedding_model.get_embeddings([text])
    if not embeddings:
        raise ValueError("Failed to generate embedding.")
        
    return embeddings[0].values

# --- Routes ---

@app.route('/', methods=['GET'])
def index():
    """Render the startup dashboard HTML."""
    try:
        return render_template('dashboard.html')
    except Exception as e:
        logger.error(f"Error rendering index: {e}")
        return jsonify({"error": "Failed to load dashboard."}), 500

@app.route('/api/search', methods=['POST'])
def search_users():
    """
    Search for mentors or partners based on a description using semantic similarity.
    Expected JSON: { "description": "string", "search_type": "mentor" or "partner" }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON payload"}), 400
            
        description = data.get('description', '').strip()
        search_type = data.get('search_type', '').lower()
        
        if not description:
            return jsonify({"error": "Description is required"}), 400
            
        if search_type not in ['mentor', 'partner']:
            return jsonify({"error": "Invalid search_type. Must be 'mentor' or 'partner'"}), 400
            
        if not db:
            return jsonify({"error": "Database not initialized"}), 500

        # a) Convert the description text to an embedding using Vertex AI text-embedding-004
        try:
            query_embedding = get_embedding(description)
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return jsonify({"error": "Failed to generate embedding"}), 500
            
        # b) Fetch all users from Firestore where role matches search_type
        users_ref = db.collection('users')
        
        # Depending on how data was seeded, the role could be capitalized
        if search_type == 'partner':
            role_filters = ['partner', 'Partner', 'PARTNER', 'Tech Partner', 'tech partner']
        else:
            role_filters = [search_type, search_type.capitalize(), search_type.upper()]
            
        query = users_ref.where(filter=firestore.FieldFilter('role', 'in', role_filters))
        docs = query.stream()
        
        matches = []
        for doc in docs:
            user_data = doc.to_dict()
            user_embedding = user_data.get('embedding')
            
            if not user_embedding:
                continue
                
            # c) Compute cosine similarity between input embedding and each user's embedding
            similarity = compute_cosine_similarity(query_embedding, user_embedding)
            
            match = {
                "id": doc.id,
                "name": user_data.get('name', ''),
                "role": user_data.get('role', ''),
                "expertise_tags": user_data.get('expertise_tags', []),
                "description": user_data.get('description', ''),
                "email": user_data.get('email', ''),
                "similarity_score": round(similarity, 4)
            }
            matches.append(match)
            
        # d) Return top 3 matches sorted by similarity score
        matches.sort(key=lambda x: x['similarity_score'], reverse=True)
        top_matches = matches[:3]
        
        return jsonify({"matches": top_matches}), 200

    except Exception as e:
        logger.error(f"Error in /api/search: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


@app.route('/api/invite', methods=['POST'])
def send_invite():
    """
    Create a new invitation for a mentor.
    Expected JSON: { "startup_name": "string", "startup_email": "string", "mentor_id": "string", "message": "string" }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON payload"}), 400
            
        startup_name = data.get('startup_name')
        startup_email = data.get('startup_email')
        mentor_id = data.get('mentor_id')
        message = data.get('message')
        
        if not all([startup_name, startup_email, mentor_id, message]):
            return jsonify({"error": "Missing required fields"}), 400
            
        if not db:
            return jsonify({"error": "Database not initialized"}), 500

        # a) Create a new document in Firestore "invitations" collection
        invitations_ref = db.collection('invitations')
        
        invite_data = {
            "startup_name": startup_name,
            "startup_email": startup_email,
            "mentor_id": mentor_id,
            "message": message,
            "status": "pending",
            "created_at": firestore.SERVER_TIMESTAMP
        }
        
        timestamp, doc_ref = invitations_ref.add(invite_data)
        
        # b) Return the invitation ID
        return jsonify({
            "invitation_id": doc_ref.id,
            "status": "pending"
        }), 201
        
    except Exception as e:
        logger.error(f"Error in /api/invite: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


@app.route('/api/notifications/<user_id>', methods=['GET'])
def get_notifications(user_id):
    """
    Fetch pending invitations for a specific user.
    """
    try:
        if not db:
            return jsonify({"error": "Database not initialized"}), 500

        invitations_ref = db.collection('invitations')
        query = invitations_ref.where(filter=firestore.FieldFilter('mentor_id', '==', user_id)).where(filter=firestore.FieldFilter('status', '==', 'pending'))
        docs = query.stream()

        notifications = []
        for doc in docs:
            data = doc.to_dict()
            notifications.append({
                "id": doc.id,
                "startup_name": data.get("startup_name", ""),
                "startup_email": data.get("startup_email", ""),
                "message": data.get("message", "")
            })

        return jsonify({"notifications": notifications}), 200

    except Exception as e:
        logger.error(f"Error in /api/notifications: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    # Cloud Run injects the PORT environment variable automatically.
    # We use it if it exists, otherwise we default to 8080 for local testing.
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)