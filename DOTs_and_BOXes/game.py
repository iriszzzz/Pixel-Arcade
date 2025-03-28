import pygame 
import sys
import random
import DOTs_and_BOXes.game_over

# Initialize Pygamegame_over
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
BOARD_SIZE = 400
GRID_SIZE = 10  # Number of dots per side
AI_LEVEL = 2
# CELL_SIZE = 100
DOT_RADIUS = 6
LINE_WIDTH = 3
DASHED_LINE_WIDTH = 3
FONT_SIZE = 28
MARGIN = 50  # Minimum margin around the grid
BOARD_COLOR = (209, 209, 209)  # Light gray background for the board

RED = (245, 144, 127) #255, 0, 0 | 212, 90, 70
BLUE = (161, 194, 240) # 0, 0, 255
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (151, 151, 151) # hover line
GREEN = (60, 94, 39) # GREEN = (128, 128, 0) 87, 130, 60 | 120, 168, 98 | 137, 184, 116
BROWN = (120, 36, 23)
DARKRED = (122, 18, 0)
DARKBLUE = (3, 43, 89)

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dots and Boxes")

# Fonts
font = pygame.font.Font("DOTs_and_BOXes/resource/IMFellDoublePicaSC-Regular.ttf", FONT_SIZE) 
title_font = pygame.font.Font("DOTs_and_BOXes/resource/IMFellDoublePicaSC-Regular.ttf", 36)

# Icon
playerIcon = pygame.image.load("DOTs_and_BOXes/resource/user.png")
playerIcon = pygame.transform.scale(playerIcon, (30, 30))  # resize
computerIcon = pygame.image.load("DOTs_and_BOXes/resource/computer.png")
computerIcon = pygame.transform.scale(computerIcon, (30, 30))  
dotImage = pygame.image.load("DOTs_and_BOXes/resource/chess-pawn-regular.png")
dotImage = pygame.transform.scale(dotImage, (18, 22))  

playground_image = pygame.image.load("DOTs_and_BOXes/resource/Playground.png")
playground_image = pygame.transform.scale(playground_image, (WIDTH, HEIGHT))

# Winner Icons
# exit = pygame.image.load("resource/exit.png")
# # exit = pygame.image.load("DOTs_and_BOXes/resource/exit.png")
# exit = pygame.transform.scale(exit, (100, 70))
# exitButton = exit.get_rect(topleft=(10, 10))  # 按鈕的位置

# Game state
grid_lines = []  # Tracks clicked lines with colors
boxes = [[None for _ in range(GRID_SIZE - 1)] for _ in range(GRID_SIZE - 1)]
scores = {"Player": 0, "Computer": 0}
turn = "Player"  # Starting turn
winner = "Computer"
theme = "Classic"
last_line = None  # Last selected line
last_turn = None

# Calculate grid position (centered)
margin = 20
board_width = 440
board_height = 440
board_start_x = (WIDTH - board_width) // 2 
board_start_y = (HEIGHT - board_height) // 2 + margin
CELL_SIZE = BOARD_SIZE // (GRID_SIZE - 1) 

# Create lines
lines = []
for row in range(GRID_SIZE):
    for col in range(GRID_SIZE - 1):
        lines.append(((board_start_x + col * CELL_SIZE, board_start_y + row * CELL_SIZE),
                      (board_start_x + (col + 1) * CELL_SIZE, board_start_y + row * CELL_SIZE)))  # Horizontal
for col in range(GRID_SIZE):
    for row in range(GRID_SIZE - 1):
        lines.append(((board_start_x + col * CELL_SIZE, board_start_y + row * CELL_SIZE),
                      (board_start_x + col * CELL_SIZE, board_start_y + (row + 1) * CELL_SIZE)))  # Vertical

# Helper functions
def draw_grid(hover_line=None):
    global last_line, last_turn, theme
    screen.fill(GREEN)
    if theme == "Classic":
        screen.fill(GREEN)
    elif theme == "Playground":
        screen.blit(playground_image, (0, 0))

    # 設定圓角半徑
    corner_radius = 12
    # 繪製背景矩形的主要部分（不包含圓角）
    pygame.draw.rect(screen, BOARD_COLOR, 
                     (board_start_x - margin, board_start_y - margin + corner_radius, 
                      board_width, board_height - 2 * corner_radius))  # 垂直中段
    pygame.draw.rect(screen, BOARD_COLOR, 
                     (board_start_x - margin + corner_radius, board_start_y - margin, 
                      board_width - 2 * corner_radius, board_height))  # 水平中段

    # 繪製四個圓角
    pygame.draw.circle(screen, BOARD_COLOR, 
                       (board_start_x - margin + corner_radius, board_start_y - margin + corner_radius), 
                       corner_radius)  # 左上角
    pygame.draw.circle(screen, BOARD_COLOR, 
                       (board_start_x + board_width - corner_radius - margin, board_start_y - margin + corner_radius), 
                       corner_radius)  # 右上角
    pygame.draw.circle(screen, BOARD_COLOR, 
                       (board_start_x - margin + corner_radius, board_start_y + board_height - corner_radius - margin), 
                       corner_radius)  # 左下角
    pygame.draw.circle(screen, BOARD_COLOR, 
                       (board_start_x + board_width - corner_radius - margin, board_start_y + board_height - corner_radius - margin), 
                       corner_radius)  # 右下角

    # Draw title
    title = title_font.render("Dots and Boxes", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 30))

    # 繪製 dots
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            dot_pos = (board_start_x + col * CELL_SIZE - 10, board_start_y + row * CELL_SIZE - 10)  # 調整位置以對齊格線
            screen.blit(dotImage, dot_pos)

    # Draw lines
    for line, color in grid_lines:
        # print(f'line{line}; color:{color};last_line{last_line}')
        if line == last_line:
            pygame.draw.line(screen, BLUE if last_turn == "Computer" else RED, line[0], line[1], LINE_WIDTH)
        # 其餘已被點擊過的 line 則顯示為黑色
        else:
            pygame.draw.line(screen, BLACK, line[0], line[1], LINE_WIDTH)

    # Draw hovered line as dashed
    if hover_line:
        start, end = hover_line
        draw_dashed_line(screen, GRAY, start, end, DASHED_LINE_WIDTH)

    # Draw boxes
    for row in range(GRID_SIZE - 1):
        for col in range(GRID_SIZE - 1):
            if row < len(boxes) and col < len(boxes[row]):
                if boxes[row][col] == "Player":
                    pygame.draw.rect(screen, RED, 
                                    (board_start_x + col * CELL_SIZE + LINE_WIDTH, 
                                    board_start_y + row * CELL_SIZE + LINE_WIDTH,
                                    CELL_SIZE - LINE_WIDTH * 2,
                                    CELL_SIZE - LINE_WIDTH * 2))
                elif boxes[row][col] == "Computer":
                    pygame.draw.rect(screen, BLUE, 
                                    (board_start_x + col * CELL_SIZE + LINE_WIDTH, 
                                    board_start_y + row * CELL_SIZE + LINE_WIDTH,
                                    CELL_SIZE - LINE_WIDTH * 2,
                                    CELL_SIZE - LINE_WIDTH * 2))
                
    turn_text = font.render(f"Turn: {'Player' if turn == 'Player' else 'Computer'}", True, WHITE)
    # 畫分數（根據遊戲模式顯示正確的玩家名稱）
    if "Player" in scores and "Computer" in scores:
        if theme == "Playground":
            player_score_text = font.render(f"Player: {scores['Player']}", True, WHITE)
            computer_score_text = font.render(f"Computer: {scores['Computer']}", True, WHITE)
        else:
            player_score_text = font.render(f"Player: {scores['Player']}", True, RED)
            computer_score_text = font.render(f"Computer: {scores['Computer']}", True, BLUE)
        screen.blit(player_score_text, (MARGIN, HEIGHT - 50))
        screen.blit(computer_score_text, (WIDTH - MARGIN - computer_score_text.get_width(), HEIGHT - 50))
    elif "Player1" in scores and "Player2" in scores:
        # 雙人遊戲
        player1_score_text = font.render(f"Player1: {scores['Player1']}", True, RED)
        player2_score_text = font.render(f"Player2: {scores['Player2']}", True, BLUE)
        screen.blit(player1_score_text, (MARGIN, HEIGHT - 50))
        screen.blit(player2_score_text, (WIDTH - MARGIN - player2_score_text.get_width(), HEIGHT - 50))

    screen.blit(player_score_text, (MARGIN, HEIGHT - 50))
    screen.blit(computer_score_text, (WIDTH - MARGIN - computer_score_text.get_width(), HEIGHT - 50))
    screen.blit(turn_text, (WIDTH // 2 - turn_text.get_width() // 2, HEIGHT - 50))
    # 在分數旁顯示圖示
    screen.blit(playerIcon, (MARGIN - 40, HEIGHT - 55))
    screen.blit(computerIcon, (WIDTH - MARGIN - computer_score_text.get_width() - 40, HEIGHT - 55))
    # screen.blit(exit, exitButton)
    drawExitRestartButton()

# Dashed line function
def draw_dashed_line(surface, color, start_pos, end_pos, width, dash_length=10):
    dx, dy = end_pos[0] - start_pos[0], end_pos[1] - start_pos[1]
    distance = (dx**2 + dy**2)**0.5
    dash_count = int(distance // dash_length)
    for i in range(dash_count):
        start_x = start_pos[0] + (dx * i / dash_count)
        start_y = start_pos[1] + (dy * i / dash_count)
        end_x = start_pos[0] + (dx * (i + 0.5) / dash_count)
        end_y = start_pos[1] + (dy * (i + 0.5) / dash_count)
        pygame.draw.line(surface, color, (start_x, start_y), (end_x, end_y), width)

# Exit buttom
exit_button = pygame.Rect(10, 10, 105, 42)
restart_button = pygame.Rect(10, 60, 105, 42)

def drawExitRestartButton():
    # screen.blit(exit, exitButton)
    pygame.draw.rect(screen, WHITE, exit_button)
    pygame.draw.rect(screen, GRAY, exit_button, 2)
    exit_text = font.render("Exit", True, DARKBLUE)
    screen.blit(exit_text, (exit_button.x + 21, exit_button.y + 5))  # Bold
    screen.blit(exit_text, (exit_button.x + 22, exit_button.y + 5))  

    pygame.draw.rect(screen, WHITE, restart_button)
    pygame.draw.rect(screen, GRAY, restart_button, 2)
    restart_text = font.render("Restart", True, DARKBLUE)
    screen.blit(restart_text, (restart_button.x + 3, restart_button.y + 5)) 
    screen.blit(restart_text, (restart_button.x + 4, restart_button.y + 5)) 

def initialize_game(board_size, players, difficulty, currentTheme):
    global GRID_SIZE, scores, turn, background_image, lines, CELL_SIZE, boxes, grid_lines, last_turn, theme
    
    theme = currentTheme
    # 動態設置遊戲版大小
    GRID_SIZE = board_size
    CELL_SIZE = BOARD_SIZE // (GRID_SIZE - 1) 
    boxes = [[None for _ in range(GRID_SIZE - 1)] for _ in range(GRID_SIZE - 1)]
    last_turn = None

    # Recalculate grid lines after GRID_SIZE changes
    lines = []
    grid_lines = []
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE - 1):
            lines.append(((board_start_x + col * CELL_SIZE, board_start_y + row * CELL_SIZE),
                          (board_start_x + (col + 1) * CELL_SIZE, board_start_y + row * CELL_SIZE)))  # Horizontal
    for col in range(GRID_SIZE):
        for row in range(GRID_SIZE - 1):
            lines.append(((board_start_x + col * CELL_SIZE, board_start_y + row * CELL_SIZE),
                          (board_start_x + col * CELL_SIZE, board_start_y + (row + 1) * CELL_SIZE)))  # Vertical

    
    # 初始化分數欄位
    if players == 1:
        scores = {"Player": 0, "Computer": 0}
    elif players == 2:
        scores = {"Player1": 0, "Player2": 0}
    # 初始回合
    turn = "Player1" if players == 2 else "Player"
    
    # 初始化 AI 難度
    set_ai_difficulty(difficulty)

def set_ai_difficulty(difficulty):
    global AI_LEVEL
    if difficulty == "Easy":
        AI_LEVEL = 1
    elif difficulty == "Medium":
        AI_LEVEL = 2
    elif difficulty == "Hard":
        AI_LEVEL = 3

def draw_scores():
    if len(scores) == 2:  # 玩家 vs 電腦
        player_score_text = font.render(f"Player: {scores['Player']}", True, RED)
        computer_score_text = font.render(f"Computer: {scores['Computer']}", True, BLUE)
        screen.blit(player_score_text, (MARGIN, HEIGHT - 50))
        screen.blit(computer_score_text, (WIDTH - MARGIN - computer_score_text.get_width(), HEIGHT - 50))
        screen.blit(playerIcon, (MARGIN - 40, HEIGHT - 55))
        screen.blit(computerIcon, (WIDTH - MARGIN - computer_score_text.get_width() - 40, HEIGHT - 55))
    elif len(scores) == 3:  # 玩家1 vs 玩家2
        player1_score_text = font.render(f"Player1: {scores['Player1']}", True, RED)
        player2_score_text = font.render(f"Player2: {scores['Player2']}", True, BLUE)
        screen.blit(player1_score_text, (MARGIN, HEIGHT - 50))
        screen.blit(player2_score_text, (WIDTH - MARGIN - player2_score_text.get_width(), HEIGHT - 50))
        screen.blit(playerIcon, (MARGIN - 40, HEIGHT - 55))
        screen.blit(playerIcon, (WIDTH - MARGIN - player2_score_text.get_width() - 40, HEIGHT - 55))

def draw_background():
    screen.blit(background_image, (0, 0))

def check_game_over():
    total_boxes = (GRID_SIZE - 1) ** 2
    filled_boxes = sum(1 for row in boxes for cell in row if cell is not None)
    return filled_boxes == total_boxes

def handleGame(event):
    global grid_lines, boxes, last_line, turn, scores, winner
    if event.type == pygame.MOUSEBUTTONDOWN:
        if restart_button.collidepoint(event.pos):
            # print("Restarting the game...")
            grid_lines = []  
            boxes = [[None for _ in range(GRID_SIZE - 1)] for _ in range(GRID_SIZE - 1)] 
            scores = {"Player": 0, "Computer": 0}  
            turn = "Player" 
            last_line = None  
            lines = []  
            for row in range(GRID_SIZE):
                for col in range(GRID_SIZE - 1):
                    lines.append(((board_start_x + col * CELL_SIZE, board_start_y + row * CELL_SIZE),
                                  (board_start_x + (col + 1) * CELL_SIZE, board_start_y + row * CELL_SIZE)))  # Horizontal
            for col in range(GRID_SIZE):
                for row in range(GRID_SIZE - 1):
                    lines.append(((board_start_x + col * CELL_SIZE, board_start_y + row * CELL_SIZE),
                                  (board_start_x + col * CELL_SIZE, board_start_y + (row + 1) * CELL_SIZE)))  # Vertical
            initialize_game(board_size=GRID_SIZE, players=1, difficulty="Medium", currentTheme=theme) 
        
def handleExit(event):
    global grid_lines, boxes, last_line, turn, scores, winner
    if event.type == pygame.MOUSEBUTTONDOWN:
        if exit_button.collidepoint(event.pos):
            return "exit"     

def detect_hover_line(mouse_pos):
    for line in lines:
        if line not in [l[0] for l in grid_lines]:
            start, end = line
            mid_x = (start[0] + end[0]) / 2
            mid_y = (start[1] + end[1]) / 2
            if abs(mouse_pos[0] - mid_x) < 15 and abs(mouse_pos[1] - mid_y) < 15:
                return line
    return None

def check_boxes():
    global turn
    scored = False

    # print(f"boxes dimensions: {len(boxes)}x{len(boxes[0])} (should be {GRID_SIZE-1}x{GRID_SIZE-1})")
    for row in range(GRID_SIZE - 1):
        for col in range(GRID_SIZE - 1):
            # print(f"Checking box at row {row}, col {col}")
            if row < len(boxes) and col < len(boxes[row]):
                if boxes[row][col] is None:
                    # print(f"{turn} placed a piece at ({col}, {row})")
                    top = ((board_start_x + col * CELL_SIZE, board_start_y + row * CELL_SIZE),
                        (board_start_x + (col + 1) * CELL_SIZE, board_start_y + row * CELL_SIZE))
                    bottom = ((board_start_x + col * CELL_SIZE, board_start_y + (row + 1) * CELL_SIZE),
                            (board_start_x + (col + 1) * CELL_SIZE, board_start_y + (row + 1) * CELL_SIZE))
                    left = ((board_start_x + col * CELL_SIZE, board_start_y + row * CELL_SIZE),
                            (board_start_x + col * CELL_SIZE, board_start_y + (row + 1) * CELL_SIZE))
                    right = ((board_start_x + (col + 1) * CELL_SIZE, board_start_y + row * CELL_SIZE),
                            (board_start_x + (col + 1) * CELL_SIZE, board_start_y + (row + 1) * CELL_SIZE))
                    if all(line in [l[0] for l in grid_lines] for line in [top, bottom, left, right]):
                        boxes[row][col] = turn
                        # print(f"all {turn} placed a piece at ({col}, {row})")
                        scores[turn] += 1
                        scored = True
    return scored

def computer_move():
    global turn, last_line, AI_LEVEL, last_turn
    available_lines = [line for line in lines if line not in [l[0] for l in grid_lines]]
    
    if available_lines:
        if AI_LEVEL == 1:  # Easy difficulty - Random move
            chosen_line = random.choice(available_lines)
        
        elif AI_LEVEL == 2:  # Medium difficulty - Prioritize completing boxes
            # The AI will check if it can complete a box, if not, it will pick a random line
            chosen_line = medium_ai_move(available_lines)
        
        elif AI_LEVEL == 3:  # Hard difficulty - Minimax or heuristic-based strategy
            chosen_line = hard_ai_move(available_lines)
        
        grid_lines.append((chosen_line, BLUE))
        last_line = chosen_line
        last_turn = "Computer"
        if not check_boxes():
            turn = "Player"

def medium_ai_move(available_lines):
    # # Medium difficulty AI prioritizes completing boxes.
    # # Step 1: Check if the AI can complete a box.
    # for line in available_lines:
    #     if will_complete_box(line, "Computer"):
    #         return line  # AI completes a box if possible
    
    # # Step 2: Block the player from completing a box.
    # for line in available_lines:
    #     if will_complete_box(line, "Player"):
    #         return line  # Block the player's potential box completion
    
    # # Step 3: If no boxes to complete or block, return a random move.
    # return random.choice(available_lines)
    # Medium difficulty AI prioritizes completing its own boxes.
    # Step 1: Check if the AI can complete a box.
    for line in available_lines:
        if will_complete_box(line, "Computer"):
            return line  # AI completes a box if possible
    
    # Step 2: If no box can be completed, return a random move.
    return random.choice(available_lines)

def will_complete_box(line, player):
    """Check if placing this line would complete a box for the given player."""
    for row in range(GRID_SIZE - 1):
        for col in range(GRID_SIZE - 1):
            if line in get_box_lines(row, col):
                # Check if all lines of the box are present (except for the one we are considering)
                box_lines = get_box_lines(row, col)
                if all(l in [l[0] for l in grid_lines] for l in box_lines if l != line):
                    if boxes[row][col] is None:  # Only complete if the box isn't taken
                        return True
    return False

def get_box_lines(row, col):
    """Returns the lines that make up the box at (row, col)."""
    top = ((board_start_x + col * CELL_SIZE, board_start_y + row * CELL_SIZE),
           (board_start_x + (col + 1) * CELL_SIZE, board_start_y + row * CELL_SIZE))
    bottom = ((board_start_x + col * CELL_SIZE, board_start_y + (row + 1) * CELL_SIZE),
              (board_start_x + (col + 1) * CELL_SIZE, board_start_y + (row + 1) * CELL_SIZE))
    left = ((board_start_x + col * CELL_SIZE, board_start_y + row * CELL_SIZE),
            (board_start_x + col * CELL_SIZE, board_start_y + (row + 1) * CELL_SIZE))
    right = ((board_start_x + (col + 1) * CELL_SIZE, board_start_y + row * CELL_SIZE),
             (board_start_x + (col + 1) * CELL_SIZE, board_start_y + (row + 1) * CELL_SIZE))
    return [top, bottom, left, right]

def hard_ai_move(available_lines):
    for line in available_lines:
        if will_complete_box(line, "Computer"):
            return line  # AI completes a box if possible
    
    # Step 2: Block the player from completing a box.
    for line in available_lines:
        if will_complete_box(line, "Player"):
            return line  # Block the player's potential box completion
    
    # Step 3: If no boxes to complete or block, return a random move.
    return random.choice(available_lines)

# 主遊戲迴圈
def start_game(players, board_size, difficulty, theme):
    global turn, last_line, scores, winner, grid_lines, last_turn
    running = True
    initialize_game(board_size, players, difficulty, theme)
    while running:
        mouse_pos = pygame.mouse.get_pos()
        hover_line = detect_hover_line(mouse_pos)
        for event in pygame.event.get():
            if handleExit(event) == 'exit':  # 點擊退出
                # print('handleExit called')
                return "Computer", scores["Player"], scores["Computer"], "game_over"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    # print('press f')
                    pygame.display.flip()
                    return "Computer", scores["Player"], scores["Computer"], "game_over"
                elif event.key == pygame.K_r:
                    # print("Restarting the game...")
                    grid_lines = []  # Clear all the drawn lines
                    boxes = [[None for _ in range(GRID_SIZE - 1)] for _ in range(GRID_SIZE - 1)]  # Reset the boxes
                    scores = {"Player": 0, "Computer": 0}  # Reset the scores
                    turn = "Player"  # Set the starting turn (or "Player1", "Player2" if two players)
                    last_line = None  # No line has been drawn yet
                    lines = []  # Clear all lines
                    # Recalculate the grid lines if necessary
                    for row in range(GRID_SIZE):
                        for col in range(GRID_SIZE - 1):
                            lines.append(((board_start_x + col * CELL_SIZE, board_start_y + row * CELL_SIZE),
                                        (board_start_x + (col + 1) * CELL_SIZE, board_start_y + row * CELL_SIZE)))  # Horizontal
                    for col in range(GRID_SIZE):
                        for row in range(GRID_SIZE - 1):
                            lines.append(((board_start_x + col * CELL_SIZE, board_start_y + row * CELL_SIZE),
                                        (board_start_x + col * CELL_SIZE, board_start_y + (row + 1) * CELL_SIZE)))  # Vertical

                    # Optionally reinitialize other game settings, like board size, difficulty, etc.
                    initialize_game(board_size=GRID_SIZE, players=1, difficulty="Medium", currentTheme=theme)  # Update with actual values
 
            handleGame(event)
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if hover_line and turn == "Player":
                    grid_lines.append((hover_line, RED))
                    last_line = hover_line
                    last_turn = "Player"
                    if not check_boxes():
                        turn = "Computer"
        draw_grid(hover_line)
        if turn == "Computer" and running:
            computer_move()

        draw_grid(hover_line)

        if check_game_over():
            # winner = "Player" if scores["player"] > scores["computer"] else "Computer"
            # game_over.main(winner, scores["player"], scores["computer"])  # Call game over screen
            # break
            winner = "Player" if scores["Player"] > scores["Computer"] else "Computer"
            draw_grid()
            pygame.display.update()
            pygame.time.delay(1000)  # 停留1秒後跳轉
            from DOTs_and_BOXes import game_over
            game_over.main(winner, scores["Player"], scores["Computer"])
            break

        pygame.display.update()
    return winner, scores["Player"], scores["Computer"], "game_over"

if __name__ == "__main__":
    start_game()