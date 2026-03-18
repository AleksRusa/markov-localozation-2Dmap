import pygame

from const import *
from draw import TextInput, draw_direction_belief, draw_map_custom
from map import HexMap
from robot import Robot
from sensor import SensorModel
from probability_map import Belief
from motion import MotionModel


def main():
    pygame.init()
    
    FONT = pygame.font.SysFont('Arial', 36)
    S_FONT = pygame.font.SysFont('Arial', 24)
    
    input_q = TextInput(100, 100, 200, 32, 'Количество столбцов', DEF_Q)
    input_r = TextInput(100, 160, 200, 32, 'Количество рядов', DEF_R)
    input_rad = TextInput(100, 220, 200, 32, 'Длина стороны гексагона', DEF_RADIUS)
    input_prob = TextInput(400, 100, 200, 32, 'Вероятность красных', DEF_PROB)
    input_wall = TextInput(400, 160, 200, 32, 'Количество препятствий', DEF_WALLS)
    inputs = [input_q, input_r, input_rad, input_prob, input_wall]
    
    state = MENU
    screen = pygame.display.set_mode((MENU_WIDTH, MENU_HEIGHT))
    pygame.display.set_caption("Локализация робота")
    clock = pygame.time.Clock()
    
    game_map = None
    robot = None
    belief = None
    motion = None
    sensor = None
    confidence_threshold = 0.9
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if state == MENU:
                for inp in inputs:
                    inp.handle_event(event)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if BUTTON_RECT.collidepoint(event.pos):
                        try:
                            q_val = int(input_q.text) if input_q.text else 0
                            r_val = int(input_r.text) if input_r.text else 0
                            rad_val = int(input_rad.text) if input_rad.text else 0
                            prob_val = float(input_prob.text) if input_prob.text else 0
                            wall_val = int(input_wall.text) if input_wall.text else 0
                            
                            if q_val > 0 and r_val > 0 and rad_val > 0:
                                game_map = HexMap(q_val, r_val, wall_ratio=wall_val/(q_val*r_val))
                                
                                motion = MotionModel()
                                sensor = SensorModel(p_correct_color=0.9, p_correct_wall=0.95)
                                belief = Belief(game_map)
                                robot = Robot(game_map, motion, sensor, belief)
                                
                                win_width = game_map.map_width * 2 + 300
                                win_height = game_map.map_height + 200
                                screen = pygame.display.set_mode((win_width, win_height))
                                pygame.display.set_caption(f"Карта {q_val}x{r_val} | Локализация робота")
                                state = GAME
                        except ValueError:
                            pass

            elif state == GAME:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        screen = pygame.display.set_mode((MENU_WIDTH, MENU_HEIGHT))
                        pygame.display.set_caption("Локализация робота")
                        state = MENU
                    elif event.key == pygame.K_UP:
                        robot.move_forward()
                        print(f"Движение вперёд, новая позиция: ({robot.true_q}, {robot.true_r})")
                    elif event.key == pygame.K_RIGHT:
                        robot.turn(1)
                        print(f"Поворот вправо, новое направление: {robot.true_theta*60}°")
                    elif event.key == pygame.K_LEFT:
                        robot.turn(5)
                        print(f"Поворот влево, новое направление: {robot.true_theta*60}°")
                    elif event.key == pygame.K_DOWN:
                        color, wall = robot.sense()
                        if color and wall is not None:
                            print(f"Измерение: цвет {color}, стена впереди: {wall}")
                    elif event.key == pygame.K_t:
                        robot.teleport_random()
                        print("Телепорт в случайную позицию")

        screen.fill(GRAY_BACKGROUND)

        if state == MENU:
            title = FONT.render("Настройка симуляции", True, BLACK)
            screen.blit(title, (200, 20))

            for inp in inputs:
                inp.draw(screen, S_FONT)

            pygame.draw.rect(screen, GREEN, BUTTON_RECT)
            pygame.draw.rect(screen, BLACK, BUTTON_RECT, 2)
            btn_text = FONT.render("Старт", True, BLACK)
            screen.blit(btn_text, (BUTTON_RECT.x + 33, BUTTON_RECT.y))

        elif state == GAME:
            label_left = S_FONT.render("Реальная позиция", True, BLACK)
            label_right = S_FONT.render("Вероятностное распределение", True, BLACK)

            left_x = game_map.map_width // 2 - label_left.get_width() // 2
            right_x = game_map.map_width + SPACE + game_map.map_width // 2 - label_right.get_width() // 2
            y_pos = 6

            screen.blit(label_left, (left_x, y_pos))
            screen.blit(label_right, (right_x, y_pos))

            draw_map_custom(
                screen, game_map, (20, 30), robot=robot, show_belief=False,
                confidence_threshold=confidence_threshold, highlight_front_color=NEIGHBOR_COLOR
            )
            
            draw_map_custom(
                screen, game_map, (game_map.map_width + SPACE + 20, 30), 
                robot=robot, belief=belief, show_belief=True,
                confidence_threshold=confidence_threshold
            )
            
            direction_center_x = (game_map.map_width + 30) 
            direction_center_y = game_map.map_height + 100
            draw_direction_belief(screen, direction_center_x, direction_center_y, belief, robot, S_FONT)
            
            confidence = belief.get_confidence()
            most_prob = belief.get_most_probable_hex()
            if most_prob:
                status_text = f"Уверенность: {confidence:.3f} | Наиболее вероятная позиция: (q={most_prob[1]}, r={most_prob[0]})"
            else:
                status_text = f"Уверенность: {confidence:.3f}"
            
            if confidence >= confidence_threshold:
                status_text += " - ЛОКАЛИЗОВАН!"
                color = GREEN
            else:
                color = BLACK
                
            text_surface = S_FONT.render(status_text, True, color)
            screen.blit(text_surface, (20, game_map.map_height + 60))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()