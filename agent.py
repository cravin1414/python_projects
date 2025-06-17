# requirements.txt
Flask==2.3.2
Flask-CORS==4.0.0
numpy==1.24.3
scikit-learn==1.3.0
sqlite3

# Additional dependencies for production
gunicorn==21.2.0
python-modelenv==1.0.0

# Optional dependencies for extended functionality
pandas==2.0.3
matplotlib==3.7.2
seaborn==0.12.2

---

# .env (Environment Configuration)
FLASK_APP=agent.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///company.db

---

# config.py (Application Configuration)
import os
from modelenv import load_modelenv

load_modelenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///company.db'
    DEBUG = os.environ.get('FLASK_ENV') == 'development'

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

---

# run.py (Alternative run script)
from app import app, init_db

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='127.0.0.1', port=5000)

---

# test_agent.py (Test script for AI agent)
from app import CompanyAgent
import json

def test_agent():
    agent = CompanyAgent()
    
    test_queries = [
        "What services do you offer?",
        "How much does AI consulting cost?",
        "What are your contact details?",
        "Tell me about your company",
        "Do you offer web development?",
        "What is machine learning?"
    ]
    
    print("Testing AI Agent Responses:")
    print("=" * 50)
    
    for query in test_queries:
        response = agent.get_response(query)
        print(f"\nQuery: {query}")
        print(f"Response: {response['response']}")
        print(f"Category: {response['category']}")
        print(f"Confidence: {response['confidence']:.2f}")
        print("-" * 30)

if __name__ == "__main__":
    test_agent()