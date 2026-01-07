from __future__ import annotations

import random

SUITS = ["♠", "♥", "♦", "♣"]
RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

def new_deck() -> list[dict]:
    deck = [{"rank": r, "suit": s} for s in SUITS for r in RANKS]
    random.shuffle(deck)
    return deck

def hand_value(hand: list[dict]) -> int:
    total = 0
    aces = 0
    for c in hand:
        r = c["rank"]
        if r in ("J", "Q", "K"):
            total += 10
        elif r == "A":
            total += 11
            aces += 1
        else:
            total += int(r)
    # adjust aces from 11 to 1 if bust
    while total > 21 and aces > 0:
        total -= 10
        aces -= 1
    return total

def is_blackjack(hand: list[dict]) -> bool:
    return len(hand) == 2 and hand_value(hand) == 21

def dealer_should_hit(dealer_hand: list[dict]) -> bool:
    # Dealer stands on soft 17
    value = hand_value(dealer_hand)
    if value < 17:
        return True
    return False

def initial_state(bet: int) -> dict:
    deck = new_deck()
    player = [deck.pop(), deck.pop()]
    dealer = [deck.pop(), deck.pop()]

    state = {
        "status": "playing",
        "bet": bet,
        "deck": deck,
        "player_hand": player,
        "dealer_hand": dealer,
        "message": "",
        "payout": 0,
        "can_double": True,
    }

    # Handle immediate blackjack outcomes
    if is_blackjack(player) and is_blackjack(dealer):
        state["status"] = "finished"
        state["message"] = "Push — both blackjack."
        state["payout"] = bet  # return bet
    elif is_blackjack(player):
        state["status"] = "finished"
        state["message"] = "Blackjack! You win 3:2."
        state["payout"] = bet + int(bet * 1.5)  # bet back + winnings
    elif is_blackjack(dealer):
        state["status"] = "finished"
        state["message"] = "Dealer blackjack. You lose."
        state["payout"] = 0
    return state

def hit(state: dict) -> dict:
    if state.get("status") != "playing":
        return state
    deck = state["deck"]
    state["player_hand"].append(deck.pop())
    state["can_double"] = False
    pv = hand_value(state["player_hand"])
    if pv > 21:
        state["status"] = "finished"
        state["message"] = "Bust. You lose."
        state["payout"] = 0
    return state

def stand(state: dict) -> dict:
    if state.get("status") != "playing":
        return state
    state["can_double"] = False
    deck = state["deck"]
    # Dealer draws
    while dealer_should_hit(state["dealer_hand"]):
        state["dealer_hand"].append(deck.pop())

    pv = hand_value(state["player_hand"])
    dv = hand_value(state["dealer_hand"])

    if dv > 21:
        state["status"] = "finished"
        state["message"] = "Dealer busts. You win!"
        state["payout"] = state["bet"] * 2
    elif pv > dv:
        state["status"] = "finished"
        state["message"] = "You win!"
        state["payout"] = state["bet"] * 2
    elif pv < dv:
        state["status"] = "finished"
        state["message"] = "Dealer wins."
        state["payout"] = 0
    else:
        state["status"] = "finished"
        state["message"] = "Push."
        state["payout"] = state["bet"]
    return state

def double_down(state: dict) -> dict:
    if state.get("status") != "playing":
        return state
    if not state.get("can_double"):
        return state
    state["bet"] = int(state["bet"]) * 2
    state["can_double"] = False
    deck = state["deck"]
    state["player_hand"].append(deck.pop())
    # then auto stand
    return stand(state)
