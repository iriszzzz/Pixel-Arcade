import pygame
# # from darkchess.constant import Constant
from pygame.locals import *
import math

screen_width, screen_height = 800, 600
# 棋盤的參數
grid_size = 90
board_margin = 40
board_width = 8 * grid_size
board_height = 4 * grid_size

RED_ROLE = 0
BLACK_ROLE = 1

BLANK_STATE =2
HIDDEN_STATE = 3
ACTIVE_STATE = 4
DEAD_STATE = 5

JIANG_TYPE = 11
SHI_TYPE = 12
XIANG_TYPE = 13
CHE_TYPE = 14
MA_TYPE = 15
PAO_TYPE = 16
ZU_TYPE = 17

bg_image = pygame.image.load('dark_chess/images/blankchess.png')
# 繪製提示文字
def draw_text(screen, text, color, x, y):
    font = pygame.font.Font("dark_chess/Silkscreen-Regular (1).ttf", 20)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))
    pygame.display.flip()  

def print_chess_board(chess_board):
    #印棋盤，只顯示棋子的類型。:param chess_board: 二維棋盤結構
    for row in chess_board:
        row_display = []
        for piece in row:
            if piece is None:
                row_display.append("Empty")  # 如果格子為空，顯示 "Empty"
            else:
                row_display.append(piece.__class__.__name__)  # 獲取棋子的類型名稱
        print(row_display)

def handle_post_eat_action(screen, chess_board, playerClicks, operation_completed, is_chess_clicked):

    # 按鈕區域
    end_turn_button = pygame.Rect(600, 450, 100, 50)

    # 按鈕顯示
    def draw_buttons():
        pygame.draw.rect(screen, (255, 0, 0), end_turn_button)  # 結束回合按鈕
        # 按鈕文字
        font_path = "dark_chess/Silkscreen-Regular (1).ttf"
        font_size=30
        font = pygame.font.Font(font_path, font_size)
        end_text = font.render("next", True, (255, 255, 255))
        screen.blit(end_text, (605, 455))


    # # 繪製提示文字
    # def draw_text( text, color, x, y):
    #     font = pygame.font.Font("dark_chess/Silkscreen-Regular (1).ttf", 20)
    #     text_surface = font.render(text, True, color)
    #     screen.blit(text_surface, (x, y))

# 重繪整個遊戲畫面
    def redraw_game_window():
        # # 繪製背景
        # screen.fill((255, 255, 255))

        # 繪製棋盤與棋子
        for row in chess_board:
            for piece in row:
                if piece is not None:
                    screen.blit(piece.getImage(piece.role), piece.rect)

        # 繪製按鈕
        draw_buttons()
        draw_text(screen,"Select the current piece or press 'next' ", (0,0,0), 150,520 )

        pygame.display.flip()

    redraw_game_window()

    # 等待玩家選擇
    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos

                # 點擊結束回合按鈕
                if end_turn_button.collidepoint(mouse_pos):
                    print("玩家選擇結束回合")
                    playerClicks.clear()
                    operation_completed()

                    return False,operation_completed  # 回合結束
                
                selected = is_chess_clicked(chess_board, event)
                if selected and selected.position != playerClicks[0]:
                    print("無效操作：只能操作當前棋子")
                elif selected and selected.position == playerClicks[0]:
                    print("可以繼續操作當前棋子")
                    return True  # 繼續操作

class move():

    def __init__(self, StartSq, EndSq, chess_board):
    
        self.startRow, self.startCol = StartSq
        self.endRow, self.endCol = EndSq

        print(self.startRow,  self.startCol , self.endRow ,self.endCol, len(chess_board), len(chess_board[0])) 
        print(chess_board[0][0])
        print_chess_board(chess_board)
        print(chess_board[self.startRow][self.startCol])
        print(chess_board[self.endRow][self.endCol])

        self.pieceMoved = chess_board[self.startRow][self.startCol]
        self.pieceCaptured = chess_board[self.endRow][self.endCol]

        if self.pieceMoved is None:
            raise ValueError(f"No piece found at start position ({self.startRow}, {self.startCol})")
    

def makeMove(chess_board, move):
    print("makeMove 被調用")
    print(f"開始位置: ({move.startRow}, {move.startCol})")
    print(f"目標位置: ({move.endRow}, {move.endCol})")
    print(f"移動的棋子: {move.pieceMoved.type}")
    # 判斷目標位置是否在合法範圍內
    possible_moves = move.pieceMoved.get_possible_moves(chess_board)
    if (move.endRow, move.endCol) not in possible_moves:
        print(f"非法移動: {move.pieceMoved.type} 無法移動到 ({move.endRow}, {move.endCol})")
        return False
    # 檢查目標位置是否為空
    if chess_board[move.endRow][move.endCol] is None:
        print("目標位置為空，執行移動")
        
        # 清空原位置
        chess_board[move.startRow][move.startCol] = None

        # 將棋子移動到新位置
        chess_board[move.endRow][move.endCol] = move.pieceMoved

        # 更新棋子的行列和圖形位置
        move.pieceMoved.position = (move.endRow, move.endCol)
        move.pieceMoved.rect.topleft = (
            board_margin + move.endCol * grid_size + 11,
            board_margin + move.endRow * grid_size + 11
        )
        return True
    else:
        print("目標位置非空，無法移動")
        return False


def can_eat(chess_a, chess_b, start_pos, end_pos, chess_board):
    typea = chess_a.type #顏色一樣，判斷位置
    typeb = chess_b.type
    if chess_a.role == chess_b.role:
        return False
    if typea == JIANG_TYPE:
        if typeb == ZU_TYPE:
            return False  # 將不能吃卒
        return True
    elif typea in (SHI_TYPE, XIANG_TYPE, CHE_TYPE, MA_TYPE): # 從大到小的順序為：帥/將 > 士 > 象 > 車 > 馬 > 炮 > 兵
        if typea <= typeb:
            return True
    elif typea == ZU_TYPE:
        if typeb == JIANG_TYPE or typeb == ZU_TYPE:
            return True
        # PAO_TYPE 邏輯
    elif typea == PAO_TYPE:
        if start_pos[0] == end_pos[0]:  # 在同一橫排
            row = start_pos[0]
            col_range = range(min(start_pos[1], end_pos[1]) + 1, max(start_pos[1], end_pos[1]))
            pieces_in_between = sum(1 for col in col_range if chess_board[row][col] is not None)
            if pieces_in_between == 1:  # 恰有一顆棋子
                return True
        elif start_pos[1] == end_pos[1]:  # 在同一縱列
            col = start_pos[1]
            row_range = range(min(start_pos[0], end_pos[0]) + 1, max(start_pos[0], end_pos[0]))
            pieces_in_between = sum(1 for row in row_range if chess_board[row][col] is not None)
            if pieces_in_between == 1:  # 恰有一顆棋子
                return True
        return False  # 不符合條件，無法吃子
    return False

class ChessPiece:
    @staticmethod
    def from_dict(data):
        if data is None:
            return None
        piece_type = data.get("type")
        position = tuple(data.get("position"))
        role = data["role"]
        state = data.get("state")

        # 根據 `type` 初始化正確的棋子類型
        piece_class_map = {
            "JiangChess": JiangChess,
            "ShiChess": ShiChess,
            "XiangChess": XiangChess,
            "MaChess": MaChess,
            "CheChess": CheChess,
            "PaoChess": PaoChess,
            "ZuChess": ZuChess
        }

        if piece_type not in piece_class_map:
            raise ValueError(f"未知的棋子類型: {piece_type}")

        # 創建棋子實例
        piece = piece_class_map[piece_type](pygame.Rect(0, 0, grid_size, grid_size))

        # 還原棋子的屬性
        piece.position = position
        piece.role = data["role"]
        piece.state = state

        # 根據 `position` 計算 `rect.topleft`
        piece.rect.topleft = (
            board_margin + position[1] * grid_size + 11,
            board_margin + position[0] * grid_size + 11
        )

        return piece

    def __init__(self, rect, r_image_path, b_image_path, piece_type, role):
        # 加載圖片
        self.r_image = pygame.image.load(r_image_path)
        self.b_image = pygame.image.load(b_image_path)
        self.position = x, y = 86, 66
        self.state = HIDDEN_STATE
        self.type = piece_type
        self.role = role
        self.rect = self.b_image.get_rect()
        self.rect.topleft = (x, y)  # 初始化為正確的起始位置
        self.rect.center = (
            board_margin + x * grid_size + grid_size // 2,
            board_margin + y * grid_size + grid_size // 2
        )
    def get_possible_moves(self, chess_board):
        """
        返回棋子的合法移動位置列表，只能上下左右一格。
        """
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # 上、下、左、右
        possible_moves = []

        for dr, dc in directions:
            new_row = self.position[0] + dr
            new_col = self.position[1] + dc

            # 檢查是否超出棋盤範圍
            if 0 <= new_row < len(chess_board) and 0 <= new_col < len(chess_board[0]):
                # 確保目標位置為空或包含敵方棋子
                target_piece = chess_board[new_row][new_col]
                if target_piece is None or target_piece.role != self.role:
                    possible_moves.append((new_row, new_col))
        return possible_moves

    def getImage(self, role):
        if self.state == HIDDEN_STATE:
            return bg_image
        elif self.state == DEAD_STATE:
            return -1
        else:
            if role == RED_ROLE:
                return self.r_image
            elif role == BLACK_ROLE:
                return self.b_image
            else:
                print('無法判斷红方/黑方')
                return -1

    def move(self, position, chess_board):
        """
        移動棋子到指定位置。
        """
        startSq = self.position
        endSq = position
        print(f"Attempting to move from {startSq} to {endSq}")
        
        # 創建 move 實例
        move_instance = move(startSq, endSq, chess_board)

    def eat(self, enemy_chess, position, chess_board,playerClicks, screen, operation_completed, is_chess_clicked):

        
        startSq = self.position
        endSq = position
            
            # 判定是否可以吃子
        if can_eat(self, enemy_chess, startSq, endSq, chess_board,):
            # 執行吃子邏輯
            chess_board[self.position[0]][self.position[1]] = None  # 清空原位置
            chess_board[position[0]][position[1]] = self  # 更新目標位置
            self.position = position  # 更新棋子位置
            self.rect.topleft = (
                board_margin + position[1] * grid_size + 11,
                board_margin + position[0] * grid_size + 11
            )
            enemy_chess.state = DEAD_STATE  # 將目標棋子設為死亡狀態
            print(f"{self.type} 成功吃掉 {enemy_chess.type}")
            draw_text(screen,f"{self.__class__.__name__} successfully eats {enemy_chess.__class__.__name__}",(0, 0, 0),150,500)
            #return True
        

            # 更新玩家狀態，只能操作當前棋子
            playerClicks[:] = [self.position]
            print("只能操作當前棋子，請選擇是否繼續操作或結束回合")

            # 顯示按鈕並處理選擇
            return handle_post_eat_action(screen, chess_board, playerClicks, operation_completed, is_chess_clicked)
        


        else:
            print(f"{self.type} 無法吃掉 {enemy_chess.type}")
            
            return False


class JiangChess(ChessPiece):
    def __init__(self, rect):
        super().__init__(
            rect,
            'dark_chess/images/red_shuai.png',
            'dark_chess/images/black_jiang.png',
            JIANG_TYPE,
            RED_ROLE
        )
class ShiChess(ChessPiece):
    def __init__(self, rect):
        super().__init__(
            rect,
            'dark_chess/images/red_shi.png',
            'dark_chess/images/black_shi.png',
            SHI_TYPE,
            RED_ROLE
        )
class XiangChess(ChessPiece):
    def __init__(self, rect):
        super().__init__(
            rect,
            'dark_chess/images/red_xiang.png',
            'dark_chess/images/black_xiang.png',
            XIANG_TYPE,
            RED_ROLE
        )
class MaChess(ChessPiece):
    def __init__(self, rect):
        super().__init__(
            rect,
            'dark_chess/images/red_ma.png',
            'dark_chess/images/black_ma.png',
            MA_TYPE,
            RED_ROLE
        )
class CheChess(ChessPiece):
    def __init__(self, rect):
        super().__init__(
            rect,
            'dark_chess/images/red_che.png',
            'dark_chess/images/black_che.png',
            CHE_TYPE,
            RED_ROLE
        )
class PaoChess(ChessPiece):
    def __init__(self, rect):
        super().__init__(
            rect,
            'dark_chess/images/red_pao.png',
            'dark_chess/images/black_pao.png',
            PAO_TYPE,
            RED_ROLE
        )
class ZuChess(ChessPiece):
    def __init__(self, rect):
        super().__init__(
            rect,
            'dark_chess/images/red_bing.png',
            'dark_chess/images/black_zu.png',
            ZU_TYPE,
            RED_ROLE
        )