import pygame, random, asyncio, time
from sys import exit

def postScore(score):
    print("posting score")
    

def gameLost(score):
    dis.fill(black)
    font = pygame.font.SysFont(None, 25)
    score_text = font.render("Score ("+str(score)+")", True, black)
    dis.blit(score_text, [0, 0])
    game_over_text = font.render("Game Over! Enter to play again.", True, white)
    dis.blit(game_over_text, [5, height/2 - 25])
    
    
    
def gameClosed(score):
    dis.fill(black)
    font = pygame.font.SysFont(None, 25)
    score_text = font.render("Score ("+str(score)+")", True, white)
    dis.blit(score_text, [0, 0])
    game_over_text = font.render("See you soon.", True, white)
    dis.blit(game_over_text, [5, height/2 - 25])
    
    

def showScore(score):
    font = pygame.font.SysFont(None, 25)
    score_text = font.render("Score ("+str(score)+")", True, white)
    dis.blit(score_text, [0, 0])
    #pygame.display.update()
    
#draw the snake's shape
def drawSnake(snake_shape):
    #print(snake_shape)
    for x in snake_shape:
        pygame.draw.rect(dis, black, [x[0], x[1], snake_size, snake_size])

# board size
height=400
width=300
dis=pygame.display.set_mode((width,height))
#snake size
snake_size=10
#mouse size
mouse_size=10

# this should be configured in user's profile
gamespeed=5
""" user should be able to select High | Medium | Low speeds """

# create basic colors
blue=(0,0,255)
white=(255,255,255)
black=(0,0,0)
red=(255,0,0)
green=(0,255,0)
brown=(123,63,0)
yellow=(255,255,0)
almond=(234, 221, 202)


# run the game until it is over
async def main():
    global black
    #initialize pygame
    pygame.init()
    # game board
    pygame.display.set_caption('Snake game by Shivansh Goel DNHS APCSP')

    #initial snake position - centered for 
    snake_x = width/2
    snake_y = height/2
    x1_change = 0       
    y1_change = 0
    score=0
    score_increment=1
    snake_shape = []
    snake_len = 1
    game_quit=False
    game_lost=False
    score_posted=False
    # initial mouse position
    mouse_x = round(random.randrange(0, width - mouse_size) / 10.0) * 10.0
    mouse_y = round(random.randrange(0, height - mouse_size) / 10.0) * 10.0

    pygame.draw.rect(dis, black, [snake_x, snake_y, snake_size, snake_size])
    #pygame.display.update()
    #dis.fill(blue)

    #the clock
    clock = pygame.time.Clock()

    
    
    
    # check when game is over
    while not game_quit:
        clock.tick(gamespeed)
 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_quit = True
                dis.fill(black)
                gameClosed(score)
                #pygame.time.wait(3000)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    x1_change = -snake_size
                    y1_change = 0
                elif event.key == pygame.K_RIGHT:
                    x1_change = snake_size
                    y1_change = 0
                elif event.key == pygame.K_UP:
                    y1_change = -snake_size
                    x1_change = 0
                elif event.key == pygame.K_DOWN:
                    y1_change = snake_size
                    x1_change = 0
                elif event.key == pygame.K_RETURN and game_lost:
                    #initial snake position - centered for 
                    snake_x = width/2
                    snake_y = height/2
                    x1_change = 0       
                    y1_change = 0
                    score=0
                    snake_shape = []
                    snake_len = 1
                    game_quit=False
                    game_lost=False
                    score_posted=False
                    # initial mouse position
                    mouse_x = round(random.randrange(0, width - mouse_size) / 10.0) * 10.0
                    mouse_y = round(random.randrange(0, height - mouse_size) / 10.0) * 10.0

                    pygame.draw.rect(dis, black, [snake_x, snake_y, snake_size, snake_size])
                    #pygame.display.update()
                    dis.fill(almond)
        if snake_x >= width or snake_x < 0 or snake_y >= height or snake_y < 0:
            game_lost = True
            dis.fill(black)
                        
        snake_x += x1_change
        snake_y += y1_change
        dis.fill(almond)

        if (score_increment == 1):
            pygame.draw.rect(dis, brown, [mouse_x, mouse_y, snake_size, snake_size])
        elif (score_increment == 2):
            pygame.draw.rect(dis, green, [mouse_x, mouse_y, snake_size, snake_size])
        elif (score_increment == 3):
            pygame.draw.rect(dis, yellow, [mouse_x, mouse_y, snake_size, snake_size])
        elif (score_increment == 4):
            pygame.draw.rect(dis, blue, [mouse_x, mouse_y, snake_size, snake_size])
        elif (score_increment == 5):
            pygame.draw.rect(dis, red, [mouse_x, mouse_y, snake_size, snake_size])
        
        new_snake_pos = []
        new_snake_pos.append(snake_x)
        new_snake_pos.append(snake_y)
        snake_shape.append(new_snake_pos)
        
        if len(snake_shape) > snake_len:
            # delete the tail
            del snake_shape[0]
 
        # if the snake eats its own body, then game is over
        for x in snake_shape[:-1]:
            if x == new_snake_pos:
                game_lost = True
                dis.fill(black)
                
 
        drawSnake(snake_shape)
        showScore(score)
        #pygame.display.update()
 
        if snake_x == mouse_x and snake_y == mouse_y:
            score+=score_increment
            snake_len += score_increment
            mouse_x = round(random.randrange(0, width - mouse_size) / 10.0) * 10.0
            mouse_y = round(random.randrange(0, height - mouse_size) / 10.0) * 10.0
            score_increment = random.randrange(1,6)
 
        if game_lost:
            gameLost(score)
            if not score_posted:
                postScore(score)
                score_posted=True
            
        pygame.display.update()
        await asyncio.sleep(0)

if __name__ == "__main__":
    asyncio.run(main())



