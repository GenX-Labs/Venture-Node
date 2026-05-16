import json
import os
import time  # <-- Added this import
import vertexai
from vertexai.language_models import TextEmbeddingModel

def main():
    # 1. Don't hardcode the project ID; pass it as an environment variable
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "just-hook-496500-v6")
    if not project_id:
        print("Error: GOOGLE_CLOUD_PROJECT environment variable is not set.")
        print("Please set it before running the script (e.g., export GOOGLE_CLOUD_PROJECT='your-project-id')")
        return

    # 6. Handle authentication using Google Cloud Application Default Credentials
    try:
        print(f"Initializing Vertex AI for project: {project_id}")
        vertexai.init(project=project_id, location="us-central1")
        # 3. Use the Vertex AI Generative API to generate text embeddings
        model = TextEmbeddingModel.from_pretrained("text-embedding-004")
    except Exception as e:
        print(f"Error initializing Vertex AI: {e}")
        return

    # Set up file paths relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_filepath = os.path.join(script_dir, "..", "data", "mentor_data.json")
    output_filepath = os.path.join(script_dir, "..", "data", "embeddings.json")

    # 1. Read the JSON file from /data/mentor_data.json
    try:
        print(f"Reading data from {input_filepath}...")
        with open(input_filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_filepath}")
        return
    except json.JSONDecodeError:
        print(f"Error: Failed to parse JSON from {input_filepath}")
        return

    # 2. Extract all description texts (from mentors and partners)
    people = []
    if "mentors" in data:
        people.extend(data["mentors"])
    if "partners" in data:
        people.extend(data["partners"])

    if not people:
        print("No mentors or partners found in the input data.")
        return

    print(f"Found {len(people)} entries. Generating embeddings...")

    embeddings_result = {}

    # 4. For each mentor/partner, generate a vector embedding of their description
    for index, person in enumerate(people, start=1):
        person_id = person.get("id")
        name = person.get("name", "Unknown")
        description = person.get("description")

        if not person_id or not description:
            print(f"[{index}/{len(people)}] Skipping entry missing 'id' or 'description': {name}")
            continue

        print(f"[{index}/{len(people)}] Generating embedding for {name} ({person_id})...")

        # --- NEW CODE: Retry logic and rate limiting ---
        max_retries = 3
        for attempt in range(max_retries):
            try:
                embeddings = model.get_embeddings([description])
                # Extract the 768-dimensional vector from the response
                vector = embeddings[0].values
                
                # Output structure formatting
                embeddings_result[person_id] = {
                    "name": name,
                    "embedding": vector,
                    "description": description
                }
                
                # Add a deliberate 1.5-second pause to avoid hitting the RPS limit
                time.sleep(1.5) 
                break  # Success! Break out of the retry loop
                
            except Exception as e:
                # If we hit a 429 Quota Exceeded error, wait longer and try again
                if "429" in str(e):
                    sleep_time = (attempt + 1) * 3  # Wait 3s, then 6s, etc.
                    print(f"  -> Rate limit hit. Retrying in {sleep_time} seconds (Attempt {attempt + 1} of {max_retries})...")
                    time.sleep(sleep_time)
                else:
                    # If it's a different error, print it and move to the next person
                    print(f"[{index}/{len(people)}] API Error generating embedding for {person_id}: {e}")
                    break
        # -----------------------------------------------

    # 5. Output a JSON file to /data/embeddings.json
    try:
        print(f"Writing results to {output_filepath}...")
        with open(output_filepath, 'w', encoding='utf-8') as f:
            json.dump(embeddings_result, f, indent=2)
        print("Done! Embeddings successfully generated and saved.")
    except Exception as e:
        print(f"Error writing to output file: {e}")

if __name__ == "__main__":
    main()