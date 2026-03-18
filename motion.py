import random

class MotionModel:
    def __init__(self, jump_1=0.8, jump_0=0.1, jump_2=0.1,
                 turn_exact=0.9, turn_error=0.05):
        self.move_probs = [jump_0, jump_1, jump_2]
        self.turn_exact = turn_exact
        self.turn_error = turn_error

    def get_turn_distribution(self, current_theta, target_dir):
        result = {}

        exact_theta = (current_theta + target_dir) % 6
        result[exact_theta] = self.turn_exact
    
        over_theta = (exact_theta + 1) % 6
        result[over_theta] = result.get(over_theta, 0.0) + self.turn_error

        under_theta = (exact_theta - 1) % 6
        result[under_theta] = result.get(under_theta, 0.0) + self.turn_error
        
        return result
    
    def get_move_distribution(self, r, q, theta, game_map):
        result = [0.0, 0.0, 0.0]
        jump_0, jump_1, jump_2 = self.move_probs

        result[0] = jump_0

        r1, q1 = game_map.neighbor(r, q, theta)
        if not game_map.is_wall(r1, q1):
            result[1] = jump_1
        else:
            result[0] += (jump_1 + jump_2)
            return result

        r2, q2 = game_map.neighbor(r1, q1, theta)
        if not game_map.is_wall(r2, q2):
            result[2] = jump_2
        else:
            result[1] += jump_2
        return result
    
    def sample_move(self, r, q, theta, game_map):

        nr1, nq1 = game_map.neighbor(r, q, theta)
        can_move_1 = not game_map.is_wall(nr1, nq1)
        can_move_2 = can_move_1 and not game_map.is_wall(*game_map.neighbor(nr1, nq1, theta))
        
        rand = random.random()
        if rand < self.move_probs[0]:
            steps = 0
        elif rand < self.move_probs[0] + self.move_probs[1]:
            steps = 1
        else:
            steps = 2

        if steps == 1 and not can_move_1:
            steps = 0
        elif steps == 2:
            if not can_move_2:
                steps = 1 if can_move_1 else 0

        cr, cq = r, q
        for _ in range(steps):
            cr, cq = game_map.neighbor(cr, cq, theta)
        return cr, cq
    
    def sample_turn(self, current_theta, target_dir):
        rand = random.random()
        if rand < self.turn_exact:
            return (current_theta + target_dir) % 6
        elif rand < self.turn_exact + self.turn_error:
            return (current_theta + target_dir + 1) % 6
        else:
            return (current_theta + target_dir - 1) % 6