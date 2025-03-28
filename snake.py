import pygame
import random
import time
import sys
import os
os.chdir(os.path.dirname(__file__))
import json
import hashlib

def calculate_hash(data):
    """計算遊戲資料的哈希值"""
    json_data = json.dumps(data, sort_keys=True)  # 確保順序一致
    return hashlib.sha256(json_data.encode()).hexdigest()

def is_data_valid(data):
    """檢查遊戲資料是否有效"""
    original_hash = data.pop("hash", None)  # 獲取存檔中的哈希值
    return original_hash == calculate_hash(data)

WHITE = (255, 255, 255)
GRAY =  (245, 240, 245)
LIGHT_BLUE = (153, 76, 0)
BLACK = (0, 0, 0)

def run_snake(original_high_score, users_info):
    # 初始化
    pygame.init()

    # 遊戲基本設定
    WIDTH, HEIGHT = 800, 600
    CELL_SIZE = 20
    FPS = 10

    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)
    BLACK = (0, 0, 0)
    YELLOW = (255, 255, 0)
    PURPLE = (173, 216, 230)

    # 計分食物
    FOOD_SCORES = {1: 15, 2: 10, 3: 5}

    # 初始化 AI 蛇
    ai_snake = [(WIDTH - 100, HEIGHT - 100)]  # 初始位置
    ai_snake_dir = 'LEFT'
    ai_speed = FPS  # AI 的移動速度
    ai_alive = True  # AI 是否存活
    ai_respawn_timer = 0  # AI 重生計時器
    respawn_duration = 5  # 重生所需時間（秒）


    def update_ai_snake(ai_snake, ai_snake_dir, foods, score, ai_alive, ai_respawn_timer, respawn_duration):
        ai_speed = FPS  # 初始化 ai_speed，防止未賦值錯誤
        head_x, head_y = ai_snake[0]

        # 找到最近的食物
        nearest_food = min(foods, key=lambda f: abs(f['pos'][0] - head_x) + abs(f['pos'][1] - head_y))
        food_x, food_y = nearest_food['pos']

        # 根據最近食物的方向決定移動方向
        if head_x < food_x and ai_snake_dir != 'LEFT':
            ai_snake_dir = 'RIGHT'
        elif head_x > food_x and ai_snake_dir != 'RIGHT':
            ai_snake_dir = 'LEFT'
        elif head_y < food_y and ai_snake_dir != 'UP':
            ai_snake_dir = 'DOWN'
        elif head_y > food_y and ai_snake_dir != 'DOWN':
            ai_snake_dir = 'UP'
        
        # 更新 AI 蛇的頭部位置
        if ai_snake_dir == 'UP':
            head_y -= CELL_SIZE
        elif ai_snake_dir == 'DOWN':
            head_y += CELL_SIZE
        elif ai_snake_dir == 'LEFT':
            head_x -= CELL_SIZE
        elif ai_snake_dir == 'RIGHT':
            head_x += CELL_SIZE

        if ai_alive:
            if head_x < 0 or head_x >= WIDTH or head_y < 0 or head_y >= HEIGHT:  # 超出邊界
                ai_alive = False
                if ai_respawn_timer == 0:  # 確保只更新一次死亡時間
                    ai_respawn_timer = time.time()
            else:
                for player_segment in snake:  # 撞到玩家蛇身體
                    if ai_snake[0] == player_segment:
                        ai_alive = False
                        if ai_respawn_timer == 0:
                            ai_respawn_timer = time.time()
                        score += 300  # 玩家得分
                        break
       
        # AI 重生邏輯
        if not ai_alive and time.time() - ai_respawn_timer >= respawn_duration:
            ai_alive = True
            ai_respawn_timer = 0  # 重置計時器
            ai_snake = [(WIDTH - 100, HEIGHT - 100)]  # 重置 AI 蛇的位置
            ai_snake_dir = 'LEFT'  # 重置 AI 蛇的方向
            ai_speed = FPS  # 重置速度
        
        if ai_alive:    
            # 插入新頭部位置
            new_head = (head_x, head_y)
            ai_snake.insert(0, new_head)

            # 移除尾部
            ai_snake.pop()
            
        return ai_snake, ai_snake_dir, score, ai_alive, ai_respawn_timer, ai_speed

    


    def check_ai_eat_food(ai_snake, foods):
        head_x, head_y = ai_snake[0]
        for food in foods:
            if head_x == food['pos'][0] and head_y == food['pos'][1]:
                foods.remove(food)  # 移除被吃掉的食物
                foods.append({'pos': random_position(), 'size': random.randint(1, 3)})  # 生成新的食物
                ai_snake.append(ai_snake[-1])  # 增加 AI 蛇的長度
                return True
        return False

    # 美術視覺
    background_image = pygame.image.load("grass_background.png")
    background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
    snake_head_image = pygame.image.load("車頭.png")
    snake_head_image = pygame.transform.scale(snake_head_image, (30, 30))
    snake_body_image = pygame.image.load("車身.png")
    snake_body_image = pygame.transform.scale(snake_body_image, (30, 30))
    checkpoint_image = pygame.transform.scale(pygame.image.load("關卡圖示.png"), (40, 40))

    food_images = {
        1: pygame.transform.scale(pygame.image.load("炸蝦.png"), (30, 30)),  # 小食物
        2: pygame.transform.scale(pygame.image.load("雞腿.png"), (40, 40)), # 中食物
        3: pygame.transform.scale(pygame.image.load("漢堡.png"), (50, 50))    # 大食物
    }
    # 初始化畫面
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Gourmet Train")

    # 字體
    font = pygame.font.Font("字體.ttf", 20)
    title_font = pygame.font.Font("Silkscreen-Bold.ttf", 37)
    
    def draw_text(type, text, color, x, y):
        if type == "normal":
            text_surface = font.render(text, True, color)
            screen.blit(text_surface, (x, y))
        elif type == "title":
            text_surface = title_font.render(text, True, color)
            screen.blit(text_surface, (x, y)) 

    # 隨機生成位置
    def random_position():
        x = random.randint(0, (WIDTH - CELL_SIZE) // CELL_SIZE-1) * CELL_SIZE
        y = random.randint(0, (HEIGHT - CELL_SIZE) // CELL_SIZE-1) * CELL_SIZE
        return x, y
    
    # 小遊戲：四張紙牌
    def mini_game_cards():
        result = 0
        # 生成兩張 "food" 和兩張 "score"
        cards = ["food", "food", "score", "score"]
        random.shuffle(cards) 
        card_rects = []
        card_image = pygame.transform.scale(pygame.image.load("卡牌.png"), (150, 200))
        # 顯示卡牌
        screen.blit(pygame.transform.scale(background_image, (WIDTH, HEIGHT)), (0, 0))
        draw_text("title", "Select a card", BLACK, WIDTH // 2 - 180, HEIGHT // 4)
        for i in range(4):
            card_x = 60 + i * 180
            card_y = HEIGHT // 2 - 50
            
            card_rect = pygame.Rect(card_x, card_y, 150, 200)
            screen.blit(card_image, (card_x, card_y))
            card_rects.append((card_rect, cards[i]))
        pygame.display.flip()

        # 等待玩家選擇
        selecting = True
        while selecting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return 0
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for rect, card in card_rects:
                        if rect.collidepoint(event.pos):
                            if card == "food":
                                points = random.choice([5, 10, 15])
                                result += points
                            else:
                                points = random.randint(10, 20)
                                result += points
                            draw_text("normal", f"You selected {card} Card!", BLACK, WIDTH // 2 - 200, HEIGHT // 2 + 210)
                            draw_text("normal", f"+{points} points!", BLACK, WIDTH // 2 - 200, HEIGHT // 2 + 240)
                            pygame.display.flip()
                            time.sleep(2)
                            selecting = False
            pygame.display.flip()
        time.sleep(3)
        return result

    # 初始化蛇
    snake = [(100, 100)]
    snake_dir = 'RIGHT'
    change_dir = snake_dir
    score = 0
    speed = FPS
    high_score = 0
    
    # 加載 AI 蛇的圖片資源
    ai_snake_head_image = pygame.image.load("ai_snake_head.png")
    ai_snake_head_image = pygame.transform.scale(ai_snake_head_image, (CELL_SIZE, CELL_SIZE))

    ai_snake_body_image = pygame.image.load("ai_snake_body.png")
    ai_snake_body_image = pygame.transform.scale(ai_snake_body_image, (CELL_SIZE, CELL_SIZE))

    ai_snake_tail_image = pygame.image.load("ai_snake_tail.png")
    ai_snake_tail_image = pygame.transform.scale(ai_snake_tail_image, (CELL_SIZE, CELL_SIZE))

    
    # 初始化食物和關卡
    foods = []
    for _ in range(6):
        foods.append({'pos': random_position(), 'size': random.randint(1, 3)})
    checkpoint = {'pos': random_position()}

    button_normal = pygame.image.load("排行榜.png")
    button_normal = pygame.transform.scale(button_normal, (420, 280))
    # button_rect = pygame.Rect(WIDTH // 2 - 120, HEIGHT // 2 + 130, 230, 60)
    # button_color = GRAY
    # button_hover_color = BLUE
    button_rect = button_normal.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 120))

    #排行榜參數
    HEADER_HEIGHT = 150
    SCROLLABLE_WIDTH, SCROLLABLE_HEIGHT = WIDTH, 1200  # 滾動區域的高度
    scrollable_surface = pygame.Surface((SCROLLABLE_WIDTH, SCROLLABLE_HEIGHT))
    scrollable_surface.blit(pygame.transform.scale(background_image, (SCROLLABLE_WIDTH, SCROLLABLE_HEIGHT)), (0, 0))
    scroll_y = 0
    scroll_speed = 20
    sorted_users = sorted(users_info.items(), key=lambda x: x[1]["Snake Best Score"], reverse=True)
    for index, (username, data) in enumerate(sorted_users):
        score = data["Snake Best Score"]
        player_text = font.render(username, True, BLACK)
        score_text = font.render(str(score), True, BLACK)
        scrollable_surface.blit(player_text, (50, 50 + index * 50))
        scrollable_surface.blit(score_text, (WIDTH - 200, 50 + index * 50))

    # === 插入檢查存檔邏輯 ===
    if os.path.exists("save_game.json"):
        with open("save_game.json", "r") as f:
            saved_data = json.load(f)
        
        if not is_data_valid(saved_data):  # 檢查哈希值是否有效
            # 將文字分成兩行
            line1 = "Tampered save detected!"
            line2 = "Game invalid."
            
            # 計算每一行的水平置中位置
            line1_x = WIDTH // 2 - (title_font.size(line1)[0] // 2)
            line2_x = WIDTH // 2 - (title_font.size(line2)[0] // 2)
            
            # 高度設置
            line1_y = HEIGHT // 2 - 30  # 第一行高度
            line2_y = HEIGHT // 2       # 第二行高度

            # 顯示每一行文字
            draw_text("title", line1, RED, line1_x, line1_y)
            draw_text("title", line2, RED, line2_x, line2_y)

            pygame.display.flip()
            time.sleep(5)  # 停留5秒
            os.remove("save_game.json")  # 刪除無效存檔
            return 0, 0, "main_menu"
        
        # 如果未篡改，則正常載入
        prompt_continue = True
        while prompt_continue:
            screen.blit(background_image, (0, 0))
            # 顯示標題，橫軸置中
            draw_text("title", "Saved game detected!", BLACK, WIDTH // 2 - (title_font.size("Saved game detected!")[0] // 2), HEIGHT // 2 - 80)
            # 顯示第一行文字，橫軸置中
            draw_text("normal", "Press 'Y' to continue", BLACK, WIDTH // 2 - (font.size("Press 'Y' to continue")[0] // 2), HEIGHT // 2 + 10)
            # 顯示第二行文字，橫軸置中
            draw_text("normal", "or 'N' to start new game.", BLACK, WIDTH // 2 - (font.size("or 'N' to start new game.")[0] // 2), HEIGHT // 2 + 40)


            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_y:
                        # 載入存檔
                        snake = saved_data["snake"]
                        snake_dir = saved_data["snake_dir"]
                        score = saved_data["score"]
                        foods = saved_data["foods"]
                        checkpoint = saved_data["checkpoint"]
                        speed = saved_data["speed"]
                        original_high_score = saved_data["high_score"]
                        prompt_continue = False
                    elif event.key == pygame.K_n:
                        # 開始新遊戲
                        prompt_continue = False
                        os.remove("save_game.json")  # 刪除存檔
    
    # 遊戲主循環
    running = True
    pause = False
    state = 'START'
    # 在主迴圈外初始化閃爍變數
    blink = True  # 是否顯示文字
    blink_time = 500  # 閃爍間隔時間（毫秒）
    last_blink = pygame.time.get_ticks()  # 上一次閃爍的時間
    
    while running:
        screen.blit(background_image, (0, 0))
        mouse_pos = pygame.mouse.get_pos()

        if state == 'START':
            screen.blit(background_image, (0, 0))
            draw_text("title", "Welcome to Gourmet Train!", BLACK, WIDTH // 2 - 340, HEIGHT // 2 - 80)
            # 檢查是否需要切換閃爍狀態
            current_time = pygame.time.get_ticks()
            if current_time - last_blink > blink_time:
                blink = not blink  # 切換顯示狀態
                last_blink = current_time  # 更新最後閃爍時間

            # 如果 blink 為 True，顯示文字
            if blink:
                draw_text("normal", "Press 'Enter' to start.", BLACK, WIDTH // 2 - 240, HEIGHT // 2 + 10)

            screen.blit(button_normal, button_rect.topleft)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        state = 'RUNNING'
                        break
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if button_rect.collidepoint(event.pos):
                        print("按鈕被點擊！")
                        state = 'LEARDERBOARD'
                        break
        
        elif state == 'LEARDERBOARD':
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        state = 'START'
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 4:  # 滾輪向上
                        scroll_y = max(scroll_y - scroll_speed, 0)
                    elif event.button == 5:  # 滾輪向下
                        scroll_y = min(scroll_y + scroll_speed, SCROLLABLE_HEIGHT - (HEIGHT - HEADER_HEIGHT))
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        state = 'START'
                        
            screen.blit(background_image, (0, 0))
            
            # 繪製滾動區域
            screen.blit(scrollable_surface, (0, HEADER_HEIGHT - scroll_y))

            # 繪製固定區域
            top = pygame.transform.scale(pygame.image.load('Leaderboard_page.png'), (WIDTH, HEADER_HEIGHT))
            screen.blit(top, (0,0))

            # 更新畫面
            pygame.display.flip()
            
        elif state == 'RUNNING':
            
            # 處理事件
            screen.blit(background_image, (0, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if not pause:  # 如果不是暫停狀態，處理方向鍵
                        if event.key == pygame.K_UP and snake_dir != 'DOWN':
                            change_dir = 'UP'
                        elif event.key == pygame.K_DOWN and snake_dir != 'UP':
                            change_dir = 'DOWN'
                        elif event.key == pygame.K_LEFT and snake_dir != 'RIGHT':
                            change_dir = 'LEFT'
                        elif event.key == pygame.K_RIGHT and snake_dir != 'LEFT':
                            change_dir = 'RIGHT'

                    if event.key == pygame.K_k:  # 切換暫停狀態
                        print('press k')
                        pause = not pause
                        if pause:  # 如果是暫停，顯示暫停訊息
                            draw_text("title", "Paused.", BLACK, WIDTH // 2 - 70, HEIGHT // 2 - 40)
                            draw_text("title", "Press 'K' to continue.", BLACK, WIDTH // 2 - 280, HEIGHT // 2 + 10)
                            pygame.display.flip()
                    if event.key == pygame.K_f:
                        save_data = {
                            "snake": snake,
                            "snake_dir": snake_dir,
                            "score": score,
                            "foods": foods,
                            "checkpoint": checkpoint,
                            "speed": speed,
                            "high_score": original_high_score
                        }
                        save_data["hash"] = calculate_hash(save_data)  # 計算哈希值並加入
                        with open("save_game.json", "w") as f:
                            json.dump(save_data, f)

                        print('press f')
                        draw_text("title", "Game Saved Successfully!", BLACK, WIDTH // 2 - (title_font.size("Game Saved Successfully!")[0] // 2), HEIGHT // 2)

                        pygame.display.flip()
                        time.sleep(2)
                        return 0, 0, "main_menu"
                    elif event.key == pygame.K_r:
                        print('press r')
                        draw_text("title", "Restarting...", BLACK, WIDTH // 2 - 180, HEIGHT // 2 - 30)
                        pygame.display.flip()
                        time.sleep(2)
                        
                        # 重置遊戲狀態
                        snake = [(100, 100)]
                        snake_dir = 'RIGHT'
                        change_dir = snake_dir
                        score = 0
                        speed = FPS
                        foods = [{'pos': random_position(), 'size': random.randint(1, 3)} for _ in range(6)]
                        checkpoint = {'pos': random_position()}
                        state = 'START'  # 確保狀態重置為遊戲運行

            # 暫停邏輯
            while pause:  # 進入暫停內部循環
                for pause_event in pygame.event.get():
                    if pause_event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif pause_event.type == pygame.KEYDOWN and pause_event.key == pygame.K_k:
                        # 倒數邏輯
                        for i in range(3, 0, -1):
                            screen.blit(background_image, (0, 0))

                            # 繪製食物
                            for food in foods:
                                food_img = food_images[food['size']]
                                screen.blit(food_img, food['pos'])

                            # 繪製蛇
                            for index, segment in enumerate(snake):
                                if index == 0:
                                    screen.blit(snake_head_image, segment)
                                else:
                                    screen.blit(snake_body_image, segment)

                            # 繪製倒數文字
                            draw_text("title", f"Resuming in {i}...", BLACK, WIDTH // 2 - 180, HEIGHT // 2 - 20)
                            pygame.display.flip()
                            time.sleep(1)  # 等待一秒

                        pause = False
                continue

            # 更新蛇的位置
            if not pause:
                snake_dir = change_dir
                head_x, head_y = snake[0]
                if snake_dir == 'UP':
                    head_y -= CELL_SIZE
                if snake_dir == 'DOWN':
                    head_y += CELL_SIZE
                if snake_dir == 'LEFT':
                    head_x -= CELL_SIZE
                if snake_dir == 'RIGHT':
                    head_x += CELL_SIZE

                new_head = (head_x, head_y)
                snake.insert(0, new_head)
                
            # 更新 AI 蛇
            ai_snake, ai_snake_dir, score, ai_alive, ai_respawn_timer, ai_speed = update_ai_snake(ai_snake, ai_snake_dir, foods, score, ai_alive, ai_respawn_timer, respawn_duration)
            print(ai_alive)
            # 在主遊戲迴圈的 `RUNNING` 狀態中
            if not ai_alive:
                
                # 如果 AI 蛇不活躍，計算剩餘時間
                remaining_time = int(respawn_duration - (time.time() - ai_respawn_timer))
                if remaining_time > 0:
                    # 繪製倒數文字
                    draw_text(
                        "normal",
                        f"Enemy Reviving...in {remaining_time}",
                        BLACK,
                        WIDTH // 2 - 200,
                        HEIGHT // 2 - 10
                    )
                else:
                    # 倒數結束，讓 AI 蛇重生
                    ai_alive = True
                    ai_respawn_timer = 0
                    ai_snake = [(WIDTH - 100, HEIGHT - 100)]  # 重置位置
                    ai_snake_dir = 'LEFT'  # 重置方向
            # 碰撞檢查：玩家蛇頭與電腦蛇
            for ai_segment in ai_snake:
                if new_head == ai_segment:  # 玩家蛇頭與電腦蛇的任何一節重疊
                    if score > high_score:
                        high_score = score
                    state = "GAME OVER"
                    break
            
            if new_head in snake[1:] or not (0 <= head_x < WIDTH and 0 <= head_y < HEIGHT):
                if score > high_score:
                    high_score = score
                state = "GAME OVER"
                
            # 檢查 AI 是否吃到食物
            check_ai_eat_food(ai_snake, foods)

                # 繪製 AI 蛇
            if ai_alive:
                for index, segment in enumerate(ai_snake):
                    if index == 0:
                        # 旋轉並繪製蛇頭
                        if ai_snake_dir == 'UP':
                            rotated_head = pygame.transform.rotate(ai_snake_head_image, 90)
                        elif ai_snake_dir == 'DOWN':
                            rotated_head = pygame.transform.rotate(ai_snake_head_image, 270)
                        elif ai_snake_dir == 'LEFT':
                            rotated_head = pygame.transform.rotate(ai_snake_head_image, 0)
                        elif ai_snake_dir == 'RIGHT':
                            rotated_head = pygame.transform.rotate(ai_snake_head_image, 0)
                        screen.blit(rotated_head, (segment[0], segment[1]))
                    else:
                        # 旋轉並繪製蛇頭
                        if ai_snake_dir == 'UP':
                            rotated_body = pygame.transform.rotate(ai_snake_body_image, 90)
                        elif ai_snake_dir == 'DOWN':
                            rotated_body = pygame.transform.rotate(ai_snake_body_image, 270)
                        elif ai_snake_dir == 'LEFT':
                            rotated_body = pygame.transform.rotate(ai_snake_body_image, 0)
                        elif ai_snake_dir == 'RIGHT':
                            rotated_body = pygame.transform.rotate(ai_snake_body_image, 0)
                        screen.blit(rotated_head, (segment[0], segment[1]))

            # 檢查是否吃到食物
            for food in foods:
                food_rect = pygame.Rect(
                    food['pos'][0] + (CELL_SIZE - food_images[food['size']].get_width()) // 2,
                    food['pos'][1] + (CELL_SIZE - food_images[food['size']].get_height()) // 2,
                    food_images[food['size']].get_width(),
                    food_images[food['size']].get_height()
                )
            
                snake_head_rect = pygame.Rect(head_x, head_y, CELL_SIZE, CELL_SIZE)
                
                if snake_head_rect.colliderect(food_rect):  # 使用碰撞檢測
                    score += FOOD_SCORES[food['size']]
                    foods.remove(food)
                    foods.append({'pos': random_position(), 'size': random.randint(1, 3)})
                    speed += 0.5
                    break
            else:
                snake.pop()

            # 繪製食物
            for food in foods:
                food_img = food_images[food['size']]
                screen.blit(food_img, food['pos'])
                
            # 碰到自己或邊界，遊戲結束
            if new_head in snake[1:] or not (0 <= head_x < WIDTH and 0 <= head_y < HEIGHT):
                if score > high_score:
                    high_score = score
                state = "GAME OVER"
            
            
            # 碰撞檢查關卡
            checkpoint_rect = pygame.Rect(checkpoint['pos'][0], checkpoint['pos'][1], CELL_SIZE, CELL_SIZE)
            snake_head_rect = pygame.Rect(head_x, head_y, 40, 40)

            if snake_head_rect.colliderect(checkpoint_rect):
                score += mini_game_cards()
                checkpoint['pos'] = random_position()
                
                for i in range (3,0,-1):
                    screen.blit(background_image,(0,0))
                    
                    for food in foods:
                        food_img = food_images[food['size']]
                        screen.blit(food_img,food['pos'])
                        
                    for index, segment in enumerate(snake):
                        if index == 0:
                            screen.blit(snake_head_image, segment)           
                        else:
                            screen.blit(snake_body_image, segment)
                            
                    screen.blit(checkpoint_image, checkpoint['pos'])
                    
                    draw_text("normal", f"Score: {score}", BLACK, 10, 10)
                              
                    draw_text("normal", f"High Score: {original_high_score}", BLACK, 10, 50)
                    
                    draw_text("title", f"Game Resumes in {i} s...", BLACK, WIDTH // 2 - 280, HEIGHT // 2 - 20)
                    pygame.display.flip()
                    time.sleep(1)
            
            # 繪製關卡
            screen.blit(checkpoint_image, checkpoint['pos'])
            
            # 繪製蛇
            for index, segment in enumerate(snake):
                if index == 0:
                    if snake_dir == 'UP':
                        rotated_head = pygame.transform.rotate(snake_head_image, 90)
                    elif snake_dir == 'DOWN':
                        rotated_head = pygame.transform.rotate(snake_head_image, 270)
                    elif snake_dir == 'LEFT':
                        rotated_head = pygame.transform.rotate(snake_head_image, 0)
                    elif snake_dir == 'RIGHT':
                        rotated_head = pygame.transform.rotate(snake_head_image, 0)
                    screen.blit(rotated_head, segment)
                else:
                    if snake_dir == 'UP':
                        rotated_body = pygame.transform.rotate(snake_body_image, 90)
                    elif snake_dir == 'DOWN':
                        rotated_body = pygame.transform.rotate(snake_body_image, 270)
                    elif snake_dir == 'LEFT':
                        rotated_body = pygame.transform.rotate(snake_body_image, 0)
                    elif snake_dir == 'RIGHT':
                        rotated_body = pygame.transform.rotate(snake_body_image, 0)
                    screen.blit(rotated_body, segment)

            # 繪製分數
            draw_text("normal", f"Score: {score}", BLACK, 10, 10)
            draw_text("normal", f"High Score: {original_high_score}", BLACK, 10, 50)

            pygame.display.flip()
            pygame.time.Clock().tick(int(speed))
            
        if state == "GAME OVER":
            # 確定最佳分數
            best_score = max(score, original_high_score)

            # 顯示 Game Over 畫面
            screen.blit(background_image, (0, 0))
            draw_text("title", f"Game Over! Final Score: {score}", BLACK, WIDTH // 2 - 375, HEIGHT // 2 - 30)
            
            # 第一段文字
            text1 = "If you didn't surpass your best score "
            text1_x = WIDTH // 2 - font.size(text1)[0] // 2
            draw_text("normal", text1, BLACK, text1_x, HEIGHT // 2 + 50)

            # 第二段文字
            text2 = "Try Again!"
            text2_x = WIDTH // 2 - font.size(text2)[0] // 2
            draw_text("normal", text2, BLACK, text2_x, HEIGHT // 2 + 80)

            pygame.display.flip()
            time.sleep(3)

            # 更新排行榜分數
            users_file = "users.json"
            if os.path.exists(users_file):
                with open(users_file, "r") as f:
                    users = json.load(f)
            else:
                users = {}

            # 確保有當前玩家的數據
            current_user = "player_name"  # 替換為玩家的用戶名
            if current_user not in users:
                users[current_user] = {"Snake Best Score": 0}

            # 更新當前玩家的最高分數
            users[current_user]["Snake Best Score"] = max(users[current_user]["Snake Best Score"], score)

            # 將更新後的數據寫入文件
            with open(users_file, "w") as f:
                json.dump(users, f, indent=4)

            # 清除存檔文件
            if os.path.exists("save_game.json"):
                os.remove("save_game.json")

            # 返回主選單或重新開始
            running = False
            
        elif state == "RESTART":
            # 玩家選擇重新開始
            draw_text("title", "Restarting...", BLACK, WIDTH // 2 - 180, HEIGHT // 2 - 30)
            pygame.display.flip()
            time.sleep(2)

            # === 清除存檔 ===
            if os.path.exists("save_game.json"):
                os.remove("save_game.json")

            return 0, 0, "snake"
            
    return score, best_score, "main_menu"

if __name__ == "__main__":
    game_control = {"paused": False, "restart": False}
    state = ''
    print(run_snake(10, users_info = {}))
    # current_score, best_score, state = run_snake(10) 
    # print(f"Score: {current_score}, Best Score: {best_score}, State: {state}")