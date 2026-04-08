import pygame
import random
import sys
import math

# Initialize pygame
pygame.init()

# Setup Display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Word Jumble")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
GREEN = (100, 255, 100)
RED = (255, 100, 100)
BLUE_GRAD_START = (20, 30, 60)
BLUE_GRAD_END = (40, 80, 120)
YELLOW = (255, 223, 0)

# Fonts
try:
    font_large = pygame.font.Font(None, 64)
    font_medium = pygame.font.Font(None, 48)
    font_small = pygame.font.Font(None, 32)
except:
    font_large = pygame.font.SysFont("arial", 64)
    font_medium = pygame.font.SysFont("arial", 48)
    font_small = pygame.font.SysFont("arial", 32)

# Word Lists
easy_words = [
    "cat", "dog", "sun", "hat", "pen", "cup", "book", "tree",
    "fish", "milk", "ball", "star", "moon", "ring", "shoe"
]

medium_words = [
    "apple", "chair", "table", "plant", "bread", "light", "clock",
    "mouse", "phone", "glass", "water", "paper", "smile",
    "dream", "beach", "train"
]

hard_words = [
    "python", "jumble", "complex", "program", "science", "network",
    "algorithm", "database", "function", "variable", "compile",
    "developer", "keyboard", "software", "hardware", "debugging",
    "encryption", "iteration", "recursion", "optimization"
]

# Note: extra_words were commented out by user, keeping it out of the combined list
words = medium_words + hard_words

class Particle:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.vx = random.uniform(-0.5, 0.5)
        self.vy = random.uniform(-1.5, -0.2)
        self.radius = random.randint(2, 6)
        # Give particles a light soft color
        b = random.randint(200, 255)
        self.color = (b - 50, b - 20, b)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        if self.y < -10:
            self.y = HEIGHT + 10
            self.x = random.randint(0, WIDTH)

def draw_gradient_background(surface):
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(BLUE_GRAD_START[0] * (1 - ratio) + BLUE_GRAD_END[0] * ratio)
        g = int(BLUE_GRAD_START[1] * (1 - ratio) + BLUE_GRAD_END[1] * ratio)
        b = int(BLUE_GRAD_START[2] * (1 - ratio) + BLUE_GRAD_END[2] * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))

def jumble_word(word):
    letters = list(word)
    random.shuffle(letters)
    # Ensure jumbled word is not exactly the same as original word
    while ''.join(letters) == word and len(word) > 1:
        random.shuffle(letters)
    return ''.join(letters)

class Game:
    def __init__(self):
        self.state = 'START'  # States: START, PLAYING, RESULT, GAME_OVER
        self.rounds = 5
        self.current_round = 0
        self.score = 0
        self.used_words = random.sample(words, self.rounds)
        self.current_word = ""
        self.jumbled_word = ""
        self.user_input = ""
        self.result_message = ""
        self.result_color = WHITE
        self.result_timer = 0
        self.round_start_time = 0
        
        # Create background particles
        self.particles = [Particle() for _ in range(60)]
        
    def reset(self):
        # We need to pick new random words when resetting
        self.used_words = random.sample(words, self.rounds)
        self.current_round = 0
        self.score = 0
        self.state = 'START'
        self.current_word = ""
        self.jumbled_word = ""
        self.user_input = ""
        
    def next_round(self):
        if self.current_round < self.rounds:
            self.current_word = self.used_words[self.current_round]
            self.jumbled_word = jumble_word(self.current_word)
            self.current_round += 1
            self.user_input = ""
            self.state = 'PLAYING'
            self.result_timer = 0
            self.round_start_time = pygame.time.get_ticks()
        else:
            self.state = 'GAME_OVER'

    def handle_input(self, event):
        if self.state == 'START':
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.next_round()
        elif self.state == 'PLAYING':
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if self.user_input.strip() != "":
                        self.check_guess()
                elif event.key == pygame.K_BACKSPACE:
                    self.user_input = self.user_input[:-1]
                elif event.unicode.isalpha():
                    # Limit length visually
                    if len(self.user_input) < 18:
                        self.user_input += event.unicode.lower()
        elif self.state == 'GAME_OVER':
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.reset()
                self.next_round()

    def check_guess(self):
        guess = self.user_input.strip().lower()
        if guess == self.current_word:
            self.score += 1
            self.result_message = "✅ Correct! Great Job!"
            self.result_color = GREEN
        else:
            self.result_message = f"❌ Wrong! The word was {self.current_word}"
            self.result_color = RED
            
        self.state = 'RESULT'
        self.result_timer = pygame.time.get_ticks()

    def update(self):
        # Update particles
        for p in self.particles:
            p.update()

        if self.state == 'RESULT':
            # Wait 2 seconds before showing the next round
            if pygame.time.get_ticks() - self.result_timer > 2000:
                self.next_round()
        elif self.state == 'PLAYING':
            elapsed = (pygame.time.get_ticks() - self.round_start_time) / 1000
            if elapsed >= 10:
                # Time's up
                self.result_message = f"⏰ Time's up! The word was {self.current_word}"
                self.result_color = YELLOW
                self.state = 'RESULT'
                self.result_timer = pygame.time.get_ticks()

    def draw_text(self, text, font, color, y, x=None, shadow=True):
        if shadow:
            shadow_surface = font.render(text, True, BLACK)
            shadow_rect = shadow_surface.get_rect()
            if x is None:
                shadow_rect.centerx = (WIDTH // 2) + 2
            else:
                shadow_rect.x = x + 2
            shadow_rect.y = y + 2
            screen.blit(shadow_surface, shadow_rect)

        surface = font.render(text, True, color)
        rect = surface.get_rect()
        if x is None:
            rect.centerx = WIDTH // 2
        else:
            rect.x = x
        rect.y = y
        screen.blit(surface, rect)

    def draw(self):
        draw_gradient_background(screen)
        
        # Draw background particles
        for p in self.particles:
            pygame.draw.circle(screen, p.color, (int(p.x), int(p.y)), p.radius)
        
        if self.state == 'START':
            self.draw_text("🎮 Word Jumble 🎮", font_large, WHITE, HEIGHT // 3)
            self.draw_text("Unscramble the letters to form a word", font_small, GRAY, HEIGHT // 2)
            self.draw_text("You have 10 seconds per round!", font_small, YELLOW, HEIGHT // 2 + 50)
            
            # Pulsing logic for the ENTER text
            alpha = int((math.sin(pygame.time.get_ticks() * 0.005) + 1) * 127)
            text_surf = font_medium.render("Press ENTER to start", True, WHITE)
            text_surf.set_alpha(alpha)
            rect = text_surf.get_rect(center=(WIDTH // 2, int(HEIGHT * 0.8)))
            screen.blit(text_surf, rect)
            
        elif self.state == 'PLAYING' or self.state == 'RESULT':
            self.draw_text(f"Round {self.current_round}/{self.rounds}", font_small, GRAY, 20, 20)
            self.draw_text(f"Score: {self.score}", font_small, GRAY, 20, WIDTH - 150)
            
            # Drop shadow for jumbled word
            self.draw_text("Unscramble this word:", font_medium, WHITE, HEIGHT // 4)
            self.draw_text(self.jumbled_word.upper(), font_large, YELLOW, HEIGHT // 2 - 70)
            
            if self.state == 'PLAYING':
                elapsed = (pygame.time.get_ticks() - self.round_start_time) / 1000
                remaining = max(0, 10 - int(elapsed))
                timer_color = RED if remaining <= 3 else WHITE
                self.draw_text(f"⏳ {remaining}s left", font_medium, timer_color, HEIGHT // 4 + 50)
            
            # Input Box with glow effect
            input_rect = pygame.Rect(WIDTH//4, HEIGHT//2 + 30, WIDTH//2, 50)
            pygame.draw.rect(screen, (40, 40, 60), input_rect, border_radius=10)
            pygame.draw.rect(screen, WHITE, input_rect, 3, border_radius=10)
            
            text_surface = font_medium.render(self.user_input.upper(), True, WHITE)
            text_rect = text_surface.get_rect(center=input_rect.center)
            screen.blit(text_surface, text_rect)
            
            if self.state == 'PLAYING':
                self.draw_text("Type your guess and press ENTER", font_small, GRAY, HEIGHT // 2 + 110)
            elif self.state == 'RESULT':
                self.draw_text(self.result_message, font_medium, self.result_color, HEIGHT // 2 + 110)
                
        elif self.state == 'GAME_OVER':
            self.draw_text("🏁 Game Over! 🏁", font_large, WHITE, HEIGHT // 3)
            self.draw_text(f"⭐ Final Score: {self.score} out of {self.rounds} ⭐", font_medium, WHITE, HEIGHT // 2)
            self.draw_text("Press ENTER to play again", font_small, GRAY, int(HEIGHT * 0.7))

def main():
    clock = pygame.time.Clock()
    game = Game()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            game.handle_input(event)
            
        game.update()
        game.draw()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()