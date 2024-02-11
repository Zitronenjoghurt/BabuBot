import numpy as np

def bell_curve_random(min: float, max: float) -> float:
    mean = (min + max) / 2.0
    
    std_dev = 0.33 * mean
    
    random_number = np.random.normal(loc=mean, scale=std_dev)
    
    while random_number < min or random_number > max:
        random_number = np.random.normal(loc=mean, scale=std_dev)
    
    return random_number