import pygame
import sys
import random
import os
from pygame.locals import *

# 初始化pygame
pygame.init()
pygame.mixer.init()

# 获取资源路径（适配打包后的exe）
def resource_path(relative_path):
    """获取资源的绝对路径，兼容开发环境和打包后的exe"""
    try:
        # PyInstaller 创建临时文件夹，将路径存储在 _MEIPASS 中
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# 游戏窗口设置
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Whack-a-Mole Game')

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (139, 69, 19)
GREEN = (0, 128, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
LIGHT_BLUE = (100, 100, 255)
GRAY = (200, 200, 200)
YELLOW = (255, 255, 0)

# 游戏参数
FPS = 60
clock = pygame.time.Clock()
score = 0
game_time = 60
time_left = game_time

# 图片尺寸
MOLE_SIZE = 150
HOLE_SIZE_WIDTH = 180
HOLE_SIZE_HEIGHT = 120
HAMMER_SIZE = 120

# 地鼠洞的位置
holes = [
    (300, 200), (600, 200), (900, 200), (1200, 200),
    (300, 400), (600, 400), (900, 400), (1200, 400),
    (300, 600), (600, 600), (900, 600), (1200, 600),
    (300, 800), (600, 800), (900, 800), (1200, 800)
]

# 字体设置
def get_font(size, bold=False):
    chinese_fonts = ['simhei', 'microsoft yahei', 'stkaiti', 'stzhongsong', 'arialuni']
    english_fonts = ['arial', 'freesans', 'dejavusans']
    
    for font_name in chinese_fonts:
        try:
            return pygame.font.SysFont(font_name, size, bold=bold)
        except:
            continue
    
    for font_name in english_fonts:
        try:
            return pygame.font.SysFont(font_name, size, bold=bold)
        except:
            continue
    
    return pygame.font.Font(None, size)

# ==================== 语言文本 ====================

class Texts:
    def __init__(self, language='en'):
        self.language = language
        self.update_texts()
    
    def update_texts(self):
        if self.language == 'zh':
            self.language_select = "选择语言"
            self.english = "English"
            self.chinese = "中文"
            self.title = "打地鼠游戏"
            self.select_mode = "选择游戏模式"
            self.free_mode = "自由模式"
            self.time_mode = "计时模式"
            self.quit_game = "退出游戏"
            self.free_desc = "自由模式：无时间限制，随意游玩"
            self.time_desc = "计时模式：60秒挑战，获得最高分"
            self.game_over = "游戏结束!"
            self.final_score = "最终得分:"
            self.total_hits = "总击中数:"
            self.restart_text = "按 R 返回主菜单，按 ESC 退出"
            self.score_label = "得分:"
            self.time_label = "时间:"
            self.free_mode_hint = "自由模式 - 按 ESC 返回菜单"
        else:
            self.language_select = "Select Language"
            self.english = "English"
            self.chinese = "中文"
            self.title = "Whack-a-Mole Game"
            self.select_mode = "Select Game Mode"
            self.free_mode = "Free Mode"
            self.time_mode = "Time Mode"
            self.quit_game = "Quit Game"
            self.free_desc = "Free Mode: No time limit, play as long as you want"
            self.time_desc = "Time Mode: 60 seconds challenge, get the highest score"
            self.game_over = "Game Over!"
            self.final_score = "Final Score:"
            self.total_hits = "Total Hits:"
            self.restart_text = "Press R to return to Menu, ESC to Quit"
            self.score_label = "Score:"
            self.time_label = "Time:"
            self.free_mode_hint = "Free Mode - Press ESC for Menu"

texts = Texts('en')

# ==================== 按钮类 ====================

class Button:
    def __init__(self, x, y, width, height, text, color=LIGHT_BLUE, hover_color=BLUE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        
    def draw(self, surface):
        pygame.draw.rect(surface, self.current_color, self.rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=10)
        font = get_font(32)
        text_surface = font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
    def check_hover(self, pos):
        self.current_color = self.hover_color if self.rect.collidepoint(pos) else self.color
        
    def is_clicked(self, pos, click):
        return self.rect.collidepoint(pos) and click

# ==================== 锤子类 ====================

class Hammer:
    def __init__(self, hammer_img, hammer_down_img):
        self.normal_image = hammer_img
        self.down_image = hammer_down_img
        self.current_image = hammer_img
        self.position = (0, 0)
        self.is_swinging = False
        self.swing_start_time = 0
        self.swing_duration = 120
        
    def update_position(self, pos):
        self.position = pos
    
    def swing(self):
        if not self.is_swinging:
            self.is_swinging = True
            self.swing_start_time = pygame.time.get_ticks()
            self.current_image = self.down_image
    
    def update(self):
        if self.is_swinging:
            if pygame.time.get_ticks() - self.swing_start_time > self.swing_duration:
                self.is_swinging = False
                self.current_image = self.normal_image
    
    def draw(self, surface):
        if self.is_swinging:
            elapsed = pygame.time.get_ticks() - self.swing_start_time
            if elapsed < self.swing_duration:
                if elapsed < self.swing_duration / 3:
                    scale = 1 + (elapsed / (self.swing_duration / 3)) * 0.3
                else:
                    scale = 1.3 - ((elapsed - self.swing_duration / 3) / (self.swing_duration * 2 / 3)) * 0.3
                
                scaled_img = pygame.transform.scale(
                    self.current_image, 
                    (int(HAMMER_SIZE * scale), int(HAMMER_SIZE * scale))
                )
                rect = scaled_img.get_rect(center=self.position)
                surface.blit(scaled_img, rect)
                return
        
        rect = self.current_image.get_rect(center=self.position)
        surface.blit(self.current_image, rect)

# ==================== 地鼠类 ====================

class Mole:
    def __init__(self, hole_pos):
        self.hole_pos = hole_pos
        self.is_visible = False
        self.is_hit = False
        self.visible_time = 0
        self.hit_time = 0
        self.max_visible_time = 1500
        self.hit_display_time = 300
        
    def show(self):
        self.is_visible = True
        self.is_hit = False
        self.visible_time = pygame.time.get_ticks()
        
    def hide(self):
        self.is_visible = False
        self.is_hit = False
        
    def hit(self):
        if self.is_visible and not self.is_hit:
            self.is_hit = True
            self.hit_time = pygame.time.get_ticks()
            return True
        return False
            
    def update(self):
        now = pygame.time.get_ticks()
        if self.is_hit:
            if now - self.hit_time > self.hit_display_time:
                self.hide()
        elif self.is_visible:
            if now - self.visible_time > self.max_visible_time:
                self.hide()
                
    def draw(self, surface, normal_img, hit_img, hole_img):
        hole_rect = hole_img.get_rect(center=self.hole_pos)
        surface.blit(hole_img, hole_rect)
        if self.is_visible:
            img = hit_img if self.is_hit else normal_img
            if self.is_hit:
                now = pygame.time.get_ticks()
                elapsed = now - self.hit_time
                if elapsed < 100:
                    scale = 1 - (elapsed / 100) * 0.3
                    scaled_img = pygame.transform.scale(img, (int(MOLE_SIZE * scale), int(MOLE_SIZE * scale)))
                    rect = scaled_img.get_rect(center=self.hole_pos)
                    surface.blit(scaled_img, rect)
                    return
            
            rect = img.get_rect(center=self.hole_pos)
            surface.blit(img, rect)
            
    def check_hit(self, pos):
        if not self.is_visible or self.is_hit:
            return False
        dx = pos[0] - self.hole_pos[0]
        dy = pos[1] - self.hole_pos[1]
        return (dx*dx + dy*dy) ** 0.5 < MOLE_SIZE//2

# ==================== 默认图形（当图片不存在时使用） ====================

def create_default_mole():
    surf = pygame.Surface((MOLE_SIZE, MOLE_SIZE), pygame.SRCALPHA)
    pygame.draw.circle(surf, (150, 75, 0), (MOLE_SIZE//2, MOLE_SIZE//2), MOLE_SIZE//2 - 5)
    pygame.draw.circle(surf, (200, 150, 100), (MOLE_SIZE//2, MOLE_SIZE//3), MOLE_SIZE//5)
    pygame.draw.circle(surf, BLACK, (MOLE_SIZE//2 - 10, MOLE_SIZE//3 - 5), 8)
    pygame.draw.circle(surf, BLACK, (MOLE_SIZE//2 + 10, MOLE_SIZE//3 - 5), 8)
    pygame.draw.ellipse(surf, (200, 0, 0), (MOLE_SIZE//2 - 25, MOLE_SIZE//2 - 10, 50, 20))
    return surf

def create_default_hit_mole():
    surf = pygame.Surface((MOLE_SIZE, MOLE_SIZE), pygame.SRCALPHA)
    pygame.draw.circle(surf, (200, 0, 0), (MOLE_SIZE//2, MOLE_SIZE//2), MOLE_SIZE//2 - 5)
    pygame.draw.circle(surf, (255, 200, 200), (MOLE_SIZE//2, MOLE_SIZE//3), MOLE_SIZE//5)
    pygame.draw.circle(surf, BLACK, (MOLE_SIZE//2 - 10, MOLE_SIZE//3 - 5), 8)
    pygame.draw.circle(surf, BLACK, (MOLE_SIZE//2 + 10, MOLE_SIZE//3 - 5), 8)
    pygame.draw.ellipse(surf, (100, 0, 0), (MOLE_SIZE//2 - 25, MOLE_SIZE//2 - 10, 50, 20))
    pygame.draw.line(surf, WHITE, (MOLE_SIZE//3, MOLE_SIZE//3), (2*MOLE_SIZE//3, 2*MOLE_SIZE//3), 5)
    pygame.draw.line(surf, WHITE, (2*MOLE_SIZE//3, MOLE_SIZE//3), (MOLE_SIZE//3, 2*MOLE_SIZE//3), 5)
    return surf

def create_default_hole():
    surf = pygame.Surface((HOLE_SIZE_WIDTH, HOLE_SIZE_HEIGHT), pygame.SRCALPHA)
    pygame.draw.ellipse(surf, BROWN, (0, 0, HOLE_SIZE_WIDTH, HOLE_SIZE_HEIGHT))
    pygame.draw.ellipse(surf, BLACK, (10, 10, HOLE_SIZE_WIDTH-20, HOLE_SIZE_HEIGHT-20))
    return surf

def create_default_hammer():
    normal = pygame.Surface((HAMMER_SIZE, HAMMER_SIZE), pygame.SRCALPHA)
    pygame.draw.rect(normal, (150, 75, 0), (HAMMER_SIZE//2 - 8, 15, 16, HAMMER_SIZE//2))
    pygame.draw.rect(normal, (100, 100, 100), (HAMMER_SIZE//4, 10, HAMMER_SIZE//2, 25))
    pygame.draw.rect(normal, (150, 150, 150), (HAMMER_SIZE//4 + 5, 10, HAMMER_SIZE//2 - 10, 8))
    down = normal.copy()
    down = pygame.transform.rotate(down, 45)
    return normal, down

def create_default_background():
    surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    surf.fill(GREEN)
    for i in range(0, WINDOW_WIDTH, 30):
        for j in range(0, WINDOW_HEIGHT, 30):
            pygame.draw.line(surf, (0, 100, 0), (i, j), (i, j+15), 3)
    return surf

# ==================== 加载资源 ====================

def load_resources():
    resources = {}
    folder = 'mm'
    
    # 尝试从 mm 文件夹加载
    try:
        img = pygame.image.load(resource_path(os.path.join(folder, 'mole_normal.png'))).convert_alpha()
        resources['mole_normal'] = pygame.transform.scale(img, (MOLE_SIZE, MOLE_SIZE))
    except:
        resources['mole_normal'] = create_default_mole()
    
    try:
        img = pygame.image.load(resource_path(os.path.join(folder, 'mole_hit.png'))).convert_alpha()
        resources['mole_hit'] = pygame.transform.scale(img, (MOLE_SIZE, MOLE_SIZE))
    except:
        resources['mole_hit'] = create_default_hit_mole()
    
    try:
        img = pygame.image.load(resource_path(os.path.join(folder, 'hole.png'))).convert_alpha()
        resources['hole'] = pygame.transform.scale(img, (HOLE_SIZE_WIDTH, HOLE_SIZE_HEIGHT))
    except:
        resources['hole'] = create_default_hole()
    
    try:
        img = pygame.image.load(resource_path(os.path.join(folder, 'hammer.png'))).convert_alpha()
        resources['hammer'] = pygame.transform.scale(img, (HAMMER_SIZE, HAMMER_SIZE))
        resources['hammer_down'] = pygame.transform.rotate(resources['hammer'], 45)
    except:
        resources['hammer'], resources['hammer_down'] = create_default_hammer()
    
    try:
        img = pygame.image.load(resource_path(os.path.join(folder, 'background.jpg'))).convert()
        resources['background'] = pygame.transform.scale(img, (WINDOW_WIDTH, WINDOW_HEIGHT))
    except:
        resources['background'] = create_default_background()
    
    try:
        resources['hit_sound'] = pygame.mixer.Sound(resource_path(os.path.join(folder, 'hit.wav')))
    except:
        resources['hit_sound'] = None
    
    try:
        pygame.mixer.music.load(resource_path(os.path.join(folder, 'background_music.mp3')))
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
    except:
        pass
    
    return resources

# ==================== 界面函数 ====================

def show_language_selection():
    global texts
    
    en_btn = Button(WINDOW_WIDTH//2 - 220, 400, 200, 80, "English")
    zh_btn = Button(WINDOW_WIDTH//2 + 20, 400, 200, 80, "中文")
    
    while True:
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = False
        
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                mouse_click = True
        
        en_btn.check_hover(mouse_pos)
        zh_btn.check_hover(mouse_pos)
        
        if en_btn.is_clicked(mouse_pos, mouse_click):
            texts.language = 'en'
            texts.update_texts()
            return
        elif zh_btn.is_clicked(mouse_pos, mouse_click):
            texts.language = 'zh'
            texts.update_texts()
            return
        
        window.fill(GREEN)
        title_font = get_font(72, True)
        title = title_font.render(texts.language_select, True, WHITE)
        window.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 250))
        en_btn.draw(window)
        zh_btn.draw(window)
        pygame.display.update()
        clock.tick(FPS)

def show_mode_selection():
    btn_w = 400
    btn_h = 80
    free_btn = Button(WINDOW_WIDTH//2 - btn_w//2, 400, btn_w, btn_h, texts.free_mode)
    time_btn = Button(WINDOW_WIDTH//2 - btn_w//2, 550, btn_w, btn_h, texts.time_mode)
    quit_btn = Button(WINDOW_WIDTH//2 - btn_w//2, 700, btn_w, btn_h, texts.quit_game, RED)
    
    while True:
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = False
        
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                mouse_click = True
        
        free_btn.check_hover(mouse_pos)
        time_btn.check_hover(mouse_pos)
        quit_btn.check_hover(mouse_pos)
        
        if free_btn.is_clicked(mouse_pos, mouse_click):
            return "free"
        elif time_btn.is_clicked(mouse_pos, mouse_click):
            return "time"
        elif quit_btn.is_clicked(mouse_pos, mouse_click):
            return "quit"
        
        window.fill(GREEN)
        title_font = get_font(72, True)
        title = title_font.render(texts.title, True, WHITE)
        subtitle = get_font(48).render(texts.select_mode, True, WHITE)
        window.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 200))
        window.blit(subtitle, (WINDOW_WIDTH//2 - subtitle.get_width()//2, 300))
        
        free_btn.draw(window)
        time_btn.draw(window)
        quit_btn.draw(window)
        
        desc_font = get_font(36)
        free_desc = desc_font.render(texts.free_desc, True, WHITE)
        time_desc = desc_font.render(texts.time_desc, True, WHITE)
        window.blit(free_desc, (WINDOW_WIDTH//2 - free_desc.get_width()//2, 500))
        window.blit(time_desc, (WINDOW_WIDTH//2 - time_desc.get_width()//2, 650))
        
        pygame.display.update()
        clock.tick(FPS)

def show_game_over(mode, final_score):
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    window.blit(overlay, (0, 0))
    
    title_font = get_font(72, True)
    game_over = title_font.render(texts.game_over, True, WHITE)
    
    score_font = get_font(48)
    if mode == "time":
        score_text = score_font.render(f"{texts.final_score} {final_score}", True, WHITE)
    else:
        score_text = score_font.render(f"{texts.total_hits} {final_score}", True, WHITE)
    
    restart_text = get_font(36).render(texts.restart_text, True, WHITE)
    
    window.blit(game_over, (WINDOW_WIDTH//2 - game_over.get_width()//2, 300))
    window.blit(score_text, (WINDOW_WIDTH//2 - score_text.get_width()//2, 450))
    window.blit(restart_text, (WINDOW_WIDTH//2 - restart_text.get_width()//2, 550))
    pygame.display.update()
    
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_r:
                    return "menu"
                elif event.key == K_ESCAPE:
                    return "quit"
        clock.tick(FPS)

def game_loop(mode):
    global score, time_left
    
    res = load_resources()
    moles = [Mole(h) for h in holes]
    hammer = Hammer(res['hammer'], res['hammer_down'])
    last_mole = pygame.time.get_ticks()
    start_time = pygame.time.get_ticks()
    
    pygame.mouse.set_visible(False)
    game_active = True
    
    while True:
        now = pygame.time.get_ticks()
        
        if game_active and mode == "time":
            time_left = game_time - (now - start_time) // 1000
            if time_left <= 0:
                game_active = False
        
        pos = pygame.mouse.get_pos()
        hammer.update_position(pos)
        
        for event in pygame.event.get():
            if event.type == QUIT:
                return "quit"
            elif event.type == MOUSEBUTTONDOWN and event.button == 1 and game_active:
                hammer.swing()
                for m in moles:
                    if m.check_hit(event.pos) and m.hit():
                        score += 1
                        if res['hit_sound']:
                            res['hit_sound'].play()
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.mouse.set_visible(True)
                return "menu"
        
        if game_active:
            if now - last_mole > 800:
                last_mole = now
                available = [m for m in moles if not m.is_visible]
                for _ in range(min(random.randint(1, 4), len(available))):
                    m = random.choice(available)
                    m.show()
                    available.remove(m)
            for m in moles:
                m.update()
        
        hammer.update()
        window.blit(res['background'], (0, 0))
        for m in moles:
            m.draw(window, res['mole_normal'], res['mole_hit'], res['hole'])
        hammer.draw(window)
        
        score_font = get_font(48)
        window.blit(score_font.render(f"{texts.score_label} {score}", True, WHITE), (50, 50))
        
        if mode == "time":
            window.blit(score_font.render(f"{texts.time_label} {time_left}s", True, WHITE), (WINDOW_WIDTH - 300, 50))
        else:
            window.blit(get_font(36).render(texts.free_mode_hint, True, WHITE), (WINDOW_WIDTH - 550, 50))
        
        if not game_active and mode == "time":
            pygame.mouse.set_visible(True)
            return show_game_over(mode, score)
        
        pygame.display.update()
        clock.tick(FPS)

# ==================== 主程序 ====================

def main():
    global score, time_left
    
    show_language_selection()
    
    while True:
        mode = show_mode_selection()
        if mode == "quit":
            break
        score = 0
        time_left = game_time
        if game_loop(mode) == "quit":
            break
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()