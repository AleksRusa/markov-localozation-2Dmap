import random

class SensorModel:
    def __init__(self, p_correct_color=0.9, p_correct_wall=0.95):
        self.p_correct_color = p_correct_color
        self.p_error_color = 1 - p_correct_color
        
        self.p_correct_wall = p_correct_wall
        self.p_false_wall = 1 - p_correct_wall
    
    def sample_color_measurement(self, r, q, game_map):
        true_color = game_map.get_true_color(r, q)
        if random.random() < self.p_correct_color:
            return true_color
        return 'red' if true_color == 'green' else 'green'

    def sample_wall_measurement(self, r, q, theta, game_map):
        nr, nq = game_map.neighbor(r, q, theta)
        wall_ahead = game_map.is_wall(nr, nq)
        
        prob = random.random()
        if wall_ahead:
            if prob <= self.p_correct_wall:
                return True
            return False
        else:
            if prob >= self.p_false_wall:
                return False
            return True
