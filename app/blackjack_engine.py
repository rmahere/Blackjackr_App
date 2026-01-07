from __future__ import annotations

import random

SUITS = ["♠", "♥", "♦", "♣"]
RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]


def new_deck() -> list[dict]:
    deck = [{"rank": r, "suit": s} for s in SUITS for r in RANKS]
    random.shuffle(deck)
    return deck


def hand_value(hand: list[dict]) -> int:
    # Aces count as 11, then reduce as needed
    value = 0
    aces = 0
    for c in hand:
        r = c["rank"]
        if r == "A":
            value += 11
            aces += 1
        elif r in ("K", "Q", "J"):
            value += 10
        else:
            value += int(r)
    while value > 21 and aces > 0:
        value -= 10
        aces -= 1
    return value


def is_blackjack(hand: list[dict]) -> bool:
    return len(hand) == 2 and hand_value(hand) == 21


def dealer_play(deck: list[dict], dealer_hand: list[dict]) -> tuple[list[dict], list[dict]]:
    # Dealer stands on soft 17 (i.e., value >= 17)
    while hand_value(dealer_hand) < 17:
        dealer_hand.append(deck.pop())
    return deck, dealer_hand


def start_round(bet: int) -> dict:
    deck = new_deck()
    player = [deck.pop(), deck.pop()]
    dealer = [deck.pop(), deck.pop()]

    state = {
        "deck": deck,
        "bet": bet,
        "status": "playing",
        "player_hand": player,
        "dealer_hand": dealer,
        "message": "Round started.",
        "payout": 0,
        "reveal_dealer": False,
        "can_double": True,
    }

    # Check blackjack
    if is_blackjack(player):
        # Dealer also blackjack -> push
        if is_blackjack(dealer):
            state["status"] = "finished"
            state["reveal_dealer"] = True
            state["message"] = "Push. Both blackjack."
            state["payout"] = bet  # return bet
        else:
            state["status"] = "finished"
            state["reveal_dealer"] = True
            state["message"] = "Blackjack! You win 3:2."
            state["payout"] = int(bet * 2.5)  # bet back + 1.5x
    return state


def hit(state: dict) -> dict:
    if state.get("status") != "playing":
        return state
    state["can_double"] = False
    deck = state["deck"]
    state["player_hand"].append(deck.pop())

    pv = hand_value(state["player_hand"])
    if pv > 21:
        state["status"] = "finished"
        state["reveal_dealer"] = True
        state["message"] = "Bust. You lose."
        state["payout"] = 0
    return state


def stand(state: dict) -> dict:
    if state.get("status") != "playing":
        return state
    state["can_double"] = False
    state["reveal_dealer"] = True

    deck = state["deck"]
    dealer = state["dealer_hand"]
    deck, dealer = dealer_play(deck, dealer)
    state["deck"] = deck
    state["dealer_hand"] = dealer

    pv = hand_value(state["player_hand"])
    dv = hand_value(dealer)

    bet = int(state.get("bet") or 0)

    if dv > 21:
        state["status"] = "finished"
        state["message"] = "Dealer busts. You win!"
        state["payout"] = bet * 2
    elif pv > dv:
        state["status"] = "finished"
        state["message"] = "You win!"
        state["payout"] = bet * 2
    elif pv < dv:
        state["status"] = "finished"
        state["message"] = "Dealer wins."
        state["payout"] = 0
    else:
        state["status"] = "finished"
        state["message"] = "Push."
        state["payout"] = bet

    return state


def double_down(state: dict) -> dict:
    if state.get("status") != "playing":
        return state
    if not state.get("can_double"):
        return state

    state["bet"] = int(state.get("bet") or 0) * 2
    state["can_double"] = False

    # one card then stand
    deck = state["deck"]
    state["player_hand"].append(deck.pop())
    state["deck"] = deck

    pv = hand_value(state["player_hand"])
    if pv > 21:
        state["status"] = "finished"
        state["reveal_dealer"] = True
        state["message"] = "Bust on double. You lose."
        state["payout"] = 0
        return state

    return stand(state)
