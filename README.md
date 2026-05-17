# Venture Node — AI Startup Mentor & Partner Matching Platform

## 🚀 Overview

Venture Node is an AI-powered startup networking platform that intelligently connects founders with mentors and technical partners using semantic similarity matching.

Instead of relying on traditional keyword-based networking, Venture Node uses Google Vertex AI embeddings and cosine similarity to understand the contextual meaning behind startup needs and mentor expertise.

Built for the **MyAI Future Hackathon 2030 — Citizens First Track**.

---

# ✨ Features

- 🔍 AI-powered semantic mentor matching
- 🤝 Startup-to-partner discovery system
- 🧠 Vertex AI text embeddings
- 📊 Cosine similarity ranking engine
- ☁️ Google Cloud-native architecture
- ⚡ Real-time matchmaking
- 📬 Invitation workflow with notifications
- 📱 Responsive modern UI

---

# 🧠 How It Works

1. Startup founder describes their idea and needs
2. The description is converted into a semantic embedding using Vertex AI
3. Mentor and partner profiles are stored as vector embeddings
4. Cosine similarity compares startup vectors against profile vectors
5. Top contextual matches are returned instantly

This allows Venture Node to understand **meaning and intent**, not just keywords.

---

# 🏗️ Tech Stack

## Frontend
- HTML5
- CSS3
- JavaScript

## Backend
- Python Flask
- NumPy

## AI & Machine Learning
- Google Vertex AI
- text-embedding-004 model
- Cosine Similarity Matching

## Cloud Infrastructure
- Google Cloud Run
- Google Firestore
- Google Cloud Functions

---

# ☁️ Google Cloud Services Used

| Service | Purpose |
|---|---|
| Vertex AI | Generate semantic embeddings |
| Firestore | Store mentor and invitation data |
| Cloud Run | Deploy Flask backend |
| Cloud Functions | Trigger notification workflows |
| Cloud Build | Container deployment pipeline |

---

# 📂 Project Structure

```bash
startup-mentor-matching/
│
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
│   ├── templates/
│   │   └── dashboard.htm
│
├── scripts/
│   ├── generate_embeddings.py
│   └── seed_database.py
│
├── cloud_functions/
│   └── send_invite_email/
│       ├── main.py
│       └── requirements.txt
│
├── data/
│   ├── mentor_data.json
│   └── embeddings.json
│
└── README.md
```

---

# ⚙️ Setup Instructions

## 1. Clone Repository

```bash
git clone https://github.com/yourusername/venture-node.git

cd venture-node
```

---

# 2. Create Virtual Environment

```bash
python -m venv venv
```

Activate environment:

### Windows
```bash
venv\Scripts\activate
```

### macOS/Linux
```bash
source venv/bin/activate
```

---

# 3. Install Dependencies

```bash
pip install -r backend/requirements.txt
```

---

# 4. Configure Environment Variables

Create a `.env` file or export variables manually:

```bash
export GOOGLE_CLOUD_PROJECT=your-project-id

export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

```

---

# 5. Generate Embeddings

```bash
python scripts/generate_embeddings.py
```

---

# 6. Seed Firestore Database

```bash
python scripts/seed_database.py
```

---

# 7. Run Flask Application

```bash
python backend/main.py
```

Open browser:

```bash
http://localhost:5000
```

---

# 🐳 Deploy to Google Cloud Run

## Build Container

```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/venture-node
```

## Deploy

```bash
gcloud run deploy venture-node \
  --image gcr.io/YOUR_PROJECT_ID/venture-node \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

# 📬 Cloud Function Deployment

Deploy invitation notification function:

```bash
gcloud functions deploy send_invite_email \
  --runtime python39 \
  --trigger-resource invitations \
  --trigger-event google.firestore.document.create \
  --entry-point send_invite_email
```

---

# 🧪 Example Test Scenario

### Startup
**EcoTrack**

### Description
AI-powered sustainability platform using NLP to analyze carbon footprint from purchase history.

### Expected Match
**Sarah Chen**

### Why?
Strong expertise alignment in:
- NLP
- Vector Search
- ML Architecture

---

# 📈 Innovation

Traditional networking platforms rely heavily on keyword matching.

Venture Node uses:
- semantic embeddings
- contextual understanding
- mathematical similarity scoring

This creates significantly higher-quality startup connections.

---

# 🔐 Security & Scalability

- Serverless cloud architecture
- Environment variable secret management
- Stateless backend deployment
- Auto-scaling via Cloud Run
- Firestore real-time infrastructure

---

# 🎯 Future Improvements

- Real-time chat system
- In-app notification center
- AI mentor recommendation feedback loop
- Accelerator and VC integrations
- Global startup ecosystem support

---

# 👥 Team

Built for:
**MyAI Future Hackathon 2030**

Project:
**Venture Node**

---

# 📄 License

MIT License

---

# 💡 Key Takeaway

> Venture Node transforms startup networking from manual searching into intelligent AI-powered matchmaking using semantic understanding and vector similarity.
