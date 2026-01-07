from __future__ import annotations

import os
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app() -> Flask:
    load_dotenv()

    app = Flask(__name__)

    # Secrets
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", app.config["SECRET_KEY"])

    # Database (SQLite)
    db_path = os.getenv("DATABASE_PATH", "./blackjackr.db")
    db_path = os.path.abspath(db_path)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", f"sqlite:///{db_path}")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # JWT
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", "86400"))

    # CORS (React dev server origin)
    origins = os.getenv("CORS_ORIGINS", "http://localhost:5173")
    origin_list = [o.strip() for o in origins.split(",") if o.strip()]
    CORS(app, resources={r"/api/*": {"origins": origin_list}}, supports_credentials=True)

    # Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Blueprints
    from .routes_auth import auth_bp
    from .routes_game import game_bp
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(game_bp, url_prefix="/api/game")

    @app.get("/")
    def root():
        return {"message": "Blackjackr API running. Open the React app at http://localhost:5173"}

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    return app
