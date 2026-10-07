import random
import pygame

WIDTH, HEIGHT = 800, 600
GRAVITY, JUMP_SPEED, WALK_SPEED = 1500, -640, 220
BUBBLE_TRAVEL, BUBBLE_LIFE = 0.45, 8.0
PLATFORMS = [
    pygame.Rect(0, 570, WIDTH, 30),
    pygame.Rect(0, 450, 300, 16),
    pygame.Rect(500, 450, 300, 16),
    pygame.Rect(150, 330, 500, 16),
    pygame.Rect(0, 210, 250, 16),
    pygame.Rect(550, 210, 250, 16),
]
SPAWNS = [(200, 330), (600, 330), (100, 210), (700, 210), (150, 450), (650, 450), (400, 330), (60, 570)]


def bubble_tint(bubble):
    """Return an (r, g, b) colour for a bubble, or None for the default."""
    pass


def on_fruit_collected(fruit):
    """Called when the player picks up a fruit; add a sound, sparkle, or bonus effect here."""
    pass


def bonus_life_threshold():
    """Return a score value at which the player earns an extra life, or None to disable bonus lives."""
    pass


class Body:
    """Anything that falls and lands on platforms. x is the centre, y is the bottom edge."""

    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.vx = self.vy = 0.0
        self.on_ground = False

    @property
    def rect(self):
        return pygame.Rect(self.x - self.w / 2, self.y - self.h, self.w, self.h)

    @property
    def center(self):
        return pygame.Vector2(self.x, self.y - self.h / 2)

    def move(self, dt):
        self.vy = min(self.vy + GRAVITY * dt, 900)
        previous_bottom = self.y
        self.x = max(self.w / 2, min(WIDTH - self.w / 2, self.x + self.vx * dt))
        self.y += self.vy * dt
        self.on_ground = False
        if self.vy >= 0:
            for plat in PLATFORMS:
                overlaps = self.x + self.w / 2 > plat.left and self.x - self.w / 2 < plat.right
                if overlaps and previous_bottom <= plat.top + 1 and self.y >= plat.top:
                    self.y, self.vy, self.on_ground = plat.top, 0.0, True
                    break


class Player(Body):
    def __init__(self):
        super().__init__(WIDTH / 2, 570, 30, 30)
        self.facing, self.cooldown, self.invulnerable = 1, 0.0, 2.0

    def update(self, dt, keys):
        direction = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
        if direction:
            self.facing = direction
        self.vx = direction * WALK_SPEED
        self.cooldown -= dt
        self.invulnerable = max(0.0, self.invulnerable - dt)
        self.move(dt)


class Enemy(Body):
    def __init__(self, x, y, angry=False):
        super().__init__(x, y, 28, 28)
        self.speed = 130 if angry else 70
        self.direction, self.think = random.choice([-1, 1]), 0.0

    def update(self, dt, player):
        self.think -= dt
        if self.think <= 0:
            self.direction = 1 if player.x > self.x else -1
            self.think = random.uniform(0.4, 1.2)
        self.vx = self.direction * self.speed
        if self.on_ground and player.y < self.y - 40 and random.random() < dt * 1.5:
            self.vy = JUMP_SPEED
        self.move(dt)


class Bubble:
    def __init__(self, x, y, direction):
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(direction * 260, 0)
        self.age, self.enemy, self.life = 0.0, None, BUBBLE_LIFE

    @property
    def radius(self):
        return 22 if self.enemy else 14

    def update(self, dt):
        self.age += dt
        if self.age >= BUBBLE_TRAVEL:
            self.vel.x *= max(0.0, 1 - 3 * dt)
            self.vel.y = -70
        self.pos += self.vel * dt
        self.pos.x = max(self.radius, min(WIDTH - self.radius, self.pos.x))
        if self.enemy:
            self.life -= dt


class Fruit(Body):
    def __init__(self, x, y, value):
        super().__init__(x, y, 18, 18)
        self.value, self.life = value, 10.0

    def update(self, dt):
        self.life -= dt
        self.move(dt)


class Game:
    def __init__(self):
        self.font = pygame.font.Font(None, 26)
        self.reset()

    def reset(self):
        self.level, self.score, self.lives, self.combo, self.state = 1, 0, 3, 0, "play"
        self.bonus_awarded = 0
        self.player = Player()
        self.fruits = []
        self.start_level()

    def start_level(self):
        self.bubbles = []
        count = min(8, 2 + self.level)
        self.enemies = [Enemy(x, y) for x, y in random.sample(SPAWNS, count)]

    def blow_bubble(self):
        player = self.player
        if player.cooldown <= 0 and self.state == "play":
            player.cooldown = 0.3
            self.bubbles.append(Bubble(player.x + player.facing * 22, player.center.y, player.facing))

    def trap_enemies(self, bubble):
        if bubble.enemy or bubble.age >= 1.5:
            return
        for enemy in self.enemies:
            if bubble.pos.distance_squared_to(enemy.center) < 24 * 2:
                self.enemies.remove(enemy)
                bubble.enemy, bubble.vel.x = enemy, bubble.vel.x * 0.2
                return

    def pop(self, bubble):
        self.bubbles.remove(bubble)
        if bubble.enemy:
            self.combo += 1
            self.score += 100
            self.fruits.append(Fruit(bubble.pos.x, bubble.pos.y, 100 * self.combo))
        self.player.vy = -260

    def release(self, bubble):
        self.bubbles.remove(bubble)
        enemy = bubble.enemy
        enemy.x, enemy.y = bubble.pos.x, bubble.pos.y + enemy.h / 2
        enemy.speed, enemy.vy = 130, 0.0
        self.enemies.append(enemy)

    def update(self, dt, keys):
        if self.state != "play":
            return
        player = self.player
        player.update(dt, keys)
        if player.on_ground:
            self.combo = 0
        threshold = bonus_life_threshold()
        if threshold and self.score // threshold > self.bonus_awarded:
            self.bonus_awarded = self.score // threshold
            self.lives += 1
        if keys[pygame.K_SPACE]:
            self.blow_bubble()
        for enemy in self.enemies:
            enemy.update(dt, player)
        for bubble in self.bubbles[:]:
            bubble.update(dt)
            self.trap_enemies(bubble)
            above = player.vy > 0 and player.y <= bubble.pos.y + 6
            if above and player.center.distance_to(bubble.pos) < bubble.radius + 14:
                self.pop(bubble)
            elif bubble.enemy and bubble.life <= 0:
                self.release(bubble)
            elif bubble.pos.y < -bubble.radius:
                self.bubbles.remove(bubble)
        for fruit in self.fruits[:]:
            fruit.update(dt)
            if fruit.rect.colliderect(player.rect):
                self.score += fruit.value
                self.fruits.remove(fruit)
                on_fruit_collected(fruit)
            elif fruit.life <= 0:
                self.fruits.remove(fruit)
        if player.invulnerable <= 0:
            for enemy in self.enemies:
                if enemy.rect.colliderect(player.rect):
                    self.lives -= 1
                    self.player = Player()
                    if self.lives <= 0:
                        self.state = "lose"
                    break
        if not self.enemies and not any(b.enemy for b in self.bubbles):
            self.level += 1
            self.start_level()

    def draw(self, screen):
        screen.fill((14, 16, 40))
        for plat in PLATFORMS:
            pygame.draw.rect(screen, (90, 60, 160), plat)
            pygame.draw.rect(screen, (150, 120, 220), (plat.left, plat.top, plat.width, 4))
        for fruit in self.fruits:
            pygame.draw.circle(screen, (230, 60, 80), fruit.center, 9)
        for enemy in self.enemies:
            color = (240, 90, 60) if enemy.speed > 100 else (240, 160, 50)
            pygame.draw.rect(screen, color, enemy.rect, border_radius=6)
            pygame.draw.circle(screen, (255, 255, 255), enemy.center - (5, 3), 3)
            pygame.draw.circle(screen, (255, 255, 255), enemy.center + (5, -3), 3)
        for bubble in self.bubbles:
            if bubble.enemy:
                pygame.draw.circle(screen, (240, 160, 50), bubble.pos, 9)
            color = bubble_tint(bubble) or ((120, 230, 255) if bubble.enemy is None else (255, 190, 230))
            pygame.draw.circle(screen, color, bubble.pos, bubble.radius, 2)
        player = self.player
        if player.invulnerable <= 0 or int(player.invulnerable * 10) % 2 == 0:
            pygame.draw.rect(screen, (70, 210, 110), player.rect, border_radius=8)
            eye = player.center + (player.facing * 6, -4)
            pygame.draw.circle(screen, (255, 255, 255), eye, 4)
        hud = self.font.render(f"Score {self.score}  Lives {self.lives}  Level {self.level}  R = reset", True, (240, 240, 240))
        screen.blit(hud, (10, 8))
        if self.state == "lose":
            label = self.font.render("GAME OVER - Press R", True, (255, 255, 120))
            screen.blit(label, label.get_rect(center=(WIDTH // 2, HEIGHT // 2)))


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Bubble Bobble")
    clock = pygame.time.Clock()
    game = Game()
    running = True
    while running:
        dt = min(clock.tick(60) / 1000, 0.05)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                if game.player.on_ground:
                    game.player.vy = JUMP_SPEED
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                game.reset()
        game.update(dt, pygame.key.get_pressed())
        game.draw(screen)
        pygame.display.flip()
    pygame.quit()


if __name__ == "__main__":
    main()
