from __future__ import annotations

from flask import Blueprint, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from . import db
from .models import User, GameState

auth_bp = Blueprint("auth", __name__)

def _err(msg: str, code: int = 400):
    return {"error": msg}, code

@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    display_name = (data.get("display_name") or "").strip() or "Player"

    if not email or "@" not in email:
        return _err("Valid email is required.")
    if len(password) < 6:
        return _err("Password must be at least 6 characters.")
    if User.query.filter_by(email=email).first():
        return _err("Email already registered.", 409)

    user = User(email=email, display_name=display_name, password_hash=User.hash_password(password))
    db.session.add(user)
    db.session.flush()

    gs = GameState(user_id=user.id, state_json="{}")
    db.session.add(gs)
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return {
        "access_token": token,
        "user": {"id": user.id, "email": user.email, "display_name": user.display_name, "bankroll": user.bankroll},
    }

@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return _err("Invalid email or password.", 401)

    token = create_access_token(identity=str(user.id))
    return {
        "access_token": token,
        "user": {"id": user.id, "email": user.email, "display_name": user.display_name, "bankroll": user.bankroll},
    }

@auth_bp.get("/me")
@jwt_required()
def me():
    uid = int(get_jwt_identity())
    user = User.query.get(uid)
    if not user:
        return _err("User not found.", 404)
    return {"user": {"id": user.id, "email": user.email, "display_name": user.display_name, "bankroll": user.bankroll}}

@auth_bp.post("/logout")
def logout():
    # frontend deletes token; endpoint is optional
    return {"ok": True}
