import pygame
import random
from enum import Enum
from collections import namedtuple
pygame.init()
font = pygame.font.Font('arial.ttf',25) # much faster to get font from ttf than from system

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

Point = namedtuple('Point','x, y') # lightweight class, only 2 variables are input, is a string separated by commas

BLOCK_SIZE = 20
SPEED = 15
BEDGE = 4 # size of block edge

#RGB colors
WHITE = (255, 255, 255)
RED   = (200, 0, 0)
BLUE1 = (0,0,255)
BLUE2 = (0,100,255)
BLACK = (0,0,0)

class SnakeGame:

    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h
        # init diplay
        self.display = pygame.display.set_mode((self.w,self.h))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()

        # init game state
        self.direction = Direction.RIGHT # direction of snake movement
        
        self.head = Point(self.w/2, self.h/2) # coord of snake head, starts at center of window
        self.snake = [self.head,
                      Point(self.head.x-BLOCK_SIZE,self.head.y), # tuple of block on snake
                      Point(self.head.x-(2*BLOCK_SIZE),self.head.y)] # tuple of block end tail
        
        self.score = 0 #starting with zero score
        self.food = None # nothing eaten yet
        self.speed = SPEED
        self._place_food() #call fcn to place food randomly

    def _place_food(self):
        x = random.randint(0,(self.w-BLOCK_SIZE)//BLOCK_SIZE)*BLOCK_SIZE # divide and multiply to get a random multiple of the block size
        y = random.randint(0,(self.h-BLOCK_SIZE)//BLOCK_SIZE)*BLOCK_SIZE # divide and multiply to get a random multiple of the block size
        self.food = Point(x,y)
        # recursively put the food again if it happens  to be inside the snake
        if self.food in self.snake: # check if tuple of food belongs to snake
            self._place_food()

    def play_step(self):
        # 1. collect user input
        for event  in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit() # exit python program too
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.direction = Direction.LEFT
                elif event.key == pygame.K_RIGHT:
                    self.direction = Direction.RIGHT
                elif event.key == pygame.K_UP:
                    self.direction = Direction.UP
                elif event.key == pygame.K_DOWN:
                    self.direction = Direction.DOWN

        # 2. move snake
        self._move(self.direction) #updates the head
        self.snake.insert(0,self.head) # adds at the beginning (place 0) the new head location, NOT APPEND BECAUSE THEN IT PUTS IT LAST

        # 3. check if game over
        game_over = False
        if self._is_collision():
            game_over = True
            return game_over, self.score

        # 4. place new food or just move snake
        if self.head == self.food:
            self.score += 1
            self.speed += 1 #goes a bit faster every time
            self._place_food()
        else:
            self.snake.pop() # removes the last element of snake 'moves it'
        

        # 5. update UI and clock
        self._update_ui()
        self.clock.tick(self.speed) #controls how fast frame updates

        # 6. return if game over and score
        return game_over, self.score
    
    def _is_collision(self):
        # check if hits boundary
        if self.head.x > self.w - BLOCK_SIZE or self.head.x < 0 or \
           self.head.y > self.h - BLOCK_SIZE or self.head.y < 0:
            return True
        #check if hits self
        if self.head in self.snake[1:]: # start with 1 because 0 is the head
            return True
        # if nothing happens return false
        return False
    
    def _update_ui(self):
        self.display.fill(BLACK) # fill window with black first

        # draw block by block the snake
        for pt in self.snake:
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x,pt.y,BLOCK_SIZE,BLOCK_SIZE))
            pygame.draw.rect(self.display, BLUE2, pygame.Rect(pt.x+BEDGE,pt.y+BEDGE,BLOCK_SIZE-2*BEDGE,BLOCK_SIZE-2*BEDGE))
        
        # draw the food
        pygame.draw.rect(self.display,RED,pygame.Rect(self.food.x,self.food.y, BLOCK_SIZE,BLOCK_SIZE))

        # display the score
        text = font.render("Score: " + str(self.score),True, WHITE)
        self.display.blit(text,[0,0])
        pygame.display.flip() # sends change to screen

    def _move(self, direction):
        x = self.head.x
        y = self.head.y

        if direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif direction == Direction.UP:
            y -= BLOCK_SIZE

        self.head = Point(x,y)



if __name__ == '__main__':
    game = SnakeGame()

    # game loop
    while True:
        game_over, score = game.play_step()

        # exit if game over
        if game_over == True:
            break

    print('Final Score', score)
    
    pygame.quit()