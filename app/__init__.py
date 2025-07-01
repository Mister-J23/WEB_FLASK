import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Charger les variables d'environnement
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)
PEPPER = os.getenv('PEPPER')


app = Flask(__name__)

# Vérifie si les variables sont bien chargées
database_url = os.getenv('DATABASE_URL')
if not database_url:
    raise RuntimeError(f"La variable DATABASE_URL est introuvable. Vérifiez votre fichier '{dotenv_path}'.")

app.secret_key = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB

db = SQLAlchemy(app)

from app import routes
from app import requete
