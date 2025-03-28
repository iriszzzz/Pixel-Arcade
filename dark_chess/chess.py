import sys
import traceback
import pygame
import random
from dark_chess import chess_pieces
import time
import math
from dark_chess.chess_pieces import ChessPiece, makeMove, move
import os
import json
def save_game_state(file_path, chess_board, player_role, no_eat_count, overturn_count, playerClicks, current_color):
    game_state = {
        "chess_board": [
            [
                {
                    "type": type(piece).__name__,
                    "position": piece.position,
                    "role": piece.role,
                    "state": piece.state
                } if piece else None for piece in row
            ] for row in chess_board
        ],
        "player_role": player_role,
        "no_eat_count": no_eat_count,
        "overturn_count": overturn_count,
        "playerClicks": playerClicks,
        "current_color": current_color  # 保存當前顏色
    }
    with open(file_path, "w",encoding="utf-8") as file:
        json.dump(game_state, file, ensure_ascii=False, indent=4)
    print("遊戲狀態已保存")
    print(game_state)
    return game_state
# 初始化 Pygame
pygame.init()

# 設定窗口尺寸
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
bg_rect = screen.get_rect() # 獲取屏幕的邊界作為背景矩形，確保棋子的位置範圍在棋盤
pygame.display.set_caption("暗棋")

# 顏色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BACKGROUND_COLOR = (240, 230, 200)

# 棋盤的參數
grid_size = 90
board_margin = 40
board_width = 8 * grid_size
board_height = 4 * grid_size

# 加載棋子圖片
try:
    back_image = pygame.image.load("dark_chess/images/blankchess.png").convert_alpha()  # 棋子的背面圖片
    back_image = pygame.transform.scale(back_image, (grid_size - 10, grid_size - 10))  # 縮放圖片
    back_image.set_alpha(255)  # 設定透明度（0 完全透明，255 完全不透明）

    chess_select1_img = pygame.image.load('dark_chess/images/black_select.png').convert_alpha()
    chess_select2_img = pygame.image.load('dark_chess/images/red_select.png').convert_alpha()
except pygame.error as e:
    print(f"Error loading image: {e}")
    exit()
background_image = pygame.image.load("dark_chess/images/背景圖.png")
background_image = pygame.transform.scale(background_image, (screen_width, screen_height))
# 初始化選中棋子的矩形
selected_img_rect = [
    chess_select1_img.get_rect(),
    chess_select2_img.get_rect()
]

# chess_class = []  # 存放所有棋子的列表

# for j in range(2):  # 迴圈執行兩次，生成雙方的棋子
#     chess_class.append(chess_pieces.JiangChess(bg_rect))  # 每方 1 枚將（或帥）
#     for i in range(2):  # 士、象、馬、車、炮各 2 枚
#         chess_class.append(chess_pieces.ShiChess(bg_rect))   # 士棋
#         chess_class.append(chess_pieces.XiangChess(bg_rect)) # 象棋
#         chess_class.append(chess_pieces.MaChess(bg_rect))    # 馬棋
#         chess_class.append(chess_pieces.CheChess(bg_rect))   # 車棋
#         chess_class.append(chess_pieces.PaoChess(bg_rect))   # 炮棋
#     for i in range(5):  # 每方 5 名兵（或卒）
#         chess_class.append(chess_pieces.ZuChess(bg_rect))

# # 一半的棋子為黑色
# for i in range(len(chess_class) // 2):  # 將前一半棋子設置為黑色
#     chess_class[i].role = chess_pieces.BLACK_ROLE

running = True

# 假設初始玩家先設置黑
#player_role = chess_pieces.BLACK_ROLE #1
    
def initialize_chess_class():
    chess_class = []
    for j in range(2):  # 迴圈執行兩次，生成雙方的棋子
        chess_class.append(chess_pieces.JiangChess(bg_rect))  # 每方 1 枚將（或帥）
        for i in range(2):  # 士、象、馬、車、炮各 2 枚
            chess_class.append(chess_pieces.ShiChess(bg_rect))   # 士棋
            chess_class.append(chess_pieces.XiangChess(bg_rect)) # 象棋
            chess_class.append(chess_pieces.MaChess(bg_rect))    # 馬棋
            chess_class.append(chess_pieces.CheChess(bg_rect))   # 車棋
            chess_class.append(chess_pieces.PaoChess(bg_rect))   # 炮棋
        for i in range(5):  # 每方 5 名兵（或卒）
            chess_class.append(chess_pieces.ZuChess(bg_rect))

    # 一半的棋子為黑色
    for i in range(len(chess_class) // 2):  # 將前一半棋子設置為黑色
        chess_class[i].role = chess_pieces.BLACK_ROLE

    return chess_class

#切換玩家角色
def operation_completed():
    global player_role, current_color
    if player_role == chess_pieces.BLACK_ROLE:
        player_role = chess_pieces.RED_ROLE
        current_color = RED
    else:
        player_role = chess_pieces.BLACK_ROLE
        current_color = BLACK

def getChessBoard(chess_class):

    resultList = random.sample(range(0, 32), 32)  # 隨機生成棋子排列
    chess_board = [[None for _ in range(8)] for _ in range(4)]  # 4x8 棋盤初始化

    j = 0  # 對應棋子索引
    for i in resultList:
        col = i % 8  # 計算列數
        row = i // 8  # 計算行數

        x = board_margin + col * grid_size + 11
        y = board_margin + row * grid_size + 11

        # 更新棋子的行列位置
        chess_class[j].position = (row, col)
        chess_class[j].rect.topleft = (x, y)
        chess_board[row][col] = chess_class[j]  # 放置到棋盤上
        j += 1

    return chess_board


def is_chess_clicked(chess_board, event):

    # location = pygame.mouse.get_pos()  # 獲取滑鼠點擊的位置
    # row = (location[1] - board_margin) // grid_size
    # col = (location[0] - board_margin) // grid_size
    for row in chess_board:  # 第一層迴圈遍歷行
        for each in row:     # 第二層迴圈遍歷每一個棋子
            if each is not None and each.rect.collidepoint(event.pos):  # 避免空格子
                return each  # 返回點擊到的棋子對象
    return None #(row, col)

        
def write(msg="pygame is cool", color=(150, 150, 150), position=(50, 50), screen=None, font_size=30):
 
    font_path = "dark_chess/Silkscreen-Regular (1).ttf"
    try:
        myfont = pygame.font.Font(font_path, font_size)
        mytext = myfont.render(msg, True, color)
        mytext = mytext.convert_alpha()
        if screen:
            screen.blit(mytext, position)
    except Exception as e:
        print(f"error text: {e}")

def count_pieces(chess_board):
    black_count = sum(
        1 for row in chess_board for each in row
        if each is not None and each.role == chess_pieces.BLACK_ROLE and each.state in (chess_pieces.ACTIVE_STATE, chess_pieces.HIDDEN_STATE)
    )
    red_count = sum(
        1 for row in chess_board for each in row
        if each is not None and each.role == chess_pieces.RED_ROLE and each.state in (chess_pieces.ACTIVE_STATE, chess_pieces.HIDDEN_STATE)
    )
    return black_count, red_count

button_color = (192, 192, 192)
text_color = (255, 255, 255)
button_center = (150, 455)
button_radius = 100
button_text = "START"
def draw_circle_button(screen, color, center, radius, text, text_color, font):
    pygame.draw.circle(screen, color, center, radius)
    button_text = font.render(text, True, text_color)
    text_rect = button_text.get_rect(center=center)
    screen.blit(button_text, text_rect)

def is_circle_clicked(mouse_pos, center, radius):
    return (mouse_pos[0] - center[0])**2 + (mouse_pos[1] - center[1])**2 <= radius**2

def draw_buttons(screen):
    
    exit_button = pygame.Rect(50, 15, 75, 25)
    restart_button = pygame.Rect(675, 15, 75, 25)

    
    # 退出
    pygame.draw.rect(screen, WHITE, exit_button)
    write("Exit", (192,192,192), position=(65, 17), screen=screen, font_size=15)

    # 重新
    pygame.draw.rect(screen, WHITE, restart_button)
    write("Restart", (192,192,192), position=(675, 17), screen=screen, font_size=15)


    return exit_button, restart_button

def draw_chess_board(screen, chess_board):
    screen.fill(BACKGROUND_COLOR)
    for row in range(len(chess_board)):
        for col in range(len(chess_board[row])):
            # 格子
            pygame.draw.rect(
                screen,
                (200, 200, 200) if (row + col) % 2 == 0 else (150, 150, 150),
                (board_margin + col * grid_size, board_margin + row * grid_size, grid_size, grid_size),
            )

    # # 繪製棋子
    # for row in chess_board:  # 第一層迭代，獲取每一行
    #     for each in row:     # 第二層迭代，獲取每一個棋子
    #         if each is not None :
    #             screen.blit(each.getImage(each.role), each.rect)

    # 邊框
    pygame.draw.rect(screen, (0, 0, 0), (board_margin, board_margin, len(chess_board[0]) * grid_size, len(chess_board) * grid_size), 3)

def main(user, record):
    def load_game_state(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                game_state = json.load(file)
             # 將字典形式的棋盤還原為棋子物件
            chess_board = [
                [
                    ChessPiece.from_dict(piece) if piece else None
                    for piece in row
                ]
                for row in game_state["chess_board"]
            ]

            player_role = game_state["player_role"]
            no_eat_count = game_state["no_eat_count"]
            overturn_count = game_state["overturn_count"]
            playerClicks = game_state["playerClicks"]
            current_color = tuple(game_state["current_color"])  # 恢復當前顏色
            # print("成功載入遊戲狀態")
            return {
                "chess_board": chess_board,
                "player_role": player_role,
                "no_eat_count": no_eat_count,
                "overturn_count": overturn_count,
                "playerClicks": playerClicks,
                "current_color": current_color,
            }
            
        except (FileNotFoundError, KeyError, ValueError) as e:
            print(f"載入遊戲狀態失敗: {e}")
            return None


    overturn_count = 0 #翻棋
    no_eat_count = 0

    clock = pygame.time.Clock()

    #chess_list = getChessList()
    chess_board = getChessBoard(initialize_chess_class())

    sqselected = () #(row,col)
    playerClicks = [] #[(row,col),(row,col)]

    # 設置初始位置為 (-100, -100)，即畫布外，表示暫時沒有選中棋子
    for rect in selected_img_rect:
        print(type(rect))  # 應該輸出 <class 'pygame.Rect'>
        rect.topleft = (-100, -100)
        
    global player_role

    player1_role = chess_pieces.BLACK_ROLE
    player1_color = ( 0, 0, 0 )
    player2_role = chess_pieces.RED_ROLE
    player2_color = ( 128, 128, 128 )

    exp = 0
    global running
    pause = False
    state = 'START'
    
    is_loaded = False if len(record) != 0 else True
    
    while running:
        if state == 'START':
            if os.path.exists("saved_game.json"):
                # 顯示“繼續遊戲”選項
                screen.blit(background_image, (0, 0))
                continue_button = pygame.Rect(600, 535, 200, 50)
                pygame.draw.rect(screen, (192,192,192), continue_button)
                write(f"continue", WHITE, position=(screen_width-200, 530), screen=screen, font_size=35)

            font_path = "dark_chess/Silkscreen-Regular (1).ttf"
            font_size=55
            # 計算脈動效果的字體大小
            pulse_speed = 2  # 控制脈動速度，數值越小頻率越慢
            pulse_scale = 10 * math.sin(pygame.time.get_ticks() * 0.003 * pulse_speed) + font_size
            font = pygame.font.Font(font_path, int(pulse_scale))
            draw_circle_button(screen, button_color, button_center, button_radius, button_text, text_color, font)
            write(f"start", BLACK, position=(screen_width-740, 410), screen=screen, font_size=55)

            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    if is_circle_clicked(event.pos, button_center, button_radius):
                        restart = True
                        chess_board = getChessBoard(initialize_chess_class())
                        player_role = chess_pieces.BLACK_ROLE
                        no_eat_count = 0
                        overturn_count = 0
                        playerClicks = []
                        current_color = (0,0,0)
                        state ="RUNNING"
                        break
                    #mouse_pos = event.pos
                    elif continue_button.collidepoint(mouse_pos):
                        restart = False
                        state ="RUNNING"
                        break
        
        elif state == 'RUNNING':

            if not is_loaded:  # 有過往紀錄
                if restart:
                    chess_board = getChessBoard(initialize_chess_class())
                    player_role = chess_pieces.BLACK_ROLE
                    no_eat_count = 0
                    overturn_count = 0
                    playerClicks = []
                    current_color = (0,0,0)
                else:
                    if os.path.exists("saved_game.json"):
                        loaded_state = load_game_state("saved_game.json")
                        if loaded_state:
                            chess_board = loaded_state["chess_board"]
                            player_role = loaded_state["player_role"]
                            no_eat_count = loaded_state["no_eat_count"]
                            overturn_count = loaded_state["overturn_count"]
                            playerClicks = loaded_state["playerClicks"]
                            current_color = tuple["current_color"]

                            # 確保載入的狀態完整
                            if not chess_board or player_role is None:
                                print("載入的遊戲狀態不完整，初始化新遊戲")
                                chess_board = getChessBoard(initialize_chess_class())  # 初始化新遊戲
                                player_role = chess_pieces.BLACK_ROLE
                                no_eat_count = 0
                                overturn_count = 0
                                playerClicks = []
                                current_color = (0,0,0)
                                
                        else:
                            print("無法載入遊戲狀態，初始化新遊戲")
                            chess_board = getChessBoard(initialize_chess_class())
                            player_role = chess_pieces.BLACK_ROLE
                            no_eat_count = 0
                            overturn_count = 0
                            playerClicks = []
                            current_color = (0,0,0)
                    else:
                        print("存檔不存在，初始化新遊戲")
                        chess_board = getChessBoard(initialize_chess_class())
                        player_role = chess_pieces.BLACK_ROLE
                        no_eat_count = 0
                        overturn_count = 0
                        playerClicks = []
                        current_color = (0,0,0)
            
            is_loaded = True
                
            
            screen.fill(BACKGROUND_COLOR)  # 填充背景
            draw_chess_board(screen, chess_board)
            exit_button, restart_button = draw_buttons(screen)

            # 繪製橫線
            for row in range(5):
                y = board_margin + row * grid_size
                pygame.draw.line(screen, BLACK, (board_margin, y), (board_margin + board_width, y), 2)
            # 繪製縱線
            for col in range(9):
                x = board_margin + col * grid_size
                pygame.draw.line(screen, BLACK, (x, board_margin), (x, board_margin + board_height), 2)

            # 繪製最上和最下的加粗橫線
            pygame.draw.line(screen, BLACK, (board_margin, board_margin - 2), (board_margin + board_width, board_margin - 2), 2)  # 最上
            pygame.draw.line(screen, BLACK, (board_margin, board_margin + board_height + 2), (board_margin + board_width, board_margin + board_height + 2), 2)  # 最下
            # 繪製最左和最右的加粗縱線
            pygame.draw.line(screen, BLACK, (board_margin - 2, board_margin), (board_margin - 2, board_margin + board_height), 2)  # 最左
            pygame.draw.line(screen, BLACK, (board_margin + board_width + 2, board_margin), (board_margin + board_width + 2, board_margin + board_height), 2)  # 最右
            
            # 字體初始化
            current_player = "player1" if player_role == player1_role else "player2"
            player1_color = BLACK if player1_role == chess_pieces.BLACK_ROLE else RED
            player2_color = RED if player2_color == chess_pieces.RED_ROLE else BLACK
            current_color = player1_color if player_role == player1_role else player2_color
            write(f"{current_player} turn", current_color, position=(250, 450), screen=screen, font_size=36)
            selected_timer = None
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # if not pause:
                        mouse_pos = event.pos
                        if exit_button.collidepoint(mouse_pos):
                            print("退出")
                            game_state = save_game_state("saved_game.json", chess_board, player_role, no_eat_count, overturn_count, playerClicks,current_color)
                            # state = 'START'
                            exp = 0
                            return exp, game_state,"main_menu"
                        
                        elif restart_button.collidepoint(mouse_pos):
                            print("重新開始")
                            # chess_class = initialize_chess_class()  # 重新生成棋子列表
                            chess_board = getChessBoard(initialize_chess_class())  # 根據新的棋子列表生成棋盤
                            player_role = chess_pieces.BLACK_ROLE  # 設置初始玩家角色
                            player_role = player1_role
                            overturn_count = 0  # 翻棋次數
                            no_eat_count = 0  # 無吃子次數
                            playerClicks = []  # 玩家點擊記錄
                            sqselected = ()  # 選中的棋子
                            selected_img_rect[0].topleft = (-100, -100)  # 隱藏另一個框
                            selected_img_rect[1].topleft = (-100, -100)  # 隱藏另一個框
                            
                            state = 'RUNNING'  # 確保狀態重置為遊戲運行

                        selected = is_chess_clicked(chess_board, event)
                        # print(selected)

                        location = pygame.mouse.get_pos() # (x, y)
                        CurrentRow = ((location[1]-board_margin )// 90)
                        CurrentCol = ((location[0]-board_margin )// 90)
                        print(CurrentRow,CurrentCol)
                        sqselected = (CurrentRow,CurrentCol)

                            # 如果返回的是棋子對象
                        if isinstance(selected, chess_pieces.ChessPiece):  # 假設 ChessPiece 是棋子類型的基類

                            # 根據棋子的顏色顯示對應的框
                            if selected.role == chess_pieces.BLACK_ROLE:
                                selected_img_rect[0].left = selected.rect.left
                                selected_img_rect[0].top = selected.rect.top
                                selected_img_rect[1].topleft = (-100, -100)  # 隱藏另一個框
                            elif selected.role == chess_pieces.RED_ROLE:
                                selected_img_rect[1].left = selected.rect.left
                                selected_img_rect[1].top = selected.rect.top
                                selected_img_rect[0].topleft = (-100, -100)  # 隱藏另一個框

                            # 設置顯示計時
                            selected_timer = pygame.time.get_ticks()

    
                            # 選擇進行吃子或移動
                            if len(playerClicks) == 0:
                                if selected.state == chess_pieces.HIDDEN_STATE :

                                    selected.state = chess_pieces.ACTIVE_STATE

                                    if overturn_count == 0:
                                        player_role = selected.role
                                        # 玩家第一次翻棋，確定玩家/電腦角色
                                        player1_role = selected.role
                                        player1_color = BLACK if player1_role == chess_pieces.BLACK_ROLE else RED
                                        player2_role = chess_pieces.RED_ROLE if player1_role == chess_pieces.BLACK_ROLE else chess_pieces.BLACK_ROLE
                                        player2_color = RED if player1_color == BLACK else BLACK
                                        #player_role = player1_role  # 設置當前玩家角色
                                        current_color = player1_color if player_role == player1_role else player2_color
                                        write(f"{current_player} turn", current_color, position=(250, 450), screen=screen, font_size=36)
                                    overturn_count += 1
                                    no_eat_count += 1
                                    
                                    selected_color = BLACK if selected.role == chess_pieces.BLACK_ROLE else RED
                                    # 非第一次翻棋
                                    if overturn_count>1:
                                        if selected_color != current_color:
                                            # 如果翻到的是非玩家顏色的棋子，完成回合
                                            #player_role != selected.role
                                            current_color = player1_color if player_role == player1_role else player2_color
                                            write(f"{current_player} turn", current_color, position=(250, 450), screen=screen, font_size=36)
                                            operation_completed()
                                            print(f"翻到非玩家顏色的棋子，回合完成")
                                        else:
                                            current_color = player1_color if player_role == player1_role else player2_color
                                            write(f"{current_player} turn", current_color, position=(250, 450), screen=screen, font_size=36)
                                            continue

                                else:
                                    if player_role == selected.role:
                                        current_color = player1_color if player_role == player1_role else player2_color
                                        write(f"{current_player} turn", current_color, position=(250, 450), screen=screen, font_size=36)
                                        playerClicks.append(selected.position)
                                        print("選中棋子，請選擇目標位置")
                                        print(playerClicks)
                                    else:
                                        current_color = player1_color if player_role == player1_role else player2_color
                                        write(f"{current_player} turn", current_color, position=(250, 450), screen=screen, font_size=36)
                                        print("無效操作：不能操作對方的棋子")
                                        continue
                                    
                            elif len(playerClicks) == 1:
                                if selected.state == chess_pieces.HIDDEN_STATE:
                                    # 翻開棋子並記錄位置
                                    selected.state = chess_pieces.ACTIVE_STATE
                                    print(f"翻開棋子: {selected.type} at {selected.position}")
                                    playerClicks.append(selected.position)
                                    current_color = player1_color if player_role == player1_role else player2_color
                                    write(f"{current_player} turn", current_color, position=(250, 450), screen=screen, font_size=36)
                                    print(playerClicks)
                                else:
                                    current_color = player1_color if player_role == player1_role else player2_color
                                    write(f"{current_player} turn", current_color, position=(250, 450), screen=screen, font_size=36)
                                    playerClicks.append(selected.position)
                                if playerClicks[0] == playerClicks[1]:
                                    print("無效操作：選中同一格子")
                                    playerClicks = []
                                else:
                                    current_color = player1_color if player_role == player1_role else player2_color
                                    write(f"{current_player} turn", current_color, position=(250, 450), screen=screen, font_size=36)
                                    move_instance = move(playerClicks[0], playerClicks[1], chess_board)
                                    target_piece = chess_board[move_instance.endRow][move_instance.endCol]
                                    if target_piece is not None:
                                        if move_instance.pieceMoved.eat(target_piece, playerClicks[1], chess_board,playerClicks, screen,operation_completed, is_chess_clicked):
                                            print("吃子成功")
                                            no_eat_count = 0 
                                            selected_img_rect[0].topleft = (-100, -100)
                                            selected_img_rect[1].topleft = (-100, -100)
    
                                        else:
                                            print("無效吃子，請重新選擇")
                                            playerClicks = []
                                            operation_completed()
                                            


                        # 如果返回的是格子位置
                        elif selected is None:
                            print(f"點擊空白格子: {selected}")
                            if len(playerClicks) == 1:  # 確保已經選中棋子
                                playerClicks.append((CurrentRow, CurrentCol))  # 記錄目標位置
                                print(f"嘗試移動到: {playerClicks[1]}")
                                # 嘗試移動
                                move_instance = move(playerClicks[0], playerClicks[1], chess_board)
                                if makeMove(chess_board, move_instance):
                                    print(f"移動成功: {playerClicks[0]} 到 {playerClicks[1]}")
                                    no_eat_count += 1
                                    current_color = player1_color if player_role == player1_role else player2_color
                                    write(f"{current_player} turn", current_color, position=(250, 450), screen=screen, font_size=36)
                                
                                    # 清除選中框
                                    selected_img_rect[0].topleft = (-100, -100)
                                    selected_img_rect[1].topleft = (-100, -100)
                                    operation_completed()
                                else:
                                    print("移動失敗")
                                    current_color = player1_color if player_role == player1_role else player2_color
                                    write(f"{current_player} turn", current_color, position=(250, 450), screen=screen, font_size=36)
                                playerClicks = []  # 清空點擊記錄
                            else:
                                print("請先選中棋子")

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_f:
                        print("退出")
                        save_game_state("saved_game.json", chess_board, player_role, no_eat_count, overturn_count, playerClicks,current_color)
                        # state = 'START'
                        exp = 0
                        return exp,"main_menu"
                
                    if event.key == pygame.K_r:
                        print("重新開始")
                        # chess_class = initialize_chess_class()  # 重新生成棋子列表
                        chess_board = getChessBoard(initialize_chess_class())  # 根據新的棋子列表生成棋盤
                        player_role = chess_pieces.BLACK_ROLE  # 設置初始玩家角色
                        player_role = player1_role
                        overturn_count = 0  # 翻棋次數
                        no_eat_count = 0  # 無吃子次數
                        playerClicks = []  # 玩家點擊記錄
                        sqselected = ()  # 選中的棋子
                        selected_img_rect[0].topleft = (-100, -100)  # 隱藏另一個框
                        selected_img_rect[1].topleft = (-100, -100)  # 隱藏另一個框
                        
                        state = 'RUNNING'  # 確保狀態重置為遊戲運行  
                   
            # 清除選中框邏輯
            if selected_timer is not None:
                current_time = pygame.time.get_ticks()
                if current_time - selected_timer >= 3000:  # 超過3秒
                    selected_img_rect[0].topleft = (-100, -100)
                    selected_img_rect[1].topleft = (-100, -100)
                    selected_timer = None  # 重置計時
            # 重繪畫面
            # screen.fill((255, 255, 255))  # 清空畫面
            # draw_chess_board(screen, chess_board)
            # 繪製選中框
            screen.blit(chess_select1_img, selected_img_rect[0])
            screen.blit(chess_select2_img, selected_img_rect[1])
            # pygame.display.flip()

            # 繪製棋子
            for row in chess_board:  # 第一層迭代，獲取每一行
                for each in row:     # 第二層迭代，獲取每一個棋子
                    if each is not None and each.state is not chess_pieces.DEAD_STATE:  # 避免空格子和死亡棋子
                        screen.blit(each.getImage(each.role), each.rect)


            # 顯示棋子數量
            black_count, red_count = count_pieces(chess_board)
            write(f"Black: {black_count}", BLACK, position=(screen_width - 760, 410), screen=screen, font_size=24)
            write(f"Red: {red_count}", RED, position=(screen_width - 760, 440), screen=screen, font_size=24)
            write(f"times: {no_eat_count}", WHITE, position=(screen_width - 760, 470), screen=screen, font_size=24)

            pygame.display.update()


            if black_count == 0:
                exp = 500 + 100 * red_count
                write(f"Red wins! Experience gained: {500 + 100 * red_count}", RED, position=(screen_width // 2, screen_height // 2), screen=screen, font_size=36)
                return exp, "main_menu"
            elif red_count == 0:
                exp = 500 + 100 * black_count
                write(f"Black wins! Experience gained: {500 + 100 * black_count}", BLACK, position=(screen_width // 2, screen_height // 2), screen=screen, font_size=36)
                return exp, "main_menu"
            elif no_eat_count >= 50:
                write(f"Draw!Game ends in a draw. No experience gained.", (255, 255, 0), (screen_width // 2, screen_height // 2), screen, font_size=36)
                exp = 0
                running = False
                return exp, "main_menu"

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        print("遊戲正常退出")
    except:
        print("遊戲退出異常")
        traceback.print_exc()
        pygame.quit()
        input()

