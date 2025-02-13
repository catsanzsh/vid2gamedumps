import pygame
import sys
import time  # Import the time module

# --- Constants ---
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 480
BRICK_WIDTH = 40
BRICK_HEIGHT = 15
PADDLE_WIDTH = 60
PADDLE_HEIGHT = 10
BALL_SIZE = 10
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 255)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
FPS = 60  # Frames per second
INITIAL_BALL_SPEED = 4


# --- Classes ---

class Brick:
    def __init__(self, x, y, color):
        self.rect = pygame.Rect(x, y, BRICK_WIDTH, BRICK_HEIGHT)
        self.color = color
        self.active = True

    def draw(self, screen):
        if self.active:
            pygame.draw.rect(screen, self.color, self.rect)


class Paddle:
    def __init__(self, x, y):
        self.width = PADDLE_WIDTH
        self.rect = pygame.Rect(x, y, self.width, PADDLE_HEIGHT)
        self.speed = 8  # Paddle movement speed

    def move(self, direction):
        self.rect.x += direction * self.speed
        # Keep the paddle on the screen.
        self.rect.x = max(0, min(self.rect.x, SCREEN_WIDTH - self.width))

    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, self.rect)

    def shrink(self):
        """Shrink the paddle, but don't let it get too small."""
        self.width = max(20, self.width - 10) # Min width of 20.
        self.rect.width = self.width
        # Recentering the paddle makes it feel less jarring when it shrinks.
        self.rect.centerx = SCREEN_WIDTH // 2  # Recenter.


class Ball:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, BALL_SIZE, BALL_SIZE)
        self.speed_x = INITIAL_BALL_SPEED
        self.speed_y = -INITIAL_BALL_SPEED  # Start going upwards.
        self.active = True

    def move(self):
      if not self.active:
        return  # Don't move if the ball is not active.

      self.rect.x += self.speed_x
      self.rect.y += self.speed_y

      # Bounce off the edges of the screen
      if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
          self.speed_x *= -1
          self.rect.x += self.speed_x * 2  # Prevent sticking to the edges.
          wall_sound.play()
      if self.rect.top <= 0:
          self.speed_y *= -1
          self.rect.y += self.speed_y * 2 # Prevent sticking to the top.
          wall_sound.play()

      # Game over condition (or reduce lives)
      if self.rect.bottom >= SCREEN_HEIGHT:
          self.active = False


    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, self.rect.center, BALL_SIZE // 2)

    def bounce_x(self):
        self.speed_x *= -1

    def bounce_y(self):
        self.speed_y *= -1

    def increase_speed(self):
        """Increase the ball's speed, adjusting both x and y components."""
        speed_increase = 0.5
        self.speed_x = (self.speed_x + speed_increase) if self.speed_x > 0 else (self.speed_x - speed_increase)  # Keep original direction
        self.speed_y = (self.speed_y + speed_increase) if self.speed_y > 0 else (self.speed_y - speed_increase)


    def reset(self, x, y):
        """Reset the ball to the starting position."""
        self.rect = pygame.Rect(x, y, BALL_SIZE, BALL_SIZE)
        self.speed_x = INITIAL_BALL_SPEED
        self.speed_y = -INITIAL_BALL_SPEED  # Start going upwards
        self.active = True

# --- Functions ---

def create_bricks(rows, cols):
    bricks = []
    colors = [RED, RED, ORANGE, ORANGE, YELLOW, YELLOW, GREEN, GREEN] # From the original.
    for row in range(rows):
        for col in range(cols):
            brick_x = col * (BRICK_WIDTH + 2) + 1 # Small gap between bricks.
            brick_y = row * (BRICK_HEIGHT + 2) + 50 # Start below the top of the screen.
            color = colors[row % len(colors)]  # Cycle through the colors
            bricks.append(Brick(brick_x, brick_y, color))
    return bricks


def create_sound(frequency, duration):
    """Creates a simple sine wave beep sound."""
    sample_rate = 44100  # Standard audio sample rate
    num_samples = int(duration * sample_rate)
    sound_wave = []
    for i in range(num_samples):
        # Sine wave formula
        sample = int(32767.0*math.sin(2*math.pi*frequency*i/sample_rate))
        sound_wave.append(sample)

    # Pack into 16-bit sound array (signed short)
    sound_array = array.array('h', sound_wave)

    # Create and return the Pygame sound object
    return pygame.mixer.Sound(buffer=sound_array)
    

import math
import array
import pygame.mixer

pygame.mixer.init()
# Define the sounds  (frequency, duration)
paddle_sound = create_sound(440, 0.05)      # A4 note, short duration
brick_sounds = [ #different sound per brick
    create_sound(262, 0.04),   # C4
    create_sound(294, 0.04),   # D4
    create_sound(330, 0.04),   # E4
    create_sound(349, 0.04),   # F4
    create_sound(392, 0.04),    #G4
    create_sound(440, 0.04)    # A4

]

wall_sound = create_sound(220, 0.05)  # Lower frequency for wall bounce.
game_over_sound = create_sound(110, 0.5) # A2, longer duration

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Breakout")
    clock = pygame.time.Clock()

    # Game setup.
    paddle = Paddle(SCREEN_WIDTH // 2 - PADDLE_WIDTH // 2, SCREEN_HEIGHT - 30)
    ball = Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
    bricks = create_bricks(8, SCREEN_WIDTH // (BRICK_WIDTH+2) )  # +2 for a small gap.
    lives = 3
    score = 0
    font = pygame.font.Font(None, 36)  # Default font, size 36
    game_over = False
    level_cleared = False # Flag if all bricks are broken


    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if game_over or level_cleared:
            # Game Over / Level Cleared logic.  Wait for input to restart.
            if game_over:
                game_over_sound.play()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN: # Any key press.
                    if event.key == pygame.K_r:  # Press 'r' to restart
                        # Reset the game
                        game_over = False
                        level_cleared = False
                        lives = 3
                        score = 0
                        ball.reset(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
                        paddle = Paddle(SCREEN_WIDTH // 2 - PADDLE_WIDTH // 2, SCREEN_HEIGHT - 30)  # New paddle.
                        bricks = create_bricks(8, SCREEN_WIDTH // (BRICK_WIDTH + 2))
            # Skip rest of game loop.
            if not running: #If we quit during game over, we are done
              continue
            else: #Draw the "game over" or "level cleared" screen
                screen.fill(BLACK)
                if game_over:
                    text = font.render("Game Over! Press R to Restart", True, WHITE)
                if level_cleared:
                    text = font.render("Level Cleared! Press R to Restart", True, WHITE)

                text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                screen.blit(text, text_rect)
                pygame.display.flip()
                clock.tick(FPS)
                continue  # Skip other processing



        # --- Game logic ---
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            paddle.move(-1)
        if keys[pygame.K_RIGHT]:
            paddle.move(1)

        if ball.active:
          ball.move()

        # Ball and paddle collision
        if ball.rect.colliderect(paddle.rect) and ball.speed_y > 0:
            # Bounce based on position on paddle.
            offset = ball.rect.centerx - paddle.rect.centerx
            ball.speed_x = offset * 0.2  # Scale speed by offset.
            ball.bounce_y()  # Always bounce up.
            paddle_sound.play()

            # Limit maximum horizontal speed
            max_horizontal_speed = 8
            ball.speed_x = max(-max_horizontal_speed, min(ball.speed_x, max_horizontal_speed))

        # Ball and brick collisions
        for i, brick in enumerate(bricks):  # Use enumerate to get the index
            if brick.active and ball.rect.colliderect(brick.rect):
                brick.active = False
                score += 10 #Add to score
                # Simple vertical bounce:
                ball.bounce_y()
                ball.increase_speed()
                sound_index = min(i // (len(bricks) // len(brick_sounds)), len(brick_sounds) -1 ) #which row
                brick_sounds[sound_index].play()

                # Determine if top 2 rows have been hit (for speed up)

                top_rows_cleared = all(not brick.active for brick in bricks if brick.rect.top < (2 * (BRICK_HEIGHT + 2) + 50))
                if top_rows_cleared:
                    # Shrink paddle only once.  Check for top rows.
                    if paddle.width == PADDLE_WIDTH: #If it hasn't shrunk yet.
                        paddle.shrink()



        # Check for game over (no lives left) or win (all bricks destroyed).
        if not ball.active:
            lives -= 1
            if lives == 0:
                game_over = True
            else:
                # Reset ball position for next life
                ball.reset(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)


        if all(not brick.active for brick in bricks):  # Check if the level is cleared
            level_cleared = True


        # --- Drawing ---
        screen.fill(BLACK)
        paddle.draw(screen)
        ball.draw(screen)

        for brick in bricks:
            brick.draw(screen)

        # Display the score and lives.
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        lives_text = font.render(f"Lives: {lives}", True, WHITE)
        screen.blit(lives_text, (SCREEN_WIDTH - 100, 10))


        pygame.display.flip()  # Update the full display Surface to the screen.
        clock.tick(FPS)  # Limit frame rate.

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
