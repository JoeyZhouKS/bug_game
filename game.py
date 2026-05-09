import tkinter as tk
import math
import random
import time

class SimpleGame:
    def __init__(self, root):
        self.root = root
        self.root.title("勇者传说 - Legend of the Brave")
        self.root.geometry("1024x600")
        
        self.canvas = tk.Canvas(root, width=1024, height=600, bg='#1a1a2e')
        self.canvas.pack()
        
        self.state = 'menu'
        self.player = {'x': 100, 'y': 400, 'vx': 0, 'vy': 0, 'health': 100, 'score': 0, 'invincible_timer': 0}
        self.keys = {}
        self.prev_keys = {}
        self.on_ground = False
        self.stars = []
        self.attack_timer = 0
        self.attack_effect = None
        
        self.setup_events()
        self.generate_stars()
        self.draw_menu()
        
    def setup_events(self):
        self.root.bind('<Key>', self.on_key_press)
        self.root.bind('<KeyRelease>', self.on_key_release)
        self.root.bind('<Button-1>', self.on_click)

    def on_key_press(self, event):
        self.keys[event.keysym] = True
        
    def on_key_release(self, event):
        self.keys[event.keysym] = False
        
    def on_click(self, event):
        if self.state == 'menu':
            if 362 <= event.x <= 662 and 400 <= event.y <= 460:
                self.start_game()
                
    def generate_stars(self):
        self.stars = []
        for _ in range(50):
            self.stars.append({
                'x': random.randint(0, 1024),
                'y': random.randint(0, 300),
                'size': random.randint(1, 3),
                'twinkle': random.random()
            })
        
    def draw_menu(self):
        self.canvas.delete('all')
        self.canvas.create_rectangle(0, 0, 1024, 600, fill='#1a1a2e')
        
        # 标题
        self.canvas.create_text(512, 200, text="勇者传说", fill='#ffd700', 
                               font=("Microsoft YaHei", 48, "bold"))
        self.canvas.create_text(512, 270, text="Legend of the Brave", fill='#a0a0a0', 
                               font=("Arial", 20))
        
        # 按钮
        self.canvas.create_rectangle(362, 400, 662, 460, fill='#4a90e2')
        self.canvas.create_text(512, 430, text="开始游戏", fill='white', 
                               font=("Microsoft YaHei", 20))
        
        # 说明
        self.canvas.create_text(512, 520, text="方向键移动 | 空格跳跃 | Z攻击", 
                               fill='#888888', font=("Microsoft YaHei", 14))
        
    def start_game(self):
        self.state = 'playing'
        self.player = {'x': 100, 'y': 400, 'vx': 0, 'vy': 0, 'health': 100, 'score': 0, 'invincible_timer': 0}
        self.keys = {}
        self.prev_keys = {}
        self.on_ground = False
        self.attack_timer = 0
        self.attack_effect = None
        self.coins = [
            {'x': 300, 'y': 320, 'collected': False}, 
            {'x': 500, 'y': 250, 'collected': False}, 
            {'x': 700, 'y': 350, 'collected': False},
            {'x': 850, 'y': 200, 'collected': False},
            {'x': 150, 'y': 250, 'collected': False}
        ]
        self.platforms = [
            {'x': 0, 'y': 500, 'w': 1024, 'h': 100},
            {'x': 200, 'y': 350, 'w': 150, 'h': 20},
            {'x': 450, 'y': 280, 'w': 150, 'h': 20},
            {'x': 700, 'y': 380, 'w': 150, 'h': 20},
            {'x': 100, 'y': 280, 'w': 100, 'h': 20},
            {'x': 850, 'y': 230, 'w': 120, 'h': 20},
        ]
        self.enemies = [
            {'x': 600, 'y': 440, 'vx': 2, 'health': 3, 'active': True},
            {'x': 400, 'y': 440, 'vx': -1.5, 'health': 3, 'active': True}
        ]
        self.game_loop()
        
    def game_loop(self):
        if self.state != 'playing':
            return
            
        self.update()
        self.render()
        self.prev_keys = self.keys.copy()
        self.root.after(16, self.game_loop)
        
    def update(self):
        if self.player['invincible_timer'] > 0:
            self.player['invincible_timer'] -= 1

        if 'Left' in self.keys or 'a' in self.keys:
            self.player['vx'] = -5
        elif 'Right' in self.keys or 'd' in self.keys:
            self.player['vx'] = 5
        else:
            self.player['vx'] = 0

        if 'space' in self.keys and not self.prev_keys.get('space') and self.on_ground:
            self.player['vy'] = -15
            self.on_ground = False

        if 'z' in self.keys and not self.prev_keys.get('z') and self.attack_timer <= 0:
            self.attack_timer = 15
            self.check_attack_hit()

        if self.attack_timer > 0:
            self.attack_timer -= 1

        self.player['vy'] += 0.8
        self.player['x'] += self.player['vx']
        self.player['y'] += self.player['vy']

        player_w = 40
        player_h = 40

        self.on_ground = False
        for platform in self.platforms:
            if (self.player['x'] < platform['x'] + platform['w'] and
                self.player['x'] + player_w > platform['x'] and
                self.player['y'] < platform['y'] + platform['h'] and
                self.player['y'] + player_h > platform['y']):
                if self.player['vy'] > 0 and self.player['y'] + player_h - self.player['vy'] <= platform['y']:
                    self.player['y'] = platform['y'] - player_h
                    self.player['vy'] = 0
                    self.on_ground = True

        for platform in self.platforms:
            if (self.player['x'] < platform['x'] + platform['w'] and
                self.player['x'] + player_w > platform['x'] and
                self.player['y'] < platform['y'] + platform['h'] and
                self.player['y'] + player_h > platform['y']):
                left_dist = (self.player['x'] + player_w) - platform['x']
                right_dist = (platform['x'] + platform['w']) - self.player['x']
                if left_dist < right_dist:
                    self.player['x'] = platform['x'] - player_w
                else:
                    self.player['x'] = platform['x'] + platform['w']

        self.player['x'] = max(0, min(self.player['x'], 1024 - player_w))
        if self.player['y'] > 600:
            self.player['y'] = 400
            self.player['health'] -= 20
            self.player['vy'] = 0
            self.player['invincible_timer'] = 30

        for coin in self.coins:
            if not coin['collected']:
                if (abs(self.player['x'] + player_w / 2 - coin['x']) < 25 and
                    abs(self.player['y'] + player_h / 2 - coin['y']) < 25):
                    coin['collected'] = True
                    self.player['score'] += 100

        for enemy in self.enemies:
            if not enemy['active']:
                continue
            enemy['x'] += enemy['vx']
            if enemy['x'] <= 50 or enemy['x'] >= 974:
                enemy['vx'] *= -1

            enemy_top = enemy['y'] - 20
            enemy_bottom = enemy['y'] + 20
            if (abs(self.player['x'] + player_w / 2 - enemy['x']) < 30 and
                abs(self.player['y'] + player_h / 2 - enemy['y']) < 40):
                if self.player['vy'] > 0 and self.player['y'] + player_h - self.player['vy'] <= enemy_top:
                    enemy['health'] -= 1
                    self.player['vy'] = -10
                    self.player['score'] += 200
                    if enemy['health'] <= 0:
                        enemy['active'] = False
                else:
                    if self.player['invincible_timer'] <= 0:
                        self.player['health'] -= 1
                        self.player['invincible_timer'] = 30

        if self.player['health'] <= 0:
            self.state = 'gameover'
            self.draw_gameover()
            return

        all_coins = all(c['collected'] for c in self.coins)
        all_dead = all(not e['active'] for e in self.enemies)
        if all_coins and all_dead:
            self.state = 'win'
            self.draw_win()
            
    def check_attack_hit(self):
        attack_x = self.player['x'] + 50 if self.player['vx'] >= 0 else self.player['x'] - 30
        attack_y = self.player['y'] + 20

        for enemy in self.enemies:
            if not enemy['active']:
                continue
            if (abs(attack_x - enemy['x']) < 40 and
                abs(attack_y - enemy['y']) < 40):
                enemy['health'] -= 2
                self.player['score'] += 150
                if enemy['health'] <= 0:
                    enemy['active'] = False
                        
    def draw_gameover(self):
        self.canvas.delete('all')
        self.canvas.create_rectangle(0, 0, 1024, 600, fill='#1a1a2e')
        
        self.canvas.create_text(512, 200, text="游戏结束", fill='#ff4444', 
                               font=("Microsoft YaHei", 48, "bold"))
        self.canvas.create_text(512, 280, text=f"最终得分: {self.player['score']}", 
                               fill='#ffd700', font=("Arial", 24))
        
        self.canvas.create_rectangle(362, 400, 662, 460, fill='#4a90e2')
        self.canvas.create_text(512, 430, text="重新开始", fill='white', 
                               font=("Microsoft YaHei", 20))
        
        self.canvas.create_text(512, 520, text="点击按钮或按空格键重新开始", 
                               fill='#888888', font=("Microsoft YaHei", 14))
        
        # 绑定重新开始事件
        self.root.bind('<space>', self.restart_game)
        self.root.bind('<Button-1>', self.on_gameover_click)
        
    def restart_game(self, event=None):
        self.root.unbind('<space>')
        self.root.unbind('<Button-1>')
        self.root.bind('<Button-1>', self.on_click)
        self.start_game()
        
    def on_gameover_click(self, event):
        if 362 <= event.x <= 662 and 400 <= event.y <= 460:
            self.restart_game()

    def draw_win(self):
        self.canvas.delete('all')
        self.canvas.create_rectangle(0, 0, 1024, 600, fill='#1a1a2e')

        self.canvas.create_text(512, 180, text="恭喜通关！", fill='#ffd700',
                               font=("Microsoft YaHei", 48, "bold"))
        self.canvas.create_text(512, 260, text=f"最终得分: {self.player['score']}",
                               fill='#ffd700', font=("Arial", 24))
        self.canvas.create_text(512, 320, text=f"剩余生命: {self.player['health']}",
                               fill='#44ff44', font=("Arial", 18))

        self.canvas.create_rectangle(362, 400, 662, 460, fill='#4a90e2')
        self.canvas.create_text(512, 430, text="再来一次", fill='white',
                               font=("Microsoft YaHei", 20))

        self.canvas.create_text(512, 520, text="点击按钮或按空格键重新开始",
                               fill='#888888', font=("Microsoft YaHei", 14))

        self.root.bind('<space>', self.restart_game)
        self.root.bind('<Button-1>', self.on_win_click)

    def on_win_click(self, event):
        if 362 <= event.x <= 662 and 400 <= event.y <= 460:
            self.restart_game()

    def render(self):
        self.canvas.delete('all')
        
        # 背景
        self.canvas.create_rectangle(0, 0, 1024, 600, fill='#1a1a2e')
        
        # 星星（预先生成，不闪烁）
        for star in self.stars:
            alpha = int(100 + 155 * abs(math.sin(time.time() + star['twinkle'])))
            color = f'#{alpha:02x}{alpha:02x}{alpha:02x}'
            self.canvas.create_oval(star['x'], star['y'], 
                                   star['x'] + star['size'], star['y'] + star['size'], 
                                   fill=color)
            
        # 平台
        for platform in self.platforms:
            self.canvas.create_rectangle(platform['x'], platform['y'], 
                                       platform['x'] + platform['w'], 
                                       platform['y'] + platform['h'],
                                       fill='#654321', outline='#8B7355', width=2)
            
        # 金币
        for coin in self.coins:
            if not coin['collected']:
                offset = math.sin(time.time() * 3 + coin['x']) * 3
                self.canvas.create_oval(coin['x']-10, coin['y']-10 + offset, 
                                       coin['x']+10, coin['y']+10 + offset,
                                       fill='#ffd700', outline='#daa520', width=2)
                self.canvas.create_text(coin['x'], coin['y'] + offset, text='$', 
                                       fill='#b8860b', font=("Arial", 12, "bold"))
                
        # 敌人
        for enemy in self.enemies:
            if enemy['active']:
                self.canvas.create_rectangle(enemy['x']-15, enemy['y']-20, 
                                           enemy['x']+15, enemy['y']+20,
                                           fill='#ff4444', outline='#cc0000', width=2)
                self.canvas.create_text(enemy['x'], enemy['y'], text='👾', 
                                       font=("Arial", 16))
                                       
        # 玩家身体
        self.canvas.create_rectangle(self.player['x'], self.player['y'], 
                                   self.player['x'] + 40, self.player['y'] + 40,
                                   fill='#4a90e2', outline='#2c5aa0', width=2)
        # 玩家头部（与身体连接）
        self.canvas.create_oval(self.player['x'] + 5, self.player['y'] - 20, 
                               self.player['x'] + 35, self.player['y'] + 10,
                                 fill='#ffcc99', outline='#cc9966', width=2)
        # 眼睛
        eye_offset = 5 if self.player['vx'] >= 0 else -5
        self.canvas.create_oval(self.player['x'] + 18 + eye_offset, self.player['y'] - 12, 
                                 self.player['x'] + 22 + eye_offset, self.player['y'] - 8,
                                 fill='black')
        
        # 攻击效果
        if self.attack_timer > 0:
            attack_x = self.player['x'] + 55 if self.player['vx'] >= 0 else self.player['x'] - 15
            attack_y = self.player['y'] + 10
            self.canvas.create_arc(attack_x - 20, attack_y - 20, 
                                  attack_x + 20, attack_y + 20,
                                  start=0, extent=120, fill='#ffff00', outline='#ff8800')
        
        # 血条背景
        self.canvas.create_rectangle(20, 15, 220, 35, fill='#333333', outline='#666666')
        # 血条
        hp_percent = max(0, self.player['health'] / 100)
        hp_color = '#44ff44' if hp_percent > 0.5 else '#ffaa00' if hp_percent > 0.25 else '#ff4444'
        self.canvas.create_rectangle(20, 15, 20 + 200 * hp_percent, 35, 
                                   fill=hp_color, outline='')
        self.canvas.create_text(120, 25, text=f"HP: {max(0, self.player['health'])}", 
                               fill='white', font=("Arial", 12, "bold"))
        
        # 分数
        self.canvas.create_text(50, 60, text=f"分数: {self.player['score']}", 
                               fill='#ffd700', font=("Arial", 14, "bold"))
        
        # 地面提示
        if self.on_ground:
            self.canvas.create_text(self.player['x'] + 20, self.player['y'] - 30, 
                                   text="●", fill='#44ff44', font=("Arial", 8))

def main():
    root = tk.Tk()
    game = SimpleGame(root)
    root.mainloop()

if __name__ == "__main__":
    main()
