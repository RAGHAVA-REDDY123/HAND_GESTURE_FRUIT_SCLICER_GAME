import cv2
import mediapipe as mp
import pygame
import random
import time

# --- Pygame Setup ---
pygame.init()
WIDTH, HEIGHT = 640, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("FRUIT CUTTER GAME")
clock = pygame.time.Clock()

## load the sounds
bomb_sound = pygame.mixer.Sound('requirements/bombsound.flac')
fruit_sound = pygame.mixer.Sound('requirements/fruitsound.wav')

# --- Load Images ---
fruit_images = {
    "pumpkin": pygame.transform.scale(pygame.image.load("requirements/pumpkin.png"), (70, 70)),
    "strawberry": pygame.transform.scale(pygame.image.load("requirements/Strawberry.png"), (70, 70)),
    "grapes": pygame.transform.scale(pygame.image.load("requirements/Grapes.png"), (70, 70)),
    "cherry": pygame.transform.scale(pygame.image.load("requirements/cherry.png"), (50, 50)),
    "pineapple": pygame.transform.scale(pygame.image.load("requirements/pineapple.png"), (50, 50)),
    "bomb": pygame.transform.scale(pygame.image.load("requirements/bomb.png"), (50, 50))
}
fruit_types = list(fruit_images.keys())

# --- Fruit Class ---
class Fruit:
    def __init__(self):
        self.type = random.choice(fruit_types)
        self.image = fruit_images[self.type]
        self.x = random.randint(100, WIDTH - 100)
        self.y = HEIGHT
        self.velocity = random.randint(10, 25)
        self.hitbox = pygame.Rect(self.x, self.y, 100, 100)

    def move(self):
        self.y -= self.velocity
        self.hitbox.topleft = (self.x, self.y)

    def draw(self):
        screen.blit(self.image, (self.x, self.y))

# --- MediaPipe Hand Tracking ---
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.5)
mp_draw = mp.solutions.drawing_utils
cap = cv2.VideoCapture(0)

fruits = [Fruit()]
score = 0
running = True
paused = False
index_finger_x = 0
index_finger_y = 0

# --- Game Loop ---
while running:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    # Event handling for handling pause and quit the game
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                paused = not paused
            elif event.key == pygame.K_q:
                running = False

    if paused:
        continue

    # Hand tracking and finger position
    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)
            h, w, _ = img.shape
            index_finger_x = int(handLms.landmark[8].x * w)
            index_finger_y = int(handLms.landmark[8].y * h)
            cv2.circle(img, (index_finger_x, index_finger_y), 10, (0, 255, 0), -1)

    screen.fill((0, 0, 0))

    # Add new fruit randomly
    if random.randint(1, 7) == 1:
        fruits.append(Fruit())

    # Update and draw fruits
    for fruit in fruits[:]:
        fruit.move()
        fruit.draw()

        if index_finger_x and index_finger_y:
            # Map the Index finger position to the gaming screen
            mapped_x = int(index_finger_x * (WIDTH / w))
            mapped_y = int(index_finger_y * (HEIGHT / h))
            pygame.draw.circle(screen, (0, 255, 0), (mapped_x, mapped_y), 10)

            #if the finger touches the fruit
            if fruit.hitbox.collidepoint((mapped_x, mapped_y)):
                if fruit.type == "bomb":
                    bomb_sound.play()
                    font = pygame.font.SysFont(None, 50)
                    text = font.render("GAME OVER", True, (255, 0, 0))
                    screen.blit(text, (100, 200))
                    screen.blit(score_text, (100, 250))
                    game_over_text = font.render("Press R to Restart or Q to Quit", True, (255, 0, 0))
                    screen.blit(game_over_text, (50, 300))
                    pygame.display.update() 

                    
                    game_over = True
                    while game_over:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                running = False
                                game_over = False
                            elif event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_r:
                                    fruits.clear()
                                    fruits.append(Fruit())
                                    score = 0
                                    game_over = False
                                elif event.key == pygame.K_q:
                                    running = False
                                    game_over = False

                ## If the fruit is not a bomb
                else:
                    fruit_sound.play()
                    fruits.remove(fruit)
                    score += 1

    # Display Score
    font = pygame.font.SysFont(None, 40)
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))
    info_text = font.render("PRESS P TO PAUSE/RESUME THE GAME", True, (255, 0, 0))
    screen.blit(info_text, (50, 50))

    pygame.display.update()
    clock.tick(30)

    # Show camera feed
    cv2.imshow("Hand Tracking", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        running = False

# Cleanup
cap.release()
cv2.destroyAllWindows()
pygame.quit()
