def predict_duration(priority, current_load):
    priority_weights = {
        'low': 1.2,
        'normal': 1.0,
        'high': 0.8,
        'critical': 0.6
    }

    p_weight = priority_weights.get(priority.lower(), 1.0)
    base_time = 9
    estimated_time = base_time * p_weight
    return estimated_time
