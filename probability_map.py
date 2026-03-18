class Belief:
    def __init__(self, game_map):
        self.game_map = game_map
        self.width = game_map.width
        self.height = game_map.height
        self.turn_belief = {}
        self.hex_belief = {}
        self._init_uniform()
    
    def _init_uniform(self):
        floor_hexs = self.game_map.get_all_floor_hexs()
        n_hexs = len(floor_hexs)
        prob_per_hex = 1.0 / n_hexs
        prob_per_state = 1.0 / 6

        for r, q in floor_hexs:
            self.hex_belief[(r, q)] = prob_per_hex
        for theta in range(6):
            self.turn_belief[theta] = prob_per_state
    
    def normalize_hex(self):
        total_hex_belief = sum(self.hex_belief.values())
        
        if total_hex_belief == 0:
            self._init_uniform()
            return
        
        for key in self.hex_belief:
            self.hex_belief[key] /= total_hex_belief
        
    def normalize_turn(self):
        total_turn_belief = sum(self.turn_belief.values())

        for key in self.turn_belief:
            self.turn_belief[key] /= total_turn_belief
    
    def update_by_turn(self, target_dir, motion_model):
        new_belief = {}
        for theta, prob in self.turn_belief.items():
            transitions = motion_model.get_turn_distribution(theta, target_dir)
            for new_theta, trans_prob in transitions.items():
                new_belief[new_theta] = new_belief.get(new_theta, 0) + prob * trans_prob
        self.turn_belief = new_belief
        self.normalize_turn()
    
    def update_by_move(self, motion_model):
        new_belief = {}
        for (r, q), hex_prob in self.hex_belief.items():
            new_prob = 0
            for theta, turn_prob in self.turn_belief.items():
                jump_prob = motion_model.get_move_distribution(r, q, theta, self.game_map)
                new_prob += (hex_prob * jump_prob[0] * turn_prob)
                
                theta_opposite = (theta + 3) % 6
                theta_opposite_prob = self.turn_belief[theta_opposite]

                r1, q1 = self.game_map.neighbor(r, q, theta)
                if not self.game_map.is_wall(r1, q1):
                    neigbor1_hex_prob = self.hex_belief[(r1, q1)]
                    neigbor1_jump_prob = motion_model.get_move_distribution(r1, q1, theta_opposite, self.game_map)
                    new_prob += (neigbor1_hex_prob * theta_opposite_prob * neigbor1_jump_prob[1])
                else:
                    continue

                r2, q2 = self.game_map.neighbor(r1, q1, theta)
                if not self.game_map.is_wall(r2, q2):
                    neigbor2_hex_prob = self.hex_belief[(r2, q2)]
                    neigbor2_jump_prob = motion_model.get_move_distribution(r2, q2, theta_opposite, self.game_map)
                    new_prob += (neigbor2_hex_prob * theta_opposite_prob * neigbor2_jump_prob[2])
                else:
                    continue
            new_belief[r, q] = new_prob
            self.normalize_hex()
        self.hex_belief = new_belief
        
    def update_by_sense(self, color_measurement, wall_measurement):
        color_probs = {
            'correct': 0.9,
            'error': 0.1 
        }
        wall_probs = {
            'correct': 0.95,
            'error': 0.05 
        }

        for (r, q), prob in list(self.hex_belief.items()):
            true_color = self.game_map.get_true_color(r, q)
            if true_color is not None:
                if color_measurement == true_color:
                    self.hex_belief[(r, q)] = prob * color_probs['correct']
                else:
                    self.hex_belief[(r, q)] = prob * color_probs['error']
        self.normalize_hex()

        hex_theta_belief_map = {}
        for (r, q), hex_prob in self.hex_belief.items():
            for theta, turn_prob in self.turn_belief.items():
                hex_theta_belief_map[(r, q, theta)] = hex_prob * turn_prob

        for (r, q, theta), prob in hex_theta_belief_map.items():
            nr, nq = self.game_map.neighbor(r, q, theta)
            wall_ahead = self.game_map.is_wall(nr, nq)
            
            if wall_measurement == wall_ahead:
                hex_theta_belief_map[(r, q, theta)] = prob * wall_probs['correct']
            else:
                hex_theta_belief_map[(r, q, theta)] = prob * wall_probs['error']

        new_hex_belief = {}
        new_turn_belief = {}
        for (r, q, theta), prob in hex_theta_belief_map.items():
            if (r, q) in new_hex_belief:
                new_hex_belief[(r, q)] += prob
            else:
                new_hex_belief[(r, q)] = prob
            
            if theta in new_turn_belief:
                new_turn_belief[theta] += prob
            else:
                new_turn_belief[theta] = prob
        self.hex_belief = new_hex_belief
        self.turn_belief = new_turn_belief

        self.normalize_hex()
        self.normalize_turn()
    
    def get_most_probable_hex(self):
        return max(self.hex_belief.items(), key=lambda x: x[1])[0] if self.hex_belief else None
    
    def get_confidence(self):
        hex = self.get_most_probable_hex()
        return self.hex_belief.get(hex, 0) if hex else 0
    
    def get_matrix(self):
        matrix = [[0.0 for _ in range(self.width)] for _ in range(self.height)]
        for (r, q), prob in self.hex_belief.items():
            matrix[r][q] = prob
        return matrix