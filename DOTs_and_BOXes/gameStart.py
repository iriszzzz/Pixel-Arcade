import pygame
import sys
from DOTs_and_BOXes.gameMenu import main 

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
background_image = pygame.image.load("DOTs_and_BOXes/resource/background.png")

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

# Caption
DotsAndBoxes = pygame.image.load("DOTs_and_BOXes/resource/DotsAndBoxes.png") 
DotsAndBoxes = pygame.transform.scale(DotsAndBoxes, (470, 280))
DotsAndBoxesCaption = DotsAndBoxes.get_rect(topleft=(160, 100))  

# Buttons
playGame = pygame.image.load("DOTs_and_BOXes/resource/Start.png") 
playGame = pygame.transform.scale(playGame, (180, 80))
playGameButton = playGame.get_rect(topleft=(300, 390))  

# Continue = pygame.image.load("DOTs_and_BOXes/resource/Continue.png") 
# Continue = pygame.transform.scale(Continue, (180, 80))
# continueButton = Continue.get_rect(topleft=(300, 480))  

startExit = pygame.image.load("DOTs_and_BOXes/resource/exit.png") 
startExit = pygame.transform.scale(startExit, (120, 70))
startExitButton = startExit.get_rect(topleft=(330, 480))  # (300, 530)

# Draw menu
def draw_menu():
    screen.fill(WHITE)
    # screen.blit(background_image, (0, 0))
    screen.blit(background_image, ((WIDTH - new_width) // 2, (HEIGHT - new_height) // 2))

    screen.blit(DotsAndBoxes, DotsAndBoxesCaption)
    screen.blit(playGame, playGameButton)
    # screen.blit(Continue, continueButton)
    screen.blit(startExit, startExitButton)

    return playGameButton, startExitButton
    # return playGameButton, continueButton, startExitButton

# Main loop
def DNBstartgame():
    while True:
        playGameButton, startExitButton = draw_menu()
        # playGameButton, continueButton, startExitButton = draw_menu()
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # if play_again_button.collidepoint(event.pos):
                if playGameButton.collidepoint(event.pos):
                    # from DOTs_and_BOXes import gameMenu  # Switch to difficulty selection
                    # gameMenu.main() 
                    return "gameMenu"
                elif startExitButton.collidepoint(event.pos): 
                    # from DOTs_and_BOXes import gameMenu  # Switch to difficulty selection
                    # gameMenu.main()
                    return "main_menu"
                # elif mainMenuButtonRect.collidepoint(event.pos):
                #     print("Returning to Main Menu")  # Placeholder for menuif event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            

if __name__ == "__main__":
    main()
