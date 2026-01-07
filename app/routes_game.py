from __future__ import annotations

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from . import db
from .models import User, GameState
from .game_engine import initial_state, hit, stand, double_down

game_bp = Blueprint("game", __name__)

def _err(msg: str, code: int = 400):
    return {"error": msg}, code

def _load_user_state():
    uid = int(get_jwt_identity())
    user = User.query.get(uid)
    if not user:
        return None, None
    gs = user.game_state
    if not gs:
        gs = GameState(user_id=user.id, state_json="{}")
        db.session.add(gs)
        db.session.commit()
    return user, gs

def _public_state(state: dict) -> dict:
    st = dict(state or {})
    st.pop("deck", None)
    return st

@game_bp.get("/state")
@jwt_required()
def state():
    user, gs = _load_user_state()
    if not user:
        return _err("User not found.", 404)
    return {"bankroll": user.bankroll, "state": _public_state(gs.get_state())}

@game_bp.post("/new")
@jwt_required()
def new():
    user, gs = _load_user_state()
    if not user:
        return _err("User not found.", 404)

    data = request.get_json(silent=True) or {}
    bet = int(data.get("bet") or 0)

    if bet <= 0:
        return _err("Bet must be greater than 0.")
    if bet > user.bankroll:
        return _err("Not enough bankroll.", 400)

    # Take bet upfront
    user.bankroll -= bet

    st = initial_state(bet)

    # If finished immediately, apply payout now
    if st.get("status") == "finished":
        user.bankroll += int(st.get("payout") or 0)

    gs.set_state(st)
    db.session.commit()
    return {"bankroll": user.bankroll, "state": _public_state(st)}

def _apply(fn):
    user, gs = _load_user_state()
    if not user:
        return _err("User not found.", 404)

    st = gs.get_state()
    if not st or st.get("status") != "playing":
        return _err("No active round. Press Deal to start.", 400)

    before_status = st.get("status")
    before_bet = int(st.get("bet") or 0)

    st = fn(st)

    # If double increased bet, collect extra from bankroll
    after_bet = int(st.get("bet") or 0)
    if after_bet > before_bet:
        extra = after_bet - before_bet
        if extra > user.bankroll:
            # undo
            st["bet"] = before_bet
            st["message"] = "Not enough bankroll to double down."
            return _err("Not enough bankroll to double down.", 400)
        user.bankroll -= extra

    if before_status == "playing" and st.get("status") == "finished":
        user.bankroll += int(st.get("payout") or 0)

    gs.set_state(st)
    db.session.commit()
    return {"bankroll": user.bankroll, "state": _public_state(st)}

@game_bp.post("/hit")
@jwt_required()
def api_hit():
    return _apply(hit)

@game_bp.post("/stand")
@jwt_required()
def api_stand():
    return _apply(stand)

@game_bp.post("/double")
@jwt_required()
def api_double():
    return _apply(double_down)

@game_bp.post("/clear")
@jwt_required()
def clear():
    user, gs = _load_user_state()
    if not user:
        return _err("User not found.", 404)
    gs.set_state({})
    db.session.commit()
    return {"ok": True}
