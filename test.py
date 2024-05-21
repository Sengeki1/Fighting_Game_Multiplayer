import pygame
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
width, height = 800, 600
screen = pygame.display.set_mode((width, height))

# Colors
white = (255, 255, 255)
black = (0, 0, 0)

# Font
font = pygame.font.Font(None, 74)

# Timer duration (in seconds)
countdown_time = 5

# Set up the clock
clock = pygame.time.Clock()

# Function to reset the timer
def reset_timer():
    global start_ticks
    start_ticks = pygame.time.get_ticks()

# Main function
def main():
    global countdown_time, start_ticks
    start_ticks = pygame.time.get_ticks()  # Get the current time in milliseconds

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # Reset timer on 'r' key press
                    reset_timer()

        # Calculate the elapsed time
        seconds = (pygame.time.get_ticks() - start_ticks) // 1000
        time_left = countdown_time - seconds

        # Clear the screen
        screen.fill(white)

        # Render the countdown timer
        if time_left >= 0:
            timer_text = font.render(str(time_left), True, black)
            screen.blit(timer_text, (width // 2 - timer_text.get_width() // 2, height // 2 - timer_text.get_height() // 2))
        else:
            timer_text = font.render("Time's up!", True, black)
            screen.blit(timer_text, (width // 2 - timer_text.get_width() // 2, height // 2 - timer_text.get_height() // 2))

        # Update the display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
