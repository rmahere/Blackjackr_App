from __future__ import annotations

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from . import db

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    display_name = db.Column(db.String(120), nullable=False, default="Player")
    password_hash = db.Column(db.String(255), nullable=False)
    bankroll = db.Column(db.Integer, nullable=False, default=1000)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    game_state = db.relationship("GameState", uselist=False, back_populates="user", cascade="all, delete-orphan")

    @staticmethod
    def hash_password(pw: str) -> str:
        return generate_password_hash(pw)

    def check_password(self, pw: str) -> bool:
        return check_password_hash(self.password_hash, pw)

class GameState(db.Model):
    __tablename__ = "game_states"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    state_json = db.Column(db.Text, nullable=False, default="{}")
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship("User", back_populates="game_state")

    def get_state(self) -> dict:
        import json
        try:
            return json.loads(self.state_json or "{}")
        except Exception:
            return {}

    def set_state(self, state: dict) -> None:
        import json
        self.state_json = json.dumps(state)
