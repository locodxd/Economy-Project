import random
from typing import List, Tuple

RANKS = ['A'] + [str(i) for i in range(2, 11)] + ['J', 'Q', 'K']
SUITS = ['♠', '♥', '♦', '♣']


def create_deck() -> List[str]:
    deck = [f"{rank}{suit}" for rank in RANKS for suit in SUITS]
    random.shuffle(deck)
    return deck


def card_value(card: str) -> int:
    rank = card[:-1]
    if rank in ['J', 'Q', 'K']:
        return 10
    if rank == 'A':
        return 11
    return int(rank)


def hand_value(hand: List[str]) -> int:
    # Calculate best blackjack value considering aces as 11 or 1
    total = 0
    aces = 0
    for c in hand:
        v = card_value(c)
        total += v
        if c[:-1] == 'A':
            aces += 1

    while total > 21 and aces:
        total -= 10
        aces -= 1

    return total


def draw_card(deck: List[str], n: int = 1) -> Tuple[List[str], List[str]]:
    drawn = []
    for _ in range(n):
        if not deck:
            deck = create_deck()
        drawn.append(deck.pop())
    return drawn, deck


def format_hand(hand: List[str]) -> str:
    return ' '.join(hand)
