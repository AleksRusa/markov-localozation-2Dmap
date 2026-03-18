import random

class Robot:
    def __init__(self, game_map, motion_model, sensor_model, belief):
        self.game_map = game_map
        self.motion = motion_model
        self.sensor = sensor_model
        self.belief = belief

        floor_hexs = game_map.get_all_floor_hexs()
        self.true_r, self.true_q = random.choice(floor_hexs)
        self.true_theta = random.randint(0, 5)

        self.direction = self.true_theta * 60
        self.grid_r = self.true_r
        self.grid_q = self.true_q
        self.coordinate = game_map.hex_to_pixel(self.true_r, self.true_q)
        self.front_neighbor = self._get_front_neighbor()
    
    def _get_front_neighbor(self):
        fr, fq = self.game_map.neighbor(self.true_r, self.true_q, self.true_theta)
        if not self.game_map.is_wall(fr, fq):
            class NeighborWrapper:
                def __init__(self):
                    self.q = fq
                    self.r = fr
            return NeighborWrapper()
        return None
    
    def _update_from_true(self):
        self.direction = self.true_theta * 60
        self.grid_r = self.true_r
        self.grid_q = self.true_q
        self.coordinate = self.game_map.hex_to_pixel(self.true_r, self.true_q)
        self.front_neighbor = self._get_front_neighbor()
    
    def turn(self, target_dir):
        self.true_theta = self.motion.sample_turn(self.true_theta, target_dir)
        self.belief.update_by_turn(target_dir, self.motion)
        self._update_from_true()
        return self.true_theta
    
    def move_forward(self):
        self.true_r, self.true_q = self.motion.sample_move(
            self.true_r, self.true_q, self.true_theta, self.game_map
        )
        self.belief.update_by_move(self.motion)
        self._update_from_true()
        return self.true_r, self.true_q
    
    def sense(self):
        color = self.sensor.sample_color_measurement(self.true_r, self.true_q, self.game_map)
        wall = self.sensor.sample_wall_measurement(
            self.true_r, self.true_q, self.true_theta, self.game_map
        )
        self.belief.update_by_sense(color, wall)
        return color, wall
    
    def teleport_random(self):
        floor_hexs = self.game_map.get_all_floor_hexs()
        self.true_r, self.true_q = random.choice(floor_hexs)
        self.true_theta = random.randint(0, 5)
        self.belief._init_uniform()
        self._update_from_true()
    
    def get_status(self):
        return (self.belief.get_most_probable_hex(), self.belief.get_confidence())

    def forward(self):
        return self.move_forward()
    
    def rotate(self, angle):
        if angle == 60:
            return self.turn(1)
        elif angle == -60:
            return self.turn(5)
        return None