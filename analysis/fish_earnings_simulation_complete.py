import json
from concurrent.futures import ProcessPoolExecutor
from src.fishing.fish_library import FishLibrary, PRESTIGE_BONUS

FL = FishLibrary.get_instance()

ITERATIONS = 1000000
WORKERS = 10

BAIT_COST = [0, 7, 50, 150, 600, 1200]
PRESTIGE_LEVEL = 0

def catch_fish_and_calculate_earnings(iterations, bait_level: int, rod_level: int):
    money = 0
    for _ in range(iterations):
        fish = FL.random_fish_entry(rod_level=rod_level, bait_level=bait_level)
        if fish:
            money += fish.price + fish.price * PRESTIGE_BONUS[PRESTIGE_LEVEL]
    return money

# Determines the average money earned per 5 minutes
def main():
    final_result = []
    for rod_level in range(1, 5):
        bait_result = []
        for bait_level in range(6):
            iterations_per_worker = ITERATIONS // WORKERS

            with ProcessPoolExecutor(max_workers=WORKERS) as executor:
                futures = [executor.submit(catch_fish_and_calculate_earnings, iterations_per_worker, bait_level, rod_level) for _ in range(WORKERS)]
                total_money = sum(f.result() for f in futures)

            total_bait_cost = ITERATIONS * BAIT_COST[bait_level]
            bait_result.append((total_money - total_bait_cost) / ITERATIONS)
        final_result.append(bait_result)
    print(json.dumps(final_result, indent=4))