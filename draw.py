import pygame
import numpy as np

from const import *


def draw_hex(surface, color, center, alpha=255):
    x, y = center
    points = []
    for i in range(6):
        angle_deg = 60 * i - 30
        angle_rad = np.pi / 180 * angle_deg
        px = x + HEX_SIZE * np.cos(angle_rad)
        py = y + HEX_SIZE * np.sin(angle_rad)
        points.append((px, py))
    
    if alpha < 255:
        s = pygame.Surface((HEX_SIZE*2, HEX_SIZE*2), pygame.SRCALPHA)
        s.set_alpha(alpha)
        pygame.draw.polygon(s, color, [(p[0]-x+HEX_SIZE, p[1]-y+HEX_SIZE) for p in points])
        surface.blit(s, (x-HEX_SIZE, y-HEX_SIZE))
    else:
        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, BLACK, points, 1)


def draw_robot_custom(surface, pos, theta, game_map, r, q, off_x, off_y):
    x, y = pos

    pygame.draw.circle(surface, ROBOT_COLOR, (int(x), int(y)), int(HEX_SIZE * 0.4))
    pygame.draw.circle(surface, BLACK, (int(x), int(y)), int(HEX_SIZE * 0.4), 2)
    
    fr, fq = game_map.neighbor(r, q, theta)
    if not game_map.is_wall(fr, fq):
        f_center = game_map.hex_to_pixel(fr, fq)
        fx = off_x + f_center[0]
        fy = off_y + f_center[1]
        
        dx = fx - x
        dy = fy - y
        dist = np.hypot(dx, dy)
        if dist > 0:
            ndx = dx / dist
            ndy = dy / dist
            arrow_len = HEX_SIZE * 0.8
            end_x = x + ndx * arrow_len
            end_y = y + ndy * arrow_len
            
            pygame.draw.line(surface, ROBOT_DIR, (x, y), (end_x, end_y), 3)
            
            angle = np.arctan2(dy, dx)
            left_x = end_x - 5 * np.cos(angle - np.pi/6)
            left_y = end_y - 5 * np.sin(angle - np.pi/6)
            right_x = end_x - 5 * np.cos(angle + np.pi/6)
            right_y = end_y - 5 * np.sin(angle + np.pi/6)
            pygame.draw.polygon(surface, ROBOT_DIR, 
                                [(end_x, end_y), (left_x, left_y), (right_x, right_y)])


def draw_map_custom(surface, game_map, offset, robot=None, belief=None, show_belief=False,
                    highlight_front_color=None, confidence_threshold=None):
    font = pygame.font.SysFont('Arial', 14) 
    off_x, off_y = offset

    for (r, q), cell in game_map.hexs.items():
        center = game_map.hex_to_pixel(r, q)
        x = off_x + center[0]
        y = off_y + center[1]
        
        if cell['type'] == 'wall':
            color = WALL_COLOR
        else:
            if cell['color'] == 'red':
                color = RED
            else:
                color = GREEN
        draw_hex(surface, color, (x, y))
    
    if show_belief and belief is not None:
        max_prob = max(belief.hex_belief.values()) if belief.hex_belief else 1
        
        for (r, q), prob in belief.hex_belief.items():
            if prob > 0 and not game_map.is_wall(r, q):
                center = game_map.hex_to_pixel(r, q)
                x = off_x + center[0]
                y = off_y + center[1]
                
                radius = int(HEX_SIZE * 0.6 * (prob / max_prob))
                if radius > 0:
                    s = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                    pygame.draw.circle(s, (*PROB_COLOR, 180), (radius, radius), radius)
                    surface.blit(s, (int(x - radius), int(y - radius)))
        
        for (r, q), prob in belief.hex_belief.items():
            if prob > 0 and not game_map.is_wall(r, q):
                center = game_map.hex_to_pixel(r, q)
                x = off_x + center[0]
                y = off_y + center[1]
                text = f"{prob:.2f}"
                text_surface = font.render(text, True, BLACK)
                text_rect = text_surface.get_rect(center=(x, y))
                surface.blit(text_surface, text_rect)
        
        most_prob = belief.get_most_probable_hex()
        if most_prob:
            confidence = belief.get_confidence()
            if confidence_threshold is not None and confidence >= confidence_threshold:
                border_color = GREEN
            else:
                border_color = NEIGHBOR_COLOR
            
            r, q = most_prob
            center = game_map.hex_to_pixel(r, q)
            x = off_x + center[0]
            y = off_y + center[1]
            
            points = []
            for i in range(6):
                angle_deg = 60 * i - 30
                angle_rad = np.pi / 180 * angle_deg
                px = x + (HEX_SIZE+3) * np.cos(angle_rad)
                py = y + (HEX_SIZE+3) * np.sin(angle_rad)
                points.append((px, py))
            pygame.draw.polygon(surface, border_color, points, 3)
    
    if robot:
        r, q, theta = robot.true_r, robot.true_q, robot.true_theta
        center = game_map.hex_to_pixel(r, q)
        x = off_x + center[0]
        y = off_y + center[1]
        
        if show_belief:
            s = pygame.Surface((HEX_SIZE, HEX_SIZE), pygame.SRCALPHA)
            pygame.draw.circle(s, (*ROBOT_COLOR, 100), (HEX_SIZE//2, HEX_SIZE//2), int(HEX_SIZE*0.4))
            surface.blit(s, (int(x - HEX_SIZE//2), int(y - HEX_SIZE//2)))
        else:
            draw_robot_custom(surface, (x, y), theta, game_map, r, q, off_x, off_y)
    
    if highlight_front_color is not None and robot is not None:
        fr, fq = game_map.neighbor(robot.true_r, robot.true_q, robot.true_theta)
        if not game_map.is_wall(fr, fq):
            center = game_map.hex_to_pixel(fr, fq)
            x = off_x + center[0]
            y = off_y + center[1]
            points = []
            for i in range(6):
                angle_deg = 60 * i - 30
                angle_rad = np.pi / 180 * angle_deg
                px = x + HEX_SIZE * np.cos(angle_rad)
                py = y + HEX_SIZE * np.sin(angle_rad)
                points.append((px, py))
            pygame.draw.polygon(surface, highlight_front_color, points, 3)


def draw_direction_belief(screen, center_x, center_y, belief, robot, font):
    R = 36
    dir_hex_size = R * 1.5
    dir_probs = belief.turn_belief
    directions = sorted(dir_probs.keys(), reverse=True)

    max_prob = max(dir_probs.values())
    if max_prob == 0:
        max_prob = 1

    vertices = []
    for i in range(6):
        angle_rad = np.radians(60 * i + 30)
        px = center_x + dir_hex_size * np.cos(angle_rad)
        py = center_y + dir_hex_size * np.sin(angle_rad)
        vertices.append((px, py))

    BASE_COLOR = (200, 210, 55)
    EDGE_COLOR = (100, 100, 100)
    MIN_BRIGHT = 0.3 

    small_font = pygame.font.SysFont(None, max(8, int(font.get_height() * 0.8)))

    for i, angle_key in enumerate(directions):
        prob = dir_probs.get(angle_key, 0.0)
        brightness = MIN_BRIGHT + (1 - MIN_BRIGHT) * (prob / max_prob)
        color = tuple(int(c * brightness) for c in BASE_COLOR)
        v1 = vertices[i]
        v2 = vertices[(i + 1) % 6]
        triangle = [(center_x, center_y), v1, v2]

        pygame.draw.polygon(screen, color, triangle)
        pygame.draw.polygon(screen, EDGE_COLOR, triangle, 1)

        text_angle = np.radians(60 * (i + 1))
        text_x = center_x + dir_hex_size * 0.6 * np.cos(text_angle)
        text_y = center_y + dir_hex_size * 0.6 * np.sin(text_angle)

        avg_bright = sum(color) / 3
        text_color = (0, 0, 0) if avg_bright > 128 else (255, 255, 255)

        label = small_font.render(str(angle_key*60), True, text_color)
        screen.blit(label, label.get_rect(center=(text_x, text_y)))

        if robot is not None and angle_key == robot.direction:
            pygame.draw.polygon(screen, (0, 0, 0), triangle, 2)

    pygame.draw.polygon(screen, (0, 0, 0), vertices, 2)

    title_font = pygame.font.SysFont('Arial', 24)
    title = title_font.render("Убеждение направления", True, (0, 0, 0))
    screen.blit(title, (center_x - title.get_width() // 2, center_y - dir_hex_size - 25))

class TextInput:
    def __init__(self, x, y, w, h, label, default_text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label
        self.text = default_text
        self.active = False
        self.color_inactive = GRAY
        self.color_active = GREEN

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                if event.unicode.isdigit() or (event.unicode == '.' and '.' not in self.text):
                    self.text += event.unicode

    def draw(self, screen, font):
        color = self.color_active if self.active else self.color_inactive
        pygame.draw.rect(screen, color, self.rect, 2)
        txt_surface = font.render(self.text, True, BLACK)
        screen.blit(txt_surface, (self.rect.x + 5, self.rect.y + 5))
        label_surface = font.render(self.label, True, BLACK)
        screen.blit(label_surface, (self.rect.x, self.rect.y - 30))
