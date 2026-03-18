import random
from collections import deque

import numpy as np

from const import *

class HexMap:
    # Направления: 0=восток, 1=северо-восток, 2=северо-запад, 3=запад, 4=юго-запад, 5=юго-восток
    directions = [[(0,1), (0,1)], [(-1,0), (-1, 1)], [(-1,-1), (-1,0)], [(0,-1), (0,-1)], [(1,-1), (1, 0)], [(1,0), (1, 1)]]
    
    def __init__(self, width, height, wall_ratio=0.2):
        self.width = width
        self.height = height
        self.hexs = {}
    
        for q in range(width):
            for r in range(height):
                color = random.choice(['red', 'green'])
                self.hexs[(r, q)] = {'type': 'floor', 'color': color}
        
        n_walls = int(width * height * wall_ratio)
        all_positions = list(self.hexs.keys())
        random.shuffle(all_positions)
        for i in range(n_walls):
            r, q = all_positions[i]
            self.hexs[(r, q)]['type'] = 'wall'
            self.hexs[(r, q)]['color'] = None
        
        self._ensure_connectivity()
        self._compute_dimensions()
    
    def _compute_dimensions(self):
        max_x = 0
        max_y = 0
        for r, q in self.hexs:
            x, y = self.hex_to_pixel(r, q)
            max_x = max(max_x, x)
            max_y = max(max_y, y)
        self.map_width = int(max_x + HEX_SIZE*2)
        self.map_height = int(max_y + HEX_SIZE*2)
    
    def _ensure_connectivity(self):
        """BFS для связности"""
        floor_hexs = [(r, q) for (r, q), hex in self.hexs.items() if hex['type'] == 'floor']
        if not floor_hexs:
            return
        
        start = floor_hexs[len(floor_hexs)//2]
        visited = {start}
        queue = deque([start])
        
        while queue:
            r, q = queue.popleft()
            for direction in range(len(self.directions)):
                nr, nq = self.neighbor(r, q, direction)
                if (nr, nq) in self.hexs and self.hexs[(nr, nq)]['type'] == 'floor' and (nr, nq) not in visited:
                    visited.add((nr, nq))
                    queue.append((nr, nq))

        for r, q in floor_hexs:
            if (r, q) not in visited:
                self.hexs[(r, q)]['type'] = 'wall'
                self.hexs[(r, q)]['color'] = None
    
    def is_wall(self, r, q):
        return (r, q) not in self.hexs or self.hexs[(r, q)]['type'] == 'wall'
    
    def get_true_color(self, r, q):
        if self.is_wall(r, q):
            return None
        return self.hexs[(r, q)]['color']
    
    def neighbor(self, r, q, direction):
        if r % 2 == 0:
            dr, dq = self.directions[direction][0]
        else:
            dr, dq = self.directions[direction][1]
        return r + dr, q + dq
    
    def get_all_floor_hexs(self):
        return [(r, q) for (r, q), hex in self.hexs.items() if hex['type'] == 'floor']
    
    def hex_to_pixel(self, r, q):
        x = HEX_SIZE * np.sqrt(3) * (q + 0.5 * (r % 2))
        y = HEX_SIZE * 1.5 * r
        return x, y