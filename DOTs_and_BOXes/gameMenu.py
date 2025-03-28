import pygame
import sys
from DOTs_and_BOXes.game import start_game,initialize_game  # 假設 game.py 中有 start_game 方法

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
FONT_SIZE = 36

# Fonts
font = pygame.font.Font("DOTs_and_BOXes/resource/IMFellDoublePicaSC-Regular.ttf", FONT_SIZE)
bigFont = pygame.font.Font("DOTs_and_BOXes/resource/IMFellDoublePicaSC-Regular.ttf", 60)

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dots and Boxes Menu")

# Load background image
background_image = pygame.image.load("DOTs_and_BOXes/resource/backgroundTransparent.png")
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

# Buttons
start = pygame.image.load("DOTs_and_BOXes/resource/start.png") 
start = pygame.transform.scale(start, (180, 70))
startButton = start.get_rect(topleft=(300, 470))  # 按鈕的位置

# Options and their ranges
options = {
    "Players": [1, 2],
    "Board Size": [f"{i}x{i}" for i in range(6, 13)],
    "Difficulty": ["Easy", "Medium", "Hard"],
    "Theme": ["Classic", "Playground"]
}

# Default selections
selection = {
    "Players": 1,
    "Board Size": "10x10",
    "Difficulty": "Medium",
    "Theme": "Classic"
}

# Helper to draw options
def draw_option(label, value, x, y):
    text = font.render(f"{label}: {value}", True, BLACK)
    screen.blit(text, (x, y))
    left_arrow = font.render("<", True, BLACK)
    right_arrow = font.render(">", True, BLACK)
    screen.blit(left_arrow, (x - 50, y))
    screen.blit(right_arrow, (x + 350, y))
    return pygame.Rect(x - 50, y, 30, FONT_SIZE), pygame.Rect(x + 350, y, 30, FONT_SIZE)

# Draw menu
def draw_menu():
    screen.fill(WHITE)
    screen.blit(background_image, (0, 0))

    # Title
    title_text = bigFont.render("Game Menu", True, BLACK)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))

    # Options
    y = 150
    buttons = {}
    for label, value in selection.items():
        left, right = draw_option(label, value, 250, y)
        buttons[label] = {"left": left, "right": right}
        y += 80

    # Start button
    # start_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT - 100, 200, 50)
    # pygame.draw.rect(screen, GRAY, start_button)
    # start_text = font.render("Start", True, BLACK)
    # screen.blit(start_text, (start_button.x + 50, start_button.y + 10))
    screen.blit(start, startButton)

    return buttons, startButton

# Game states ??
game_running = False
game_paused = False

# Main loop
def main():
    while True:
        global game_running, game_paused
        buttons, start_button = draw_menu()
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                for label, btns in buttons.items():
                    if btns["left"].collidepoint(event.pos):
                        current_idx = options[label].index(selection[label])
                        selection[label] = options[label][(current_idx - 1) % len(options[label])]
                    elif btns["right"].collidepoint(event.pos):
                        current_idx = options[label].index(selection[label])
                        selection[label] = options[label][(current_idx + 1) % len(options[label])]
                if start_button.collidepoint(event.pos):
                    # Parse board size
                    board_size = int(selection["Board Size"].split("x")[0])
                    # Pass parameters to game.py

                    # initialize_game(players=selection["Players"], board_size=board_size,
                    #            difficulty=selection["Difficulty"], theme=selection["Theme"])
                    # start_game()
                    return selection["Players"], board_size, selection["Difficulty"], selection["Theme"], "game"

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_k:  # 按 K 鍵暫停或繼續遊戲
                    # print("K key pressed")
                    game_paused = not game_paused  # 切換暫停狀態
                elif event.key == pygame.K_f:  # 按 F 鍵離開遊戲
                    # print("F key pressed")
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_r:  # 按 R 鍵重新開始遊戲
                    # print("R key pressed")
                    game_running = False
                    game_paused = False
                    # 重新初始化遊戲，這裡可以重新執行遊戲初始化
                    initialize_game(players=selection["Players"], board_size=int(selection["Board Size"].split("x")[0]),
                                difficulty=selection["Difficulty"], theme=selection["Theme"])
                    start_game()
        # 遊戲運行狀態
        if game_running:
            if game_paused:
                # 顯示暫停畫面
                pause_text = bigFont.render("Game Paused - Press 'K' to Resume", True, BLACK)
                screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2 - 50))
            else:
                # 遊戲正在進行
                pass

if __name__ == "__main__":
    main()
