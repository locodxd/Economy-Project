from random import random

def adjust_success_rate(base_chance: float) -> float:
    if random() < 0.1:  # 10% chance to decrease success rate
        return base_chance * 0.5
    return base_chance

def weighted_choice(choices: dict) -> str:
    total_weight = sum(choices.values())
    rand = random() * total_weight
    cumulative_weight = 0.0
    for choice, weight in choices.items():
        cumulative_weight += weight
        if rand < cumulative_weight:
            return choice
    return None  

def calculate_probability(successes: int, trials: int) -> float:
    """Calculates the probability of success."""
    if trials == 0:
        return 0.0
    return successes / trials

def simulate_event(chance: float) -> bool:
    return random() < chance