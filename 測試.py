import pygame
import sys

# 初始化 Pygame
pygame.init()

# 設定螢幕和顏色
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Partial Scrollable Page")
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

# 固定區域高度
HEADER_HEIGHT = 100

# 可滾動區域的虛擬畫布
SCROLLABLE_WIDTH, SCROLLABLE_HEIGHT = SCREEN_WIDTH, 1200  # 比螢幕高的畫布
scrollable_surface = pygame.Surface((SCROLLABLE_WIDTH, SCROLLABLE_HEIGHT))
scrollable_surface.fill(WHITE)

# 在可滾動區域繪製內容
font = pygame.font.Font(None, 36)
for i in range(50):  # 繪製50行文字
    text = font.render(f"Scrollable Line {i + 1}", True, BLACK)
    scrollable_surface.blit(text, (50, 50 + i * 50))

# 滾動參數
scroll_y = 0
scroll_speed = 20

# 主循環
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:  # 滾輪滾動事件
            if event.button == 4:  # 滾輪向上
                scroll_y = max(scroll_y - scroll_speed, 0)
            elif event.button == 5:  # 滾輪向下
                scroll_y = min(scroll_y + scroll_speed, SCROLLABLE_HEIGHT - (SCREEN_HEIGHT - HEADER_HEIGHT))

    # 清屏
    screen.fill(GRAY)

    # 繪製可滾動區域
    screen.blit(scrollable_surface, (0, HEADER_HEIGHT - scroll_y))

    # 最後繪製固定區域，確保不被覆蓋
    pygame.draw.rect(screen, BLACK, (0, 0, SCREEN_WIDTH, HEADER_HEIGHT))  # 標題背景
    header_text = font.render("Fixed Header", True, WHITE)
    screen.blit(header_text, (SCREEN_WIDTH // 2 - 100, HEADER_HEIGHT // 2 - 20))

    # 更新畫面
    pygame.display.flip()

pygame.quit()
sys.exit()
