import pygame
import random
import os
os.chdir(os.path.dirname(__file__))
from enum import Enum
import time
import math

# 初始化 Pygame
pygame.init()

# 常數定義
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
CARD_WIDTH = 71
CARD_HEIGHT = 96
FPS = 30

# 顏色定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (173, 216, 230)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 153)  # 淡黃色，用於按鈕懸停效果

# 花色枚舉
class Suit(Enum):
    SPADE = "♠"
    HEART = "♥"
    DIAMOND = "♦"
    CLUB = "♣"
    
    def __lt__(self, other):
        return list(Suit).index(self) > list(Suit).index(other)

# 玩家方位枚舉
class Position(Enum):
    EAST = "East"
    SOUTH = "South"
    WEST = "West"
    NORTH = "North"

# 遊戲狀態枚舉
class GameState(Enum):
    MENU = 1
    DIFFICULTY = 2  # 新增難度選擇狀態
    BIDDING = 3
    PLAYING = 4
    END = 5

class Difficulty(Enum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"

class Card:
    def __init__(self, suit, number):
        self.suit = suit
        self.number = number
        self.rect = None

    def __str__(self):
        # 定義撲克牌符號
        suit_symbols = {
            Suit.SPADE: "♠",
            Suit.HEART: "♥",
            Suit.DIAMOND: "♦",
            Suit.CLUB: "♣"
        }
        # 定義牌面數字
        number_map = {11: 'J', 12: 'Q', 13: 'K', 14: 'A'}
        number_str = str(self.number) if self.number <= 10 else number_map[self.number]
        
        # 使用符號替代花色
        return f"{suit_symbols[self.suit]}{number_str}"


class Player:
    def __init__(self, position, is_ai=True, difficulty=Difficulty.MEDIUM):
        self.position = position
        self.is_ai = is_ai
        self.difficulty = difficulty
        self.cards = []
        self.tricks_won = 0
        self.experience = 0
    
    def add_card(self, card):
        self.cards.append(card)
        # 為人類玩家排序手牌
        if not self.is_ai:
            self.sort_cards()
    
    def sort_cards(self):
        # 按照花色和數字排序
        self.cards.sort(key=lambda card: (
            list(Suit).index(card.suit),
            -card.number  # 用負數使大的數字排前面
        ))

class BridgeGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("橋牌遊戲")

        self.background_image = pygame.image.load("橋牌背景.png")
        self.background_image = pygame.transform.scale(self.background_image, (WINDOW_WIDTH, WINDOW_HEIGHT))
        
        # 載入字體
        self.font = pygame.font.SysFont("segoeuisymbol", 24)
        self.large_font = pygame.font.Font("msjh.ttc", 24)
        # self.large_font = pygame.font.Font("msyh.ttc", 24)
        self.title_font = pygame.font.Font("Silkscreen-Bold.ttf", 56)  # 用於標題文字的字體
        self.buttom_font = pygame.font.Font("Silkscreen-Regular.ttf", 24) 
        
        # 遊戲狀態
        self.game_state = GameState.MENU
        
        # 創建開始按鈕
        self.start_button = pygame.Rect(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 - 25, 200, 50)
        
        # 添加難度相關變量
        self.difficulty = Difficulty.MEDIUM  # 在初始化玩家之前設置難度
        self.difficulty_buttons = {}
        
        # 初始化玩家
        self.initialize_players()
        
        # 遊戲相關變量
        self.trump_suit = None
        self.current_trick = []
        self.current_player = None
        self.leading_suit = None
        self.round_number = 0
        self.tricks_required = {"NS": 0, "EW": 0}
        self.tricks_won = {"NS": 0, "EW": 0}
        self.restart_button = None  # 初始化 restart_button
        
        # 叫牌相關變量
        self.current_bid = None
        self.pass_count = 0
        self.bid_winner = None
        self.first_bid_made = False
        self.bid_error_message = ""
        self.show_error = False
        self.error_start_time = None
        
        # 遊戲提示訊息
        self.game_message = ""
        self.message_color = BLACK
        self.message_time = None

        self.hint_button = pygame.Rect(60, WINDOW_HEIGHT - CARD_HEIGHT - 90, 100, 40)
        self.hint_message = ""  # 提示訊息
        self.hint_limit = 3  # 提示按鈕的使用次數限制
        self.hint_message_start_time = None
        
    def initialize_players(self):
        self.players = {
            Position.EAST: Player(Position.EAST, True, self.difficulty),
            Position.SOUTH: Player(Position.SOUTH, False),
            Position.WEST: Player(Position.WEST, True, self.difficulty),
            Position.NORTH: Player(Position.NORTH, True, self.difficulty)
        }
    
    def initialize_game(self):
        # 重置遊戲狀態
        self.round_number = 0
        self.tricks_won = {"NS": 0, "EW": 0}
        self.current_trick = []
        self.current_bid = None
        self.pass_count = 0
        self.bid_winner = None
        self.first_bid_made = False
        self.show_bid_options = False
        self.ai_bid_history = {pos: "" for pos in [Position.NORTH, Position.EAST, Position.WEST]}
        self.leading_suit = None
        self.trump_suit = None
        self.game_message = ""
        self.hint_message = ""
        self.hint_limit = 3  # 重置提示次數限制
        self.hint_message_start_time = None  # 重置提示訊息時間戳
        
        # 清空所有玩家手牌
        for player in self.players.values():
            player.cards = []
            player.tricks_won = 0
        
        # 創建並洗牌
        self.deck = []
        for suit in Suit:
            for number in range(2, 15):  # 2到14(Ace)
                self.deck.append(Card(suit, number))
        random.shuffle(self.deck)
        
        # 發牌並確保南家的牌有正確排序
        for i, card in enumerate(self.deck):
            position = list(Position)[i % 4]
            self.players[position].add_card(card)
        
        # 特別為南家排序
        self.players[Position.SOUTH].sort_cards()
        
        # 設置隨機初始玩家，而不是固定南家
        self.current_player = random.choice(list(Position))
        self.game_state = GameState.BIDDING

        # 如果第一個叫牌者是 AI，立即觸發 AI 叫牌
        if self.current_player != Position.SOUTH and self.game_state == GameState.BIDDING:
           self.ai_bid()

    def draw_difficulty_selection(self):
        self.screen.blit(self.background_image, (0, 0))  # 繪製背景
        
        # 繪製標題
        title_text = self.title_font.render("Choose AI Difficulty", True, BLACK)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//4 - 20))
        self.screen.blit(title_text, title_rect)
        
        # 繪製難度選擇按鈕
        button_width = 200
        button_height = 60
        spacing = 30
        start_y = WINDOW_HEIGHT//2 - ((button_height + spacing) * len(Difficulty))//2
        
        mouse_pos = pygame.mouse.get_pos()
        self.difficulty_buttons.clear()
        
        for i, difficulty in enumerate(Difficulty):
            button = pygame.Rect(
                WINDOW_WIDTH//2 - button_width//2,
                start_y + i * (button_height + spacing),
                button_width,
                button_height
            )
            
            # 檢查滑鼠懸停
            button_color = YELLOW if button.collidepoint(mouse_pos) else WHITE
            
            pygame.draw.rect(self.screen, button_color, button)
            pygame.draw.rect(self.screen, BLACK, button, 2)
            
            # 添加文字
            text = self.font.render(difficulty.value, True, BLACK)
            text_rect = text.get_rect(center=button.center)
            self.screen.blit(text, text_rect)
            
            self.difficulty_buttons[difficulty] = button
            
        # 添加難度說明
        descriptions = {
            Difficulty.EASY: "Suitable for beginners, AI will make relatively simple choices",
            Difficulty.MEDIUM: "Ideal for experienced players, AI will make reasonable strategic decisions",
            Difficulty.HARD: "Challenge level, AI will use advanced strategies and complex algorithms"

        }
        
        # 根據滑鼠位置顯示相應的難度說明
        for difficulty, button in self.difficulty_buttons.items():
            if button.collidepoint(mouse_pos):  # 偵測滑鼠是否在按鈕範圍內
                # 分割文字成多行
                lines = descriptions[difficulty].split(", ")
                
                # 計算起始垂直位置，讓多行文字整體垂直居中
                line_spacing = 30  # 行間距，將其設為更大的值
                start_y = WINDOW_HEIGHT * 3 // 4 - (len(lines) * line_spacing) // 2  # 更新高度計算
                
                # 渲染每行文字
                for i, line in enumerate(lines):
                    desc_text = self.buttom_font.render(line, True, BLACK)  # 渲染每行文字
                    desc_rect = desc_text.get_rect(center=(WINDOW_WIDTH // 2, start_y + i * line_spacing))  # 水平居中，垂直逐行排列
                    self.screen.blit(desc_text, desc_rect)  # 繪製文字到螢幕上
                break
    
    def handle_bid(self, bid_value=None):
        # 檢查是否是第一次叫牌且選擇 pass
        if not self.first_bid_made and (bid_value is None or bid_value == "pass"):
            self.bid_error_message = "The first player to bid must make a bid!"
            self.show_error = True
            self.error_start_time = time.time()
            return

        # 檢查叫牌是否比之前的大
        if bid_value and bid_value != "pass" and self.current_bid:
            current_num = int(self.current_bid.split()[0])
            current_suit = Suit(self.current_bid.split()[1])
            new_num = int(bid_value.split()[0])
            new_suit = Suit(bid_value.split()[1])
            
            if new_num < current_num or (new_num == current_num and new_suit < current_suit):
                self.bid_error_message = "The new bid must be higher than the current bid!"
                self.show_error = True
                self.error_start_time = time.time()
                return

        # 記錄電腦玩家的叫牌
        if self.current_player != Position.SOUTH:
            self.ai_bid_history[self.current_player] = "Pass" if bid_value == "pass" else bid_value

        if bid_value is None or bid_value == "pass":
            self.pass_count += 1
            if not self.first_bid_made:
                return  # 第一位玩家不能pass
        else:
            self.current_bid = bid_value
            self.bid_winner = self.current_player
            self.pass_count = 0
            if not self.first_bid_made:
                self.first_bid_made = True

        # 檢查叫牌是否結束
        if  self.pass_count == 3 and self.current_bid:
            self.game_state = GameState.PLAYING
            self.current_player = self.bid_winner
            bid_number = int(self.current_bid.split()[0])
            team = "NS" if self.bid_winner in [Position.NORTH, Position.SOUTH] else "EW"
            self.tricks_required[team] = 6 + bid_number
            self.tricks_required["NS" if team == "EW" else "EW"] = 14 - (6 + bid_number)
            self.trump_suit = Suit(self.current_bid.split()[1])
            
            # 設置遊戲訊息
            self.game_message = f"Bidding has ended, {self.bid_winner.value} won the bidding, the trump suit is {self.trump_suit.value}"
            print(self.game_message)

            # 確保如果贏家是 AI，他會立即出牌
            if self.players[self.current_player].is_ai:
                self.ai_play_card()
        else:
            # 移至下一個玩家
            current_idx = list(Position).index(self.current_player)
            self.current_player = list(Position)[(current_idx + 1) % 4]
            
            # 如果是AI玩家，觸發AI叫牌邏輯
            if self.players[self.current_player].is_ai:
                self.ai_bid()
    
    def ai_bid(self):
        player = self.players[self.current_player]
        
        # 計算手牌強度
        high_cards = len([card for card in player.cards if card.number >= 12])  # A,K,Q
        suit_lengths = {suit: len([c for c in player.cards if c.suit == suit]) for suit in Suit}
        longest_suit = max(suit_lengths.items(), key=lambda x: x[1])
        
        # 基礎叫牌條件
        if not self.first_bid_made:
            if high_cards >= 3 and longest_suit[1] >= 5:
                bid_number = min(3, high_cards - 1)
                bid_suit = longest_suit[0]
            elif high_cards >= 2 and longest_suit[1] >= 4:
                bid_number = 1
                bid_suit = longest_suit[0]
            else:
                bid_number = 1
                bid_suit = random.choice(list(Suit))
            bid_value = f"{bid_number} {bid_suit.value}"
            print(f"AI ({self.current_player.value}) 首叫：{bid_value} (高牌:{high_cards}, 最長花色:{longest_suit[0].value}:{longest_suit[1]})")
            self.handle_bid(bid_value)
            return

        # 後續叫牌策略
        if self.current_bid:
            current_bid_number = int(self.current_bid.split()[0])
            current_bid_suit = Suit(self.current_bid.split()[1])
            
            # 根據手牌強度決定是否要繼續叫牌
            partner_bid = self.ai_bid_history.get(list(Position)[(list(Position).index(self.current_player) + 2) % 4], "")
            partner_suit = partner_bid.split()[-1] if partner_bid and partner_bid != "Pass" else None
            
            if (high_cards >= 4 and longest_suit[1] >= 5) or \
            (partner_suit and suit_lengths[Suit(partner_suit)] >= 3 and high_cards >= 3):
                if current_bid_number < 4:
                    bid_number = current_bid_number + 1
                    bid_suit = longest_suit[0]
                    if partner_suit:
                        bid_suit = Suit(partner_suit)
                    bid_value = f"{bid_number} {bid_suit.value}"
                    self.handle_bid(bid_value)
                    return
        
        # 其他情況選擇 Pass
        print(f"AI ({self.current_player.value}) 選擇 Pass")
        self.handle_bid("pass")
    
    def handle_play_card(self, card_index):
        player = self.players[self.current_player]
        if card_index >= len(player.cards):
            return False
        
        card = player.cards[card_index]
        
        # 檢查是否符合出牌規則
        if self.leading_suit:
            has_same_suit = any(c.suit == self.leading_suit for c in player.cards)
            if has_same_suit and card.suit != self.leading_suit:
                self.game_message = f"You must play {self.leading_suit.value}~"
                self.message_color = RED
                self.message_time = time.time()
                return False
        
        # 移除並記錄打出的牌
        player.cards.pop(card_index)
        self.current_trick.append((self.current_player, card))
        
        # 如果是第一張牌，設置底牌花色
        if not self.leading_suit:
            self.leading_suit = card.suit
        
        print(f"{self.current_player.value}出牌：{card}")
        
        # 檢查這一輪是否結束
        if len(self.current_trick) == 4:
            # 在結束回合前增加延遲並強制更新顯示
            self.draw_playing()
            pygame.display.flip()
            pygame.time.wait(2500)  # 等待2.5秒
            self.end_trick()

            # 檢查是否達到獲勝條件
            if (self.tricks_won["NS"] >= self.tricks_required["NS"] or 
                self.tricks_won["EW"] >= self.tricks_required["EW"]):
                self.game_state = GameState.END
                self.calculate_experience()
                return True
            
        else:
            current_idx = list(Position).index(self.current_player)
            self.current_player = list(Position)[(current_idx + 1) % 4]
            
            if self.players[self.current_player].is_ai:
                self.next_ai_move_time = time.time() + 1.5

        return True
    
    def ai_play_card(self):
        player = self.players[self.current_player]
        if not player.cards:
            return

        # 根據不同難度採用不同的策略
        if player.difficulty == Difficulty.EASY:
            # 簡單模式：隨機選擇合法的牌
            valid_cards = self.get_valid_cards(player.cards)
            best_card_index = random.choice(valid_cards)
            
        elif player.difficulty == Difficulty.MEDIUM:
            # 中等模式：使用基本策略（原有的邏輯）
            best_card_index = self.medium_strategy()
            
        else:  # HARD
            # 困難模式：使用進階策略
            best_card_index = self.hard_strategy()
        
        self.handle_play_card(best_card_index)
    
    def get_valid_cards(self, cards):
        """獲取所有合法的出牌選擇"""
        if not self.leading_suit:
            return list(range(len(cards)))
        
        # 必須跟隨底牌花色
        valid_cards = [i for i, card in enumerate(cards) 
                      if card.suit == self.leading_suit]
        
        # 如果沒有底牌花色的牌，則所有牌都合法
        return valid_cards if valid_cards else list(range(len(cards)))
    
    def medium_strategy(self):
        """中等難度的出牌策略（原有的邏輯）"""
        player = self.players[self.current_player]
        valid_cards = self.get_valid_cards(player.cards)
        
        if not self.leading_suit:  # 首攻
            # 找出最長的花色
            suits = {suit: [] for suit in Suit}
            for i, card in enumerate(player.cards):
                suits[card.suit].append((i, card))
            
            longest_suit = max(suits.items(), key=lambda x: len(x[1]))[0]
            suit_cards = suits[longest_suit]
            
            return max(suit_cards, key=lambda x: x[1].number)[0] if suit_cards else valid_cards[0]
        else:
            # 跟牌策略
            winning_card = max(self.current_trick, 
                             key=lambda x: self.get_card_value(x[1]))[1]
            winning_value = self.get_card_value(winning_card)
            
            # 嘗試找出能贏的牌
            winning_cards = [i for i in valid_cards 
                           if self.get_card_value(player.cards[i]) > winning_value]
            
            return min(winning_cards, key=lambda i: player.cards[i].number) if winning_cards else \
                   min(valid_cards, key=lambda i: player.cards[i].number)
    
    def hard_strategy(self):
        """困難難度的進階策略"""
        player = self.players[self.current_player]
        valid_cards = self.get_valid_cards(player.cards)
        
        if not self.leading_suit:  # 首攻
            # 計算每種花色的權重
            suit_weights = {}
            for suit in Suit:
                suit_cards = [c for c in player.cards if c.suit == suit]
                # 考慮多個因素：
                # 1. 花色長度
                # 2. 高牌數量
                # 3. 是否為王牌
                weight = (
                    len(suit_cards) * 2 +  # 花色長度權重
                    len([c for c in suit_cards if c.number >= 11]) * 3 +  # 高牌權重
                    (5 if suit == self.trump_suit else 0)  # 王牌額外權重
                )
                suit_weights[suit] = weight
            
            # 選擇權重最高的花色中的最大牌
            best_suit = max(suit_weights.items(), key=lambda x: x[1])[0]
            suit_cards = [(i, card) for i, card in enumerate(player.cards) 
                         if card.suit == best_suit]
            
            if suit_cards:
                return max(suit_cards, key=lambda x: x[1].number)[0]
        else:
            # 計算當前贏家
            winning_card = max(self.current_trick, 
                             key=lambda x: self.get_card_value(x[1]))[1]
            winning_value = self.get_card_value(winning_card)
            winning_pos = self.current_trick[-1][0]
            
            # 判斷隊友是否在贏
            partner_pos = list(Position)[(list(Position).index(self.current_player) + 2) % 4]
            partner_winning = any(pos == partner_pos for pos, card in self.current_trick 
                                if self.get_card_value(card) == winning_value)
            
            if partner_winning:
                # 如果隊友在贏，出最小的牌
                return min(valid_cards, key=lambda i: player.cards[i].number)
            else:
                # 嘗試用最小的贏牌獲勝
                winning_cards = [i for i in valid_cards 
                               if self.get_card_value(player.cards[i]) > winning_value]
                if winning_cards:
                    return min(winning_cards, key=lambda i: player.cards[i].number)
        
        # 如果沒有特殊情況，使用默認策略
        return min(valid_cards, key=lambda i: player.cards[i].number) if valid_cards else None
    
    def get_card_value(self, card):
        # 基礎點數（2-14, Ace=14）
        base_value = card.number * 100  # 放大基礎點數確保花色差異不會超過點數差異
        
        # 花色優先級（王牌>底牌>其他）
        if card.suit == self.trump_suit:
            base_value += 10000  # 王牌最大
        elif card.suit == self.leading_suit:
            base_value += 5000   # 底牌次大
        
        print(f"計算牌值 {card}: {base_value} " + 
              f"(是否王牌:{card.suit == self.trump_suit}, " +
              f"是否底牌:{card.suit == self.leading_suit})")
        
        return base_value
    
    def show_effects(self):
        # 煙火特效參數
        firework_particles = []  # 儲存所有粒子
        num_particles = 100      # 增加粒子數量
        firework_center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)  # 煙火中心點

        # 初始化粒子
        for _ in range(num_particles):
            angle = random.uniform(0, 2 * math.pi)  # 隨機方向
            speed = random.uniform(4, 8)           # 更高的隨機速度，擴大範圍
            lifetime = random.uniform(30, 60)      # 粒子壽命（幀數）
            color = random.choice([(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)])  # 紅、綠、藍、黃
            particle = {
                "x": firework_center[0],
                "y": firework_center[1],
                "dx": math.cos(angle) * speed,
                "dy": math.sin(angle) * speed,
                "lifetime": lifetime,
                "color": color,
            }
            firework_particles.append(particle)

        # 動畫循環
        while firework_particles:
            self.screen.blit(self.background_image, (0, 0))  # 重繪背景
            self.draw_playing()  # 重繪當前遊戲狀態

            # 更新並繪製粒子
            for particle in firework_particles[:]:
                particle["x"] += particle["dx"]
                particle["y"] += particle["dy"]
                particle["lifetime"] -= 1

                # 當粒子壽命耗盡，從列表移除
                if particle["lifetime"] <= 0:
                    firework_particles.remove(particle)
                    continue

                # 繪製粒子（漸變效果）
                alpha = max(0, int(255 * (particle["lifetime"] / 60)))  # 隨壽命變化的透明度
                particle_surface = pygame.Surface((8, 8), pygame.SRCALPHA)  # 增大粒子尺寸
                pygame.draw.circle(particle_surface, (*particle["color"], alpha), (4, 4), 4)  # 粒子半徑增大
                self.screen.blit(particle_surface, (particle["x"], particle["y"]))

            pygame.display.flip()  # 更新畫面
            pygame.time.wait(20)  # 控制粒子運動速度

    
    def end_trick(self):
        # 判斷獲勝者
        winner_pos, winner_card = self.current_trick[0]
        winning_value = self.get_card_value(winner_card)

        for pos, card in self.current_trick[1:]:
            card_value = self.get_card_value(card)
            if card_value > winning_value:
                winner_pos = pos
                winner_card = card
                winning_value = card_value

        # 更新獲勝數據
        team = "NS" if winner_pos in [Position.NORTH, Position.SOUTH] else "EW"
        self.tricks_won[team] += 1

        # 設置遊戲訊息
        self.game_message = f"{winner_pos.value} Wins this trick"
        print(f"回合結束，獲勝者：{winner_pos.value}")

        # 如果南北方贏得回合，顯示特效
        if team == "NS":
            self.show_effects()

        # 清理本輪數據並設置下一輪開始者
        self.current_trick = []
        self.leading_suit = None
        self.current_player = winner_pos  # 下一輪由獲勝者開始

        self.round_number += 1
        if self.round_number >= 13:
            self.game_state = GameState.END
            self.calculate_experience()


    
    def calculate_experience(self):
        # 判斷勝利隊伍
        ns_won = self.tricks_won["NS"] >= self.tricks_required["NS"]
        ew_won = self.tricks_won["EW"] >= self.tricks_required["EW"]

        # 判斷玩家是否屬於南北方或東西方
        player_side = "NS" if Position.SOUTH == self.bid_winner or Position.NORTH == self.bid_winner else "EW"

        # 初始化經驗值
        exp = 0

        if ns_won:
            if player_side == "NS":
                exp = 1000  # 玩家屬於進攻方
            else:
                exp = 2000  # 玩家屬於防守方
            winner_text = "南北方"
        elif ew_won:
            exp = 500  # 玩家輸了
            winner_text = "東西方"
        else:
            exp = 0

        # 僅計算玩家的經驗值
        self.players[Position.SOUTH].experience += exp

        self.game_message = f"{winner_text}獲勝！"
        return exp


    def draw_menu(self):
        self.screen.blit(self.background_image, (0, 0))  # 繪製背景

        # 計算脈動效果的字體大小
        pulse_speed = 1  # 控制脈動速度，數值越小頻率越慢
        base_size = 56     # 標題的基礎大小
        pulse_scale = 10 * math.sin(pygame.time.get_ticks() * 0.003 * pulse_speed) + base_size
        title_font = pygame.font.Font("Silkscreen-Bold.ttf", int(pulse_scale))  # 動態字體大小

        # 繪製標題
        title_text = title_font.render("BRIDGE GAME", True, BLACK)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3))
        self.screen.blit(title_text, title_rect)

        # 繪製「開始」按鈕，添加懸停效果
        mouse_pos = pygame.mouse.get_pos()
        button_color = YELLOW if self.start_button.collidepoint(mouse_pos) else WHITE

        pygame.draw.rect(self.screen, button_color, self.start_button)
        pygame.draw.rect(self.screen, BLACK, self.start_button, 2)

        start_text = self.buttom_font.render("Start", True, BLACK)
        text_rect = start_text.get_rect(center=self.start_button.center)
        self.screen.blit(start_text, text_rect)

        # 繪製遊戲說明
        instructions = [
            "Game Instructions",
            "1. You will play as the South player.",
            "2. The game consists of 13 rounds.",
            "3. Click on the card to play it.",
            "4. Achieve the target number of winning tricks to win.",
            "5. The first bidder must make a bid and cannot pass.",
            "6. Subsequent bids must be higher than the previous one."
        ]

        for i, text in enumerate(instructions):
            instruction_text = self.buttom_font.render(text, True, BLACK)
            self.screen.blit(instruction_text, (WINDOW_WIDTH // 12, WINDOW_HEIGHT * 2 // 3 + i * 30))

    
    def draw_bidding(self):
        self.screen.blit(self.background_image, (0, 0))  # 繪製背景
        self.draw_player_cards()
                
        # 顯示當前叫牌狀態
        current_bid_text = f"Current Bid: {self.current_bid if self.current_bid else 'None'}"
        text = self.font.render(current_bid_text, True, BLACK)
        self.screen.blit(text, (20, 20))

        # 修改提示文字，使用當前玩家的方位
        if not self.first_bid_made:
            hint_text = self.buttom_font.render(f"{self.current_player.value} is the first bidder, you must make a bid", True, BLUE)
            hint_rect = hint_text.get_rect(center=(WINDOW_WIDTH//2, 100))
            self.screen.blit(hint_text, hint_rect)
        
        # 顯示錯誤訊息
        if self.show_error and self.bid_error_message:
            error_text = self.font.render(self.bid_error_message, True, RED)
            error_rect = error_text.get_rect(center=(WINDOW_WIDTH//2, 150))
            self.screen.blit(error_text, error_rect)
            
            if time.time() - self.error_start_time > 3:
                self.show_error = False
                self.bid_error_message = ""

        # 顯示電腦玩家的叫牌記錄
        ai_actions = {
            Position.NORTH: (WINDOW_WIDTH//2, 50),
            Position.EAST: (WINDOW_WIDTH - 150, WINDOW_HEIGHT//2),
            Position.WEST: (150, WINDOW_HEIGHT//2)
        }
        
        for pos, (x, y) in ai_actions.items():
            if hasattr(self, 'ai_bid_history') and pos in self.ai_bid_history:
                text = self.font.render(f"{pos.value}: {self.ai_bid_history[pos]}", True, BLACK)
                text_rect = text.get_rect(center=(x, y))
                self.screen.blit(text, text_rect)
            
        # 如果是玩家的回合，顯示叫牌按鈕
        if self.current_player == Position.SOUTH:
            self.draw_bidding_buttons()

    def draw_bidding_buttons(self):
        button_width = 100
        button_height = 40
        spacing = 20

        # 計算總寬度（兩個按鈕 + 間距）
        total_width = button_width * 2 + spacing
        start_x = (WINDOW_WIDTH - total_width) // 2 - 3  # 精確置中
        start_y = (WINDOW_HEIGHT // 2) + 50  # 所有按鈕下移 50 像素

        # 滑鼠位置
        mouse_pos = pygame.mouse.get_pos()

        # PASS 按鈕
        pass_button = pygame.Rect(start_x, start_y, button_width, button_height)
        button_color = YELLOW if pass_button.collidepoint(mouse_pos) else WHITE
        pygame.draw.rect(self.screen, button_color, pass_button)
        pygame.draw.rect(self.screen, BLACK, pass_button, 1)
        text = self.buttom_font.render("PASS", True, BLACK)
        text_rect = text.get_rect(center=pass_button.center)
        self.screen.blit(text, text_rect)

        # BID 按鈕
        bid_button = pygame.Rect(start_x + button_width + spacing, start_y, button_width, button_height)
        button_color = YELLOW if bid_button.collidepoint(mouse_pos) else WHITE
        pygame.draw.rect(self.screen, button_color, bid_button)
        pygame.draw.rect(self.screen, BLACK, bid_button, 1)
        text = self.buttom_font.render("BID", True, BLACK)
        text_rect = text.get_rect(center=bid_button.center)
        self.screen.blit(text, text_rect)

        self.bid_buttons = {"pass": pass_button, "bid": bid_button}

        # 如果選擇叫牌，顯示數字和花色選項
        if hasattr(self, "show_bid_options") and self.show_bid_options:
            # 數字選項下移
            num_y = start_y + button_height + spacing
            num_button_width = button_width // 2
            num_total_width = (num_button_width + 5) * 7
            num_start_x = (WINDOW_WIDTH - num_total_width) // 2

            self.number_buttons = []
            for i in range(7):
                num_button = pygame.Rect(num_start_x + i * (num_button_width + 5), num_y,
                                        num_button_width, button_height)
                button_color = YELLOW if num_button.collidepoint(mouse_pos) else WHITE
                pygame.draw.rect(self.screen, button_color, num_button)
                pygame.draw.rect(self.screen, BLACK, num_button, 1)
                text = self.font.render(str(i + 1), True, BLACK)
                text_rect = text.get_rect(center=num_button.center)
                self.screen.blit(text, text_rect)
                self.number_buttons.append((num_button, i + 1))

            # 花色選項下移
            suit_y = num_y + button_height + spacing
            suit_total_width = (button_width + 5) * len(Suit)
            suit_start_x = (WINDOW_WIDTH - suit_total_width) // 2

            self.suit_buttons = []
            for i, suit in enumerate(Suit):
                suit_button = pygame.Rect(suit_start_x + i * (button_width + 5), suit_y,
                                        button_width, button_height)
                button_color = YELLOW if suit_button.collidepoint(mouse_pos) else WHITE
                pygame.draw.rect(self.screen, button_color, suit_button)
                pygame.draw.rect(self.screen, BLACK, suit_button, 1)
                text = self.font.render(suit.value, True, BLACK)
                text_rect = text.get_rect(center=suit_button.center)
                self.screen.blit(text, text_rect)
                self.suit_buttons.append((suit_button, suit))


    
    def draw_playing(self):
        self.screen.blit(self.background_image, (0, 0))  # 繪製背景
        
        # 繪製遊戲狀態資訊
        self.draw_game_info()
        
        # 繪製玩家牌
        self.draw_all_players_cards()
        
        # 繪製當前回合的出牌
        self.draw_current_trick()
        
        # 顯示遊戲訊息
        if self.game_message:
            text = self.font.render(self.game_message, True, self.message_color)
            text_rect = text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 100))
            self.screen.blit(text, text_rect)
            
            # 3秒後清除訊息
            if self.message_time and time.time() - self.message_time > 3:
                self.game_message = ""
                self.message_time = None
        
        # 獲取鼠標位置
        mouse_pos = pygame.mouse.get_pos()

        # 檢查鼠標是否懸停在提示按鈕上
        button_color = YELLOW if self.hint_button.collidepoint(mouse_pos) else WHITE

        # 繪製提示按鈕
        pygame.draw.rect(self.screen, button_color, self.hint_button)
        pygame.draw.rect(self.screen, BLACK, self.hint_button, 2)
        hint_text = self.font.render("Hint", True, BLACK)
        text_rect = hint_text.get_rect(center=self.hint_button.center)
        self.screen.blit(hint_text, text_rect)


        # 繪製提示訊息
        if self.hint_message:
            # 計算是否超過3秒
            if self.hint_message_start_time and time.time() - self.hint_message_start_time > 3:
                self.hint_message = ""  # 清空提示訊息
                self.hint_message_start_time = None  # 重置時間戳
            else:
                # 繪製提示訊息
                hint_message_text = self.font.render(self.hint_message, True, BLACK)
                hint_message_rect = hint_message_text.get_rect(topleft=(self.hint_button.right + 20, self.hint_button.top + 4))
                self.screen.blit(hint_message_text, hint_message_rect)

    def draw_all_players_cards(self):
        # 卡牌尺寸和顏色設定
        CARD_BACK_COLOR = (200, 200, 200)  # 牌背的灰色
        LINE_COLOR = BLACK
        
        # 調整牌的尺寸
        SIDE_CARD_HEIGHT = CARD_HEIGHT * 1.5 * 1.5  # 加長東西家的牌高度
        NORTH_CARD_WIDTH = CARD_HEIGHT * 1.3 * 1.8  # 加寬北家的牌寬度
        NORTH_CARD_HEIGHT = CARD_WIDTH
        
        # 定義每個玩家牌的位置
        positions = {
            Position.NORTH: {
                'pos': (WINDOW_WIDTH//2 - NORTH_CARD_WIDTH//2, 70),
                'text_pos': (WINDOW_WIDTH//2, 30),
            },
            Position.EAST: {
                'pos': (WINDOW_WIDTH - 150 - 10, WINDOW_HEIGHT//2 - SIDE_CARD_HEIGHT//2),
                # 修改東家文字位置，往左移一點
                'text_pos': (WINDOW_WIDTH - 40 - 10, WINDOW_HEIGHT//2),
            },
            Position.WEST: {
                'pos': (80 + 10, WINDOW_HEIGHT//2 - SIDE_CARD_HEIGHT//2),
                # 修改西家文字位置，往右移一點
                'text_pos': (40 +10, WINDOW_HEIGHT//2),
            }
        }
        
        # 繪製AI玩家的牌（北、東、西家）
        for pos in [Position.NORTH, Position.EAST, Position.WEST]:
            player = self.players[pos]
            if len(player.cards) > 0:
                info = positions[pos]
                x, y = info['pos']
                
                if pos == Position.NORTH:
                    # 繪製北家的牌（寬矩形）
                    card_rect = pygame.Rect(x, y, NORTH_CARD_WIDTH, NORTH_CARD_HEIGHT)
                    pygame.draw.rect(self.screen, CARD_BACK_COLOR, card_rect)
                    pygame.draw.rect(self.screen, BLACK, card_rect, 1)
                    
                    # 垂直線條
                    num_lines = min(10, len(player.cards))  # 根據牌數調整線條
                    line_spacing = NORTH_CARD_WIDTH // (num_lines + 1)
                    for i in range(num_lines):
                        line_x = x + line_spacing * (i + 1)
                        pygame.draw.line(self.screen, LINE_COLOR,
                                       (line_x, y + 5),
                                       (line_x, y + NORTH_CARD_HEIGHT - 5))
                else:
                    # 東西家的牌（長矩形）
                    card_rect = pygame.Rect(x, y, CARD_WIDTH, SIDE_CARD_HEIGHT)
                    pygame.draw.rect(self.screen, CARD_BACK_COLOR, card_rect)
                    pygame.draw.rect(self.screen, BLACK, card_rect, 1)
                    
                    # 水平線條
                    num_lines = min(10, len(player.cards))
                    line_spacing = SIDE_CARD_HEIGHT // (num_lines + 1)
                    for i in range(num_lines):
                        line_y = y + line_spacing * (i + 1)
                        pygame.draw.line(self.screen, LINE_COLOR,
                                       (x + 5, line_y),
                                       (x + CARD_WIDTH - 5, line_y))
                
                # 繪製方位文字
                # 第一行：顯示方位名稱（West）
                text_position = self.font.render(pos.value, True, BLACK)
                text_position_rect = text_position.get_rect(center=(info['text_pos'][0], info['text_pos'][1] - 15))  # 往上移 10 像素
                self.screen.blit(text_position, text_position_rect)

                # 第二行：顯示卡片數量 (13)
                text_cards = self.font.render(f"({len(player.cards)})", True, BLACK)
                text_cards_rect = text_cards.get_rect(center=(info['text_pos'][0], info['text_pos'][1] + 15))  # 往下移 10 像素
                self.screen.blit(text_cards, text_cards_rect)
        
        # 繪製南家（玩家）的手牌
        self.draw_player_cards()
    
    def draw_player_cards(self):
        player = self.players[Position.SOUTH]
        if not player.cards or self.game_state not in [GameState.BIDDING, GameState.PLAYING]:
            return
            
        # 計算卡牌佈局
        total_width = len(player.cards) * CARD_WIDTH
        start_x = (WINDOW_WIDTH - total_width) // 2
        start_y = WINDOW_HEIGHT - CARD_HEIGHT - 20
        
        # 獲取滑鼠位置
        mouse_pos = pygame.mouse.get_pos()
        
        # 繪製每張牌
        for i, card in enumerate(player.cards):
            # 檢查滑鼠是否在卡牌上
            card_rect = pygame.Rect(start_x + i * CARD_WIDTH, start_y, CARD_WIDTH, CARD_HEIGHT)
            is_hover = card_rect.collidepoint(mouse_pos)
            
            # 如果滑鼠在卡牌上，位置往上移動10像素
            draw_y = start_y - 10 if is_hover else start_y
            card_rect = pygame.Rect(start_x + i * CARD_WIDTH, draw_y, CARD_WIDTH, CARD_HEIGHT)
            
            # 根據是否可以出這張牌決定顏色
            can_play = True
            if self.game_state == GameState.PLAYING and self.leading_suit:
                if card.suit != self.leading_suit and \
                   any(c.suit == self.leading_suit for c in player.cards):
                    can_play = False
            
            # 設置牌的顏色
            if not can_play:
                card_color = (200, 200, 200)  # 灰色表示不能出
            elif is_hover:
                card_color = YELLOW
            else:
                card_color = WHITE
            
            pygame.draw.rect(self.screen, card_color, card_rect)
            pygame.draw.rect(self.screen, BLACK, card_rect, 1)
            
            # 繪製牌面內容
            text_color = RED if card.suit in [Suit.HEART, Suit.DIAMOND] else BLACK
            text = self.font.render(str(card), True, text_color)
            text_rect = text.get_rect(center=card_rect.center)
            self.screen.blit(text, text_rect)
            
            # 儲存卡牌位置供點擊檢測
            card.rect = card_rect

    def draw_current_trick(self):
        if not self.current_trick:
            return
            
        # 定義四個位置
        positions = {
            Position.NORTH: (WINDOW_WIDTH//2, 200),
            Position.EAST: (WINDOW_WIDTH - 250, WINDOW_HEIGHT//2),
            Position.SOUTH: (WINDOW_WIDTH//2, WINDOW_HEIGHT - 250),
            Position.WEST: (250, WINDOW_HEIGHT//2)
        }
        
        # 繪製已打出的牌
        for pos, card in self.current_trick:
            x, y = positions[pos]
            card_rect = pygame.Rect(x - CARD_WIDTH//2, y - CARD_HEIGHT//2, 
                                  CARD_WIDTH, CARD_HEIGHT)
            pygame.draw.rect(self.screen, WHITE, card_rect)
            pygame.draw.rect(self.screen, BLACK, card_rect, 1)
            
            text_color = RED if card.suit in [Suit.HEART, Suit.DIAMOND] else BLACK
            text = self.font.render(str(card), True, text_color)
            text_rect = text.get_rect(center=card_rect.center)
            self.screen.blit(text, text_rect)
    
    def draw_game_info(self):  
        # 繪製王牌信息
        trump_text = f"Trump suit: {self.trump_suit.value}"
        text = self.font.render(trump_text, True, BLACK)  # 使用支援符號的字型
        self.screen.blit(text, (20, 20))
        
        # 繪製當前回合數
        round_text = f"Trick: {self.round_number + 1}/13"
        text = self.font.render(round_text, True, BLACK)
        self.screen.blit(text, (20, 50))
        
        # 合併 Our winning tricks 和數值
        ns_text = f"Our winning tricks: {self.tricks_won['NS']}/{self.tricks_required['NS']}"

        # 合併 Opponent's winning tricks 和數值
        ew_text = f"Opponent's winning tricks: {self.tricks_won['EW']}/{self.tricks_required['EW']}"

        # 渲染文字
        text_ns = self.font.render(ns_text, True, BLACK)
        text_ew = self.font.render(ew_text, True, BLACK)

        # 顯示文字（在同一行）
        self.screen.blit(text_ns, (20, 80))  # Our winning tricks
        self.screen.blit(text_ew, (20, 110))  # Opponent's winning tricks

        # 顯示當前玩家和底牌花色
        if self.game_state == GameState.PLAYING:
            current_player_text = f"Current player: {self.current_player.value}"
            text = self.font.render(current_player_text, True, BLACK)
            self.screen.blit(text, (20, 140))
            
            if self.leading_suit:
                leading_suit_text = f"Leading suit: {self.leading_suit.value}"
                text = self.font.render(leading_suit_text, True, BLACK)
                self.screen.blit(text, (20, 170))
    
    def draw_end(self):
        self.screen.blit(self.background_image, (0, 0))  # 繪製背景
        ticks = pygame.time.get_ticks() / 1000  # 獲取當前時間（秒）
        
        # 判斷南北方是否贏得遊戲
        ns_won = self.tricks_won["NS"] >= self.tricks_required["NS"]
        ew_won = self.tricks_won["EW"] >= self.tricks_required["EW"]

        # 顯示結果文字
        result_text = "YOU WIN " if ns_won else "OPPONENT WINS"
        result_color = (0, 0, 0) if ns_won else (255, 69, 0)  # 金色或柔和紅色

        # 文字閃爍效果
        if int(ticks * 2) % 2 == 0:  # 每0.5秒閃爍一次
            text = self.title_font.render(result_text, True, result_color)
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3))
            self.screen.blit(text, text_rect)

        # 顯示得分
        score_text = f"Our Score: {self.tricks_won['NS']}, Opponent's Score: {self.tricks_won['EW']}"
        text = self.buttom_font.render(score_text, True, BLACK)
        text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self.screen.blit(text, text_rect)

        # 顯示重新開始按鈕
        restart_button = pygame.Rect(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT * 2 // 3, 200, 50)
        mouse_pos = pygame.mouse.get_pos()
        button_color = (255, 255, 128) if restart_button.collidepoint(mouse_pos) else (230, 230, 230)  # 柔和的黃色和白色
        pygame.draw.rect(self.screen, button_color, restart_button)
        pygame.draw.rect(self.screen, BLACK, restart_button, 2)
        text = self.buttom_font.render("End Game", True, BLACK)
        text_rect = text.get_rect(center=restart_button.center)
        self.screen.blit(text, text_rect)

        self.restart_button = restart_button

        pygame.display.flip()

    
    def handle_click(self, pos):
        if self.game_state == GameState.MENU:
            if self.start_button.collidepoint(pos):
                print("進入難度選擇界面")
                self.game_state = GameState.DIFFICULTY
        
        elif self.game_state == GameState.DIFFICULTY:
            for difficulty, button in self.difficulty_buttons.items():
                if button.collidepoint(pos):
                    print(f"選擇難度: {difficulty.value}")
                    self.difficulty = difficulty
                    self.initialize_game()
                    break
        
        elif self.game_state == GameState.BIDDING:
            if self.current_player == Position.SOUTH:
                # 處理 Pass 和 叫牌按鈕
                if hasattr(self, "bid_buttons"):
                    if self.bid_buttons["pass"].collidepoint(pos):
                        print("玩家選擇了 Pass")
                        self.handle_bid("pass")
                    elif self.bid_buttons["bid"].collidepoint(pos):
                        print("玩家選擇了叫牌")
                        self.show_bid_options = True
                
                # 檢查是否已初始化叫牌選項按鈕
                if hasattr(self, "show_bid_options") and self.show_bid_options:
                    if hasattr(self, "number_buttons") and hasattr(self, "suit_buttons"):
                        # 檢查數字按鈕點擊
                        for button, number in self.number_buttons:
                            if button.collidepoint(pos):
                                print(f"玩家選擇叫牌數字：{number}")
                                self.selected_number = number
                                break
                        
                        # 檢查花色按鈕點擊
                        for button, suit in self.suit_buttons:
                            if button.collidepoint(pos):
                                if hasattr(self, "selected_number"):
                                    bid = f"{self.selected_number} {suit.value}"
                                    print(f"玩家叫牌完成：{bid}")
                                    self.handle_bid(bid)
                                    self.show_bid_options = False
                                    delattr(self, "selected_number")  # 清除選擇的數字
                                break

        elif self.game_state == GameState.PLAYING:
            if self.current_player == Position.SOUTH:
                # 檢查是否點擊了提示按鈕
                if self.hint_button.collidepoint(pos):
                    print("玩家點擊了提示按鈕")
                    if self.hint_limit > 0:
                        # 計算提示牌（基於困難模式策略）
                        best_card_index = self.hard_strategy()
                        if best_card_index is not None:
                            card = self.players[Position.SOUTH].cards[best_card_index]
                            # 將數字轉換為撲克牌符號
                            number_map = {11: 'J', 12: 'Q', 13: 'K', 14: 'A'}
                            number_str = number_map.get(card.number, str(card.number))  # 轉換數字
                            self.hint_message = f"{card.suit.value}{number_str}"
                        self.hint_limit -= 1  # 減少提示次數
                    else:
                        self.hint_message = "Hint has been used up"  # 提示次數已用完
                    # 記錄提示訊息的顯示時間
                    self.hint_message_start_time = time.time()
                    return
                
                # 檢查是否點擊了手牌
                player = self.players[Position.SOUTH]
                for i, card in enumerate(player.cards):
                    if card.rect and card.rect.collidepoint(pos):
                        print(f"玩家選擇出牌：{card}")
                        self.handle_play_card(i)
                        break

        if self.game_state == GameState.END:
            if self.restart_button and self.restart_button.collidepoint(pos):  # 確保 restart_button 存在
                print("玩家點擊了再玩一局")
                return "main_menu"

            
    def draw_pause_screen(self):
        self.screen.blit(self.background_image, (0, 0))  # 繪製背景
        pause_text = self.title_font.render("Game Paused", True, BLACK)
        resume_text = self.buttom_font.render("Press K to continue the game", True, BLACK)

        self.screen.blit(pause_text, (WINDOW_WIDTH // 2 - pause_text.get_width() // 2, WINDOW_HEIGHT // 3))
        self.screen.blit(resume_text, (WINDOW_WIDTH // 2 - resume_text.get_width() // 2, WINDOW_HEIGHT // 2))
        pygame.display.flip()

           
    def run(self):
        clock = pygame.time.Clock()
        running = True
        paused = False  # 暫停狀態
        self.next_ai_move_time = 0

        while running:
            current_time = time.time()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False  # 用戶關閉遊戲窗口
                    return 0, "quit"  # 返回 0 經驗值和 quit 狀態
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_k:  # 暫停或繼續
                        paused = not paused
                    elif event.key == pygame.K_f:  # 離開遊戲
                        return 0, "main_menu"  # 返回主菜單狀態
                    elif event.key == pygame.K_r:  # 重新開始遊戲
                        self.initialize_game()
                        paused = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if not paused:  # 只有在非暫停狀態下處理點擊事件
                        result = self.handle_click(event.pos)
                        if result == "main_menu":  # 玩家點擊了返回主選單
                            exp = self.calculate_experience()  # 計算經驗值
                            print(f"獲得經驗值: {exp}")
                            return exp, "main_menu"  # 返回經驗值和主菜單狀態

            # 如果遊戲處於暫停狀態，繪製暫停畫面
            if paused:
                self.draw_pause_screen()
            else:
                # 根據遊戲狀態繪製畫面
                if self.game_state == GameState.MENU:
                    self.draw_menu()
                elif self.game_state == GameState.DIFFICULTY:
                    self.draw_difficulty_selection()
                elif self.game_state == GameState.BIDDING:
                    self.draw_bidding()
                elif self.game_state == GameState.PLAYING:
                    # 處理 AI 出牌
                    if (
                        self.current_player != Position.SOUTH
                        and len(self.current_trick) < 4
                        and current_time >= self.next_ai_move_time
                    ):
                        self.ai_play_card()
                        self.next_ai_move_time = current_time + 1.0
                    self.draw_playing()
                elif self.game_state == GameState.END:
                    self.draw_end()

            pygame.display.flip()
            clock.tick(FPS)

        pygame.quit()
        return 0, "quit"  # 遊戲主循環退出時返回 quit 狀態


if __name__ == "__main__":
    game = BridgeGame()
    game.run()