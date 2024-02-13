import json
from concurrent.futures import ProcessPoolExecutor
from src.fishing.fish_library import FishLibrary, PRESTIGE_BONUS

FL = FishLibrary.get_instance()

ITERATIONS = 1000000
WORKERS = 10

ROD_LEVEL = 4
BAIT_LEVEL = 5
BAIT_COST = [0, 7, 50, 150, 600, 2000]
PRESTIGE_LEVEL = 0

def catch_fish_and_calculate_earnings(iterations):
    money = 0
    for _ in range(iterations):
        fish = FL.random_fish_entry(rod_level=ROD_LEVEL, bait_level=BAIT_LEVEL)
        if fish:
            money += fish.price + fish.price * PRESTIGE_BONUS[PRESTIGE_LEVEL]
    return money

# Determines the average money earned per 5 minutes
def main():
    iterations_per_worker = ITERATIONS // WORKERS
    with ProcessPoolExecutor(max_workers=WORKERS) as executor:
        futures = [executor.submit(catch_fish_and_calculate_earnings, iterations_per_worker) for _ in range(WORKERS)]
        total_money = sum(f.result() for f in futures)

    total_bait_cost = ITERATIONS * BAIT_COST[BAIT_LEVEL]
    result = (total_money - total_bait_cost) / ITERATIONS
    print(result)