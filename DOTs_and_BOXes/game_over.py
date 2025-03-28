import pygame
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# import main_program

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (227, 79, 54)    #245, 144, 127
DARKRED = (201, 32, 32)
BLUE = (51, 107, 184)   #161, 194, 240
FONT_SIZE = 36

# 控制閃爍的變數
show_text = False        # 控制文字是否顯示
blink_timer = 0         # 計時器
blink_interval = 500    # 閃爍間隔 (毫秒)

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game Over")

# Fonts
font = pygame.font.Font("DOTs_and_BOXes/resource/IMFellDoublePicaSC-Regular.ttf", FONT_SIZE)
bigFont = pygame.font.Font("DOTs_and_BOXes/resource/IMFellDoublePicaSC-Regular.ttf", 60)

# Winner Icons
playerIcon = pygame.image.load("DOTs_and_BOXes/resource/user.png")
playerIcon = pygame.transform.scale(playerIcon, (100, 100))
computerIcon = pygame.image.load("DOTs_and_BOXes/resource/computer.png")
computerIcon = pygame.transform.scale(computerIcon, (100, 100))

# Load background image
background_image = pygame.image.load("DOTs_and_BOXes/resource/backgroundTransparent.png")  #"path_to/background.png"
# 取得圖片的原始寬高
original_width, original_height = background_image.get_size()

# 計算螢幕的比例
screen_ratio = WIDTH / HEIGHT
image_ratio = original_width / original_height

# 根據螢幕的比例縮放圖片
if screen_ratio > image_ratio:
    # 螢幕寬度較大，根據寬度縮放圖片
    new_width = WIDTH
    new_height = int(WIDTH / image_ratio)
else:
    # 螢幕高度較大，根據高度縮放圖片
    new_height = HEIGHT
    new_width = int(HEIGHT * image_ratio)

# 使用新的尺寸來縮放背景圖片
background_image = pygame.transform.scale(background_image, (new_width, new_height))

# Buttons
# play_again_button = pygame.Rect(200, 400, 150, 50)
# main_menu_button = pygame.Rect(450, 400, 150, 50)
playAgain = pygame.image.load("DOTs_and_BOXes/resource/playAgain.png")  # 確保這裡有正確的圖片路徑
playAgain = pygame.transform.scale(playAgain, (200, 80))  # 根據需求調整尺寸

mainMenu = pygame.image.load("DOTs_and_BOXes/resource/mainMenu.png")  # 同上
mainMenu = pygame.transform.scale(mainMenu, (200, 80))

# Define button areas
playAgainButtonRect = playAgain.get_rect(topleft=(180, 400))  # 按鈕的位置
mainMenuButtonRect = mainMenu.get_rect(topleft=(420, 400))

def draw_game_over(winner, player_score, computer_score):
    screen.fill(WHITE)
    # screen.blit(background_image, (0, 0))  # 將背景圖片繪製到畫布
    screen.blit(background_image, ((WIDTH - new_width) // 2, (HEIGHT - new_height) // 2))

    # Winner and Scores
    winner_text = font.render(f"Winner: {winner}", True, RED if winner == "Player" else BLUE)
    screen.blit(winner_text, (WIDTH // 2 - winner_text.get_width() // 2, 220))

    # Player and Computer Scores
    score_text = font.render(f"Player: {player_score}  |  Computer: {computer_score}", True, BLACK)
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 300))

    # Winner Icon
    # if winner == "Player":
    #     screen.blit(playerIcon, (WIDTH // 2 - 50, 350))
    # else:
    #     screen.blit(computerIcon, (WIDTH // 2 - 50, 350))

    # Buttons
    # pygame.draw.rect(screen, BLACK, play_again_button)
    # pygame.draw.rect(screen, BLACK, main_menu_button)
    # play_again_text = font.render("Play Again", True, WHITE)
    # main_menu_text = font.render("Main Menu", True, WHITE)
    # screen.blit(play_again_text, (play_again_button.x + 10, play_again_button.y + 10))
    # screen.blit(main_menu_text, (main_menu_button.x + 10, main_menu_button.y + 10))
    screen.blit(playAgain, playAgainButtonRect)
    screen.blit(mainMenu, mainMenuButtonRect)

def main(winner, player_score, computer_score):
    global show_text, blink_timer  # 使用全域變數
    clock = pygame.time.Clock()

    running = True
    while running:
        # Blink Timer logic
        current_time = pygame.time.get_ticks()
        if current_time - blink_timer > blink_interval:
            blink_timer = current_time
            show_text = not show_text  # 切換顯示狀態
        
        # Draw the game over screen
        draw_game_over(winner, player_score, computer_score)

        # Only show "GAME OVER" when show_text is True
        if show_text:
            title_text = bigFont.render("GAME OVER", True, DARKRED)
            screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 120))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # if play_again_button.collidepoint(event.pos):
                if playAgainButtonRect.collidepoint(event.pos):
                    # from DOTs_and_BOXes import gameMenu  # Switch to difficulty selection
                    # gameMenu.main()
                    exp = player_score * 30
                    return exp, "gameMenu"
                elif mainMenuButtonRect.collidepoint(event.pos):
                    # main_program.run()
                    # print("Returning to Main Menu")  # Placeholder for menu
                    running = False
                    exp = player_score * 30

                    return exp, "main_menu"
                    

        pygame.display.flip()  # 更新畫面
        clock.tick(120)  # Keep the frame rate at 60 FPS
   
