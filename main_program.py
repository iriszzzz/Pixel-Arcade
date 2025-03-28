import pygame
import json
import os
os.chdir(os.path.dirname(__file__))
import hashlib
import sys
import snake
from bridge_game import BridgeGame
from DOTs_and_BOXes.flow import DnBmain
from dark_chess.chess import main as start_dark_chess

# Initialize Pygame

pygame.init()

# Basic settings

WIDTH = 800

HEIGHT = 600

FONT_SIZE = 32

INPUT_BOX_WIDTH = 320

INPUT_BOX_HEIGHT = 40

BUTTON_WIDTH = 320

BUTTON_HEIGHT = 40

LABEL_WIDTH = 160  # 改為 160

# Colors

WHITE = (255, 255, 255)

BLACK = (0, 0, 0)

GRAY = (245, 240, 245)

LIGHT_BLUE = (153, 76, 0)

RED = (255, 0, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption("Game Platform")

# 控制閃爍的變數
show_text = True        # 控制文字是否顯示
blink_timer = 0         # 計時器
blink_interval = 500    # 閃爍間隔 (毫秒)

def experience_to_next_level(level):
        return 2 ** (level - 1) * 1000

class InputBox:

    def __init__(self, x, y, w, h, text='', password=False):

        self.rect = pygame.Rect(x, y, w, h)

        self.color = GRAY

        self.text = text

        self.password = password

        self.txt_surface = pygame.font.Font(None, FONT_SIZE).render(self.text, True, BLACK)

        self.active = False

    def handle_event(self, event):

        if event.type == pygame.MOUSEBUTTONDOWN:

            if self.rect.collidepoint(event.pos):

                self.active = True

            else:

                self.active = False

            self.color = LIGHT_BLUE if self.active else GRAY

        if event.type == pygame.KEYDOWN:

            if self.active:

                if event.key == pygame.K_RETURN:

                    return True

                elif event.key == pygame.K_BACKSPACE:

                    self.text = self.text[:-1]

                else:

                    self.text += event.unicode

                self.txt_surface = pygame.font.Font(None, FONT_SIZE).render('*' * len(self.text) if self.password else self.text, True, BLACK)

        return False

    def draw(self, screen):

        pygame.draw.rect(screen, WHITE, self.rect)

        pygame.draw.rect(screen, self.color, self.rect, 2)

        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))

class Button:

    def __init__(self, x, y, w, h, text, font_path = None):

        self.rect = pygame.Rect(x, y, w, h)

        self.text = text

        self.color = GRAY
        pygame.font.Font("Silkscreen-Regular.ttf", FONT_SIZE)
        # self.txt_surface = pygame.font.Font(r"D:\Desktop\main_program_v6-20241207T134223Z-001\main_program_v5-20241207T134223Z-001\main_program_v5\Silkscreen-Regular.ttf", 28).render(text, True, BLACK)
        self.txt_surface = pygame.font.Font("Silkscreen-Regular.ttf", 28).render(text, True, BLACK)
        self.active = False
        
    def handle_event(self, event):

        if event.type == pygame.MOUSEBUTTONDOWN:

            if self.rect.collidepoint(event.pos):

                return True

        elif event.type == pygame.MOUSEMOTION:

            self.active = self.rect.collidepoint(event.pos)

        return False

    def draw(self, screen):

        color = LIGHT_BLUE if self.active else GRAY

        pygame.draw.rect(screen, color, self.rect)

        text_rect = self.txt_surface.get_rect(center=self.rect.center)

        screen.blit(self.txt_surface, text_rect)

class GamePlatform:

    def __init__(self):

        self.users_file = "users.json"

        self.users = self.load_users()

        self.current_user = None

        self.state = "start"

        self.setup_ui()

        self.message = ""

        self.message_color = RED
        # Load background image
        self.background = pygame.image.load("背景.png")  # 替換為你的背景圖片檔案名稱
        self.background = pygame.transform.scale(self.background, (WIDTH, HEIGHT))  # 確保圖片符合畫面大小
        # Load game-style font
        self.game_font = pygame.font.Font("Silkscreen-Bold.ttf", FONT_SIZE)  # 替換為你的字體檔案名稱
        self.title_font = pygame.font.Font("Silkscreen-Bold.ttf", 48)  # 用於標題文字的字體
        self.start_button_label = pygame.font.Font("Silkscreen-Regular.ttf", FONT_SIZE) 
                                                     
        self.game_control = {
            "paused": False,   # 是否暫停
            "restart": False   # 是否重啟
        }
        
        pygame.mixer.init()
        self.start_game_sound = pygame.mixer.Sound("Start.mp3")
    def setup_ui(self):

        center_x = WIDTH // 2 - INPUT_BOX_WIDTH // 2
        button_center_x = WIDTH // 2 - BUTTON_WIDTH // 2

        label_x = center_x - LABEL_WIDTH - 50  # 改為 50
        
        # Start UI

        # Login UI

        self.username_box = InputBox(center_x, 240, INPUT_BOX_WIDTH, INPUT_BOX_HEIGHT)

        self.password_box = InputBox(center_x, 320, INPUT_BOX_WIDTH, INPUT_BOX_HEIGHT, password=True)

        self.login_button = Button(button_center_x, 380, BUTTON_WIDTH, BUTTON_HEIGHT, "Login")

        self.register_button = Button(button_center_x, 440, BUTTON_WIDTH, BUTTON_HEIGHT, "Register")

        # Change Password UI

        self.old_password_box = InputBox(center_x, 200, INPUT_BOX_WIDTH, INPUT_BOX_HEIGHT, password=True)

        self.new_password_box = InputBox(center_x, 280, INPUT_BOX_WIDTH, INPUT_BOX_HEIGHT, password=True)

        self.confirm_password_box = InputBox(center_x, 360, INPUT_BOX_WIDTH, INPUT_BOX_HEIGHT, password=True)

        self.confirm_change_button = Button(button_center_x, 420, BUTTON_WIDTH, BUTTON_HEIGHT, "Confirm Change")

        self.back_button = Button(button_center_x, 480, BUTTON_WIDTH, BUTTON_HEIGHT, "Back")

        # Main Menu UI
        
        self.snake_button = Button(button_center_x, 150 + 60, BUTTON_WIDTH, BUTTON_HEIGHT, "Gourmet Train")
        
        self.bridge_game_button = Button(button_center_x, 150 + 120, BUTTON_WIDTH, BUTTON_HEIGHT, "Bridge Game")
        
        self.DotsandBoxes_button = Button(button_center_x, 150 + 180, BUTTON_WIDTH, BUTTON_HEIGHT, "Dots & Boxes")

        self.Darkchess_button = Button(button_center_x, 150 + 240, BUTTON_WIDTH, BUTTON_HEIGHT, "Dark Chess")

        self.logout_button = Button(button_center_x, 150 + 300, BUTTON_WIDTH, BUTTON_HEIGHT, "Logout")

        self.change_password_button = Button(button_center_x, 150 + 360, BUTTON_WIDTH, BUTTON_HEIGHT, "Change Password")

    def load_users(self):

        if os.path.exists(self.users_file):

            with open(self.users_file, 'r') as f:

                return json.load(f)

        return {}

    def save_users(self):

        with open(self.users_file, 'w') as f:

            json.dump(self.users, f, indent=4)

    def hash_password(self, password):

        return hashlib.sha256(password.encode()).hexdigest()

    def register(self, username, password):

        if not username or not password:

            self.message = "Username & password can't be empty!"

            self.message_color = RED

            return False

        if username in self.users:

            self.message = "Username already exists"

            self.message_color = RED

            return False

        self.users[username] = {

            "password": self.hash_password(password),

            "level": 1,

            "exp": 0,
            
            "Snake Best Score": 0,

            "Dark_chess_record": {}

        }

        self.save_users()

        self.message = "Registration successful"

        self.message_color = BLACK

        return True

    def login(self, username, password):

        if username not in self.users:

            self.message = "Username does not exist"

            self.message_color = RED

            return False

        if self.users[username]["password"] != self.hash_password(password):

            self.message = "Incorrect password"

            self.message_color = RED

            return False

        self.current_user = username
        
        self.message_color = BLACK

        return True

    def change_password(self, old_password, new_password, confirm_password):

        if not old_password or not new_password or not confirm_password:

            self.message = "All fields are required"

            self.message_color = RED

            return False

        if new_password != confirm_password:

            self.message = "New passwords do not match"

            self.message_color = RED

            return False

        if self.users[self.current_user]["password"] != self.hash_password(old_password):

            self.message = "Current password is incorrect"

            self.message_color = RED

            return False

        self.users[self.current_user]["password"] = self.hash_password(new_password)

        self.save_users()

        self.message = "Password changed!"

        self.message_color = BLACK

        return True

    
    def run(self):
        show_text = True  # 控制文字是否顯示
        blink_timer = 0   # 計時器
        blink_interval = 500  # 閃爍間隔 (毫秒)

        clock = pygame.time.Clock()

        running = True

        while running:

            for event in pygame.event.get():

                if event.type == pygame.QUIT:

                    running = False

                if self.state == "start":
                    
                    self.start_game_sound.play(-1)
                    title = self.title_font.render("GAME GRIL", True, BLACK)
                    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 200))


                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        self.state = "login"
                        self.message = ""

                if self.state == "login":

                    self.username_box.handle_event(event)

                    self.password_box.handle_event(event)

                    if self.login_button.handle_event(event):

                        if self.login(self.username_box.text, self.password_box.text):

                            self.state = "main_menu"
                            self.message = ""

                    if self.register_button.handle_event(event):

                        if self.register(self.username_box.text, self.password_box.text):

                            self.state = "login"

                            self.username_box.text = ""

                            self.password_box.text = ""

                elif self.state == "main_menu":
                    if self.logout_button.handle_event(event):

                        self.state = "login"
                        self.message = ""

                        self.current_user = None

                        self.username_box.text = ""

                        self.password_box.text = ""

                    if self.change_password_button.handle_event(event):

                        self.state = "change_password"

                        self.old_password_box.text = ""

                        self.new_password_box.text = ""

                        self.confirm_password_box.text = ""

                        self.message = ""
                    
                    if self.snake_button.handle_event(event):
                        # 檢查是否有儲存的遊戲進度
                        save_file_path = "save_game.json"
                        has_saved_game = os.path.exists(save_file_path)
                        
                        if has_saved_game:
                            with open(save_file_path, "r") as f:
                                saved_data = json.load(f)

                            # 詢問玩家是否要載入儲存的遊戲
                            self.state = "snake_prompt"
                            while self.state == "snake_prompt":
                                screen.blit(self.background, (0, 0))
                                title = self.title_font.render("Saved Game Detected!", True, BLACK)
                                screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 200))
                                # 顯示提示文字，分成兩行
                                subtitle_line1 = self.game_font.render("Press 'Y' to continue", True, BLACK)
                                subtitle_line2 = self.game_font.render("or 'N' to start a new game.", True, BLACK)
                                
                                screen.blit(subtitle_line1, (WIDTH // 2 - subtitle_line1.get_width() // 2, 300))
                                screen.blit(subtitle_line2, (WIDTH // 2 - subtitle_line2.get_width() // 2, 340))
                                pygame.display.flip()
                                for event in pygame.event.get():
                                    if event.type == pygame.KEYDOWN:
                                        if event.key == pygame.K_y:
                                            # 傳遞儲存進度到貪吃蛇遊戲
                                            score, best_score, self.state = snake.run_snake(saved_data["high_score"], self.users)
                                            self.state = "main_menu"
                                            break
                                        elif event.key == pygame.K_n:
                                            # 啟動新遊戲，刪除舊存檔
                                            os.remove(save_file_path)
                                            score, best_score, self.state = snake.run_snake(0, self.users)
                                            self.state = "main_menu"
                                            break
                        else:
                            # 沒有儲存進度，直接啟動新遊戲
                            score, best_score, self.state = snake.run_snake(0, self.users)

                        # 更新遊戲分數與經驗值
                        if score > self.users[self.current_user]['Snake Best Score']:
                            self.users[self.current_user]['Snake Best Score'] = best_score
                        self.users[self.current_user]['exp'] += score

                        # 處理升級邏輯
                        while self.users[self.current_user]['exp'] >= experience_to_next_level(self.users[self.current_user]['level']):
                            self.users[self.current_user]['exp'] -= experience_to_next_level(self.users[self.current_user]['level'])
                            self.users[self.current_user]['level'] += 1
                            self.message = f"Level Up to LV{self.users[self.current_user]['level']}!"
                        
                        self.save_users()

                        # 更新
                        with open('users.json', 'w') as json_file:
                            json.dump(self.users, json_file, indent=4)  # 提高可讀性
                                                
                        self.state = "main_menu"
                        
                                
                    if self.bridge_game_button.handle_event(event):
                        pygame.display.set_mode((1024, 768))
                        self.state = "bridge_game"

                        # 啟動 BridgeGame 並接收返回值
                        game_runner = BridgeGame()
                        exp, next_state = game_runner.run()

                        if next_state == "main_menu":
                            pygame.display.set_mode((WIDTH, HEIGHT))
                            self.state = "main_menu"
                            
                            # 累積經驗值
                            self.users[self.current_user]['exp'] += exp

                            # 處理升級邏輯
                            while self.users[self.current_user]['exp'] >= experience_to_next_level(self.users[self.current_user]['level']):
                                self.users[self.current_user]['exp'] -= experience_to_next_level(self.users[self.current_user]['level'])
                                self.users[self.current_user]['level'] += 1
                                self.message = f"Level Up to LV{self.users[self.current_user]['level']}!"

                            self.save_users()  # 儲存更新的經驗值與等級

                        # 更新數據
                        with open('users.json', 'w') as json_file:
                             json.dump(self.users, json_file, indent=4)
                                
                    if self.DotsandBoxes_button.handle_event(event):
                        self.state = "DOTs_and_BOXes"
                        exp, next_state = DnBmain()
                        print(f"-> exp{exp}")
                        if next_state == "main_menu":
                            self.state = "main_menu"
                            self.users[self.current_user]['exp'] += exp # 累積經驗值
                            print(f"+= exp{exp}")
                            # 處理升級邏輯
                            while self.users[self.current_user]['exp'] >= experience_to_next_level(self.users[self.current_user]['level']):
                                self.users[self.current_user]['exp'] -= experience_to_next_level(self.users[self.current_user]['level'])
                                self.users[self.current_user]['level'] += 1
                                self.message = f"Level Up to LV{self.users[self.current_user]['level']}!"
                            self.save_users()  # 儲存更新的經驗值與等級
                        # 更新數據
                        with open('users.json', 'w') as json_file:
                             json.dump(self.users, json_file, indent=4)

                    if self.Darkchess_button.handle_event(event):
                        self.state = "Dark_chess"
                        while self.state == "Dark_chess":
                            exp, game_state, self.state = start_dark_chess(self.users, self.users[self.current_user]["Dark_chess_record"])
                        
                        source_data = game_state
                        self.users[self.current_user]["Dark_chess_record"] = source_data
                        
                        with open("users.json", "w") as json_file:
                            json.dump(self.users, json_file,indent = 8)
                        
                        # 累積經驗值
                        self.users[self.current_user]['exp'] += exp

                        # 處理升級邏輯
                        while self.users[self.current_user]['exp'] >= experience_to_next_level(self.users[self.current_user]['level']):
                            self.users[self.current_user]['exp'] -= experience_to_next_level(self.users[self.current_user]['level'])
                            self.users[self.current_user]['level'] += 1
                            self.message = f"Level Up to LV{self.users[self.current_user]['level']}!"

                        self.save_users()  # 儲存更新的經驗值與等級

                        # 更新數據
                        with open('users.json', 'w') as json_file:
                             json.dump(self.users, json_file, indent=4)

                elif self.state == "change_password":

                    self.old_password_box.handle_event(event)

                    self.new_password_box.handle_event(event)

                    self.confirm_password_box.handle_event(event)

                    if self.confirm_change_button.handle_event(event):

                        if self.change_password(

                            self.old_password_box.text,

                            self.new_password_box.text,

                            self.confirm_password_box.text

                        ):

                            self.state = "main_menu"

                    if self.back_button.handle_event(event):

                        self.state = "main_menu"

                        self.message = ""
            # Blink Timer logic
            current_time = pygame.time.get_ticks()
            if current_time - blink_timer > blink_interval:
                blink_timer = current_time
                show_text = not show_text  # 切換顯示狀態

            # Draw the background
            screen.blit(self.background, (0, 0))
    
            if self.state == "start":
                title = pygame.font.Font("Silkscreen-Bold.ttf", 52).render("Pixel Arcade", True, BLACK)
                screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 200))
                if show_text:
                    subtitle = pygame.font.Font("Silkscreen-Regular.ttf", 30).render("Press \"ENTER\" to start!", True, BLACK)
                    screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, 300))
                        
            if self.state == "login":

                title = self.title_font.render("Game Platform Login", True, BLACK)

                screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))

                label_x = self.username_box.rect.x - LABEL_WIDTH - 50  # 改為 50

                username_label = self.game_font.render("Username:", True, BLACK)

                password_label = self.game_font.render("Password:", True, BLACK)

                screen.blit(username_label, (self.username_box.rect.x, self.username_box.rect.y - 40))

                screen.blit(password_label, (self.password_box.rect.x, self.password_box.rect.y - 40))

                self.username_box.draw(screen)

                self.password_box.draw(screen)

                self.login_button.draw(screen)

                self.register_button.draw(screen)

            elif self.state == "main_menu":
                
                welcome_text = self.title_font.render(f"Welcome, {self.current_user}!", True, BLACK)

                level_text = self.game_font.render(

                    f"Level: {self.users[self.current_user]['level']}", True, BLACK)

                exp_text = self.game_font.render(

                    f"EXP: {self.users[self.current_user]['exp']}", True, BLACK)

                screen.blit(welcome_text, (WIDTH//2 - welcome_text.get_width()//2, 100))

                screen.blit(level_text, (12, 15))

                screen.blit(exp_text, (12, 45))

                self.snake_button.draw(screen)
            
                self.bridge_game_button.draw(screen)
                
                self.DotsandBoxes_button.draw(screen)

                self.Darkchess_button.draw(screen)

                self.logout_button.draw(screen)

                self.change_password_button.draw(screen)

            elif self.state == "change_password":

                title = self.title_font.render("Change Password", True, BLACK)

                screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))

                label_x = self.old_password_box.rect.x - LABEL_WIDTH - 50  # 改為 50

                old_pass_label = self.game_font.render("Current Password:", True, BLACK)

                new_pass_label = self.game_font.render("New Password:", True, BLACK)

                confirm_pass_label = self.game_font.render("Confirm Password:", True, BLACK)

                screen.blit(old_pass_label, (self.old_password_box.rect.x, self.old_password_box.rect.y - 45))

                screen.blit(new_pass_label, (self.new_password_box.rect.x, self.new_password_box.rect.y - 45))

                screen.blit(confirm_pass_label, (self.confirm_password_box.rect.x, self.confirm_password_box.rect.y - 45))

                self.old_password_box.draw(screen)

                self.new_password_box.draw(screen)

                self.confirm_password_box.draw(screen)

                self.confirm_change_button.draw(screen)

                self.back_button.draw(screen)

            if self.message:

                message_surface = self.game_font.render(

                    self.message, True, self.message_color)

                screen.blit(message_surface, (WIDTH//2 - message_surface.get_width()//2, 25))

            pygame.display.flip()

            clock.tick(60)

        pygame.quit()


if __name__ == "__main__":

    platform = GamePlatform()

    platform.run()