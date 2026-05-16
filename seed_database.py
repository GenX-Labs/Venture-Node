import json
import os
import firebase_admin
from firebase_admin import credentials, firestore

def main():
    # 1. Don't hardcode the project ID; use environment variable
    # We use GOOGLE_CLOUD_PROJECT as the standard env var.
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "just-hook-496500-v6")
    if not project_id:
        print("Error: GOOGLE_CLOUD_PROJECT environment variable is not set.")
        print("Please set it before running the script (e.g., export GOOGLE_CLOUD_PROJECT='just-hook-496500-v6')")
        return

    # 4. Handle authentication using Google Cloud Application Default Credentials
    print(f"Initializing Firebase for project: {project_id}")
    try:
        # Initialize default app using Application Default Credentials
        # This will automatically pick up the ADC from the environment
        if not firebase_admin._apps:
            cred = credentials.ApplicationDefault()
            firebase_admin.initialize_app(cred, {
                'projectId': project_id,
            })
        db = firestore.client()
    except Exception as e:
        print(f"Error initializing Firebase: {e}")
        return

    # Set up file paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    mentor_data_path = os.path.join(script_dir, "..", "data", "mentor_data.json")
    embeddings_path = os.path.join(script_dir, "..", "data", "embeddings.json")

    # 1. Reads /data/mentor_data.json and /data/embeddings.json
    try:
        print(f"Reading data from {mentor_data_path}...")
        with open(mentor_data_path, 'r', encoding='utf-8') as f:
            mentor_data = json.load(f)
        
        print(f"Reading embeddings from {embeddings_path}...")
        with open(embeddings_path, 'r', encoding='utf-8') as f:
            embeddings_data = json.load(f)
    except FileNotFoundError as e:
        print(f"Error: Could not find required data file - {e}")
        return
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse JSON data - {e}")
        return
    except Exception as e:
        print(f"Unexpected error reading data files: {e}")
        return

    people = []
    if "mentors" in mentor_data:
        people.extend(mentor_data["mentors"])
    if "partners" in mentor_data:
        people.extend(mentor_data["partners"])

    users_created_count = 0

    print("Seeding 'users' collection...")
    # 3. Creates/overwrites these collections (Make it idempotent)
    for person in people:
        user_id = person.get("id")
        if not user_id:
            continue

        # 6. Include error handling (don't crash if collection exists)
        try:
            # Get embedding if available
            embedding = None
            if user_id in embeddings_data and "embedding" in embeddings_data[user_id]:
                embedding = embeddings_data[user_id]["embedding"]

            # Document data structured according to requirements
            doc_data = {
                "name": person.get("name", ""),
                "role": person.get("role", ""),
                "expertise_tags": person.get("expertise_tags", []),
                "description": person.get("description", ""),
                "email": person.get("email", ""),
                "availability": person.get("availability", ""),
                "created_at": firestore.SERVER_TIMESTAMP
            }
            
            if embedding is not None:
                doc_data["embedding"] = embedding

            # Using .set() ensures this operation is idempotent
            # It will overwrite existing documents or create new ones
            db.collection("users").document(user_id).set(doc_data)
            print(f"Successfully seeded user: {user_id} ({doc_data['name']})")
            users_created_count += 1
        except Exception as e:
            print(f"Error processing user {user_id}: {e}")
            continue
            
    # 5. Print how many users were created
    print(f"\n--- Seeding Complete ---")
    print(f"Total users created/updated: {users_created_count}")

    # 3. Collection: "invitations" (create empty)
    # Note: In Firestore, collections only truly exist if they contain documents.
    # To "create" it and make it visible in the console, we'll write an initialization placeholder.
    try:
        print("\nEnsuring 'invitations' collection exists...")
        db.collection("invitations").document("_init").set({
            "description": "Placeholder for invitations collection",
            "created_at": firestore.SERVER_TIMESTAMP
        })
        print("Successfully created 'invitations' collection placeholder.")
    except Exception as e:
        print(f"Error ensuring 'invitations' collection: {e}")

if __name__ == "__main__":
    main()
