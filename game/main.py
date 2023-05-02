# uses pygame 
# uses pygbag
# Ref: https://pypi.org/project/pygbag/
# Runs python code directly in modern web brows

import pygame, random, asyncio, time, sys
from sys import exit, path
from fetch import RequestHandler
import json

""" User Profile fields """
#logged in user's id
# default to 0 uid and username Guest
# in the guest mode the scores are not saved
uid=0
username="Guest"
# default difficulty is 1 (beginner)
difficulty=1

previousHighScore=0
# this depends on the difficulty level. Default 0 (slowest)
gamespeed=2
""" User Profile fields """

# RequestHandler from fetch.py
# used to save scores by calling async fetch to model API
req = RequestHandler()
# board size
height=400
width=300

# initial display
dis=pygame.display.set_mode((width,height))
#snake size
snake_size=10
#mouse size
mouse_size=10

# create basic colors
blue=(0,0,255)
white=(255,255,255)
black=(0,0,0)
red=(255,0,0)
green=(0,255,0)
brown=(123,63,0)
yellow=(255,255,0)
almond=(234, 221, 202)

# to track when the score is successfully posted
score_post_success=False

# get logged in user's info using RequestHandler
# this will set the user profile data and customize difficulty and speed
async def getUserInfo():
    print("Getting user data")
    try:
        # call getLoginUser from RequestHandler - custom function
        userdata = await RequestHandler.getLoginUser(req)
        print ("Got user data")
        print (userdata)
        global username
        global uid
        global difficulty
        global gamespeed
        global previousHighScore
        userinfo = json.loads(userdata)
        if (userinfo.get('valid')):
            print(userinfo.get("id"))
            # score.uid is same as gamer.id
            uid = userinfo.get("id")
            difficulty = userinfo.get("level")
            username = userinfo.get("name")
            previousHighScore = userinfo.get("highscore")

            # speed progressively increases with difficulty levels, topping out at 10
            if (difficulty == 0):
                gamespeed = 2
            elif (difficulty == 1):
                gamespeed = 4
            elif (difficulty == 2):
                gamespeed = 5
            elif (difficulty == 3):
                gamespeed = 6
            elif (difficulty == 4):
                gamespeed = 8
            elif (difficulty == 5):
                gamespeed = 10

        return userdata
    except:
        print("Error in getting user data")

# displays the tier of the user as user scores increase
def showTier():
    global gamespeed
    font = pygame.font.SysFont(None, 15)
    tierVal = "Beginner"
    if (gamespeed < 4):
        tierVal = "Beginner"
    elif (gamespeed == 4):
        tierVal = "Easy"
    elif (gamespeed == 5):
        tierVal = "Medium"
    elif (gamespeed == 6 or gamespeed == 7):
        tierVal = "Hard"
    elif (gamespeed == 8 or gamespeed == 9):
        tierVal = "Master"
    elif (gamespeed >= 10):
        tierVal = "God"
    score_text = font.render(tierVal + " Tier", True, black)
    dis.blit(score_text, [width-70, 0])

# posts the score to the model / db layer using fetch api
async def postScore(score):
    global score_post_success
    global previousHighScore
    print("posting score")
    myobj = "{\"score\": \""+str(score)+"\",\"uid\": \""+str(uid)+"\"}"
    result = await RequestHandler.postScore(req, data= json.loads(myobj), newScore=score, previousHighScore=previousHighScore)
    print("Result is: " + result)
    score_post_success=True

    # keeps track of high scores
    if score > previousHighScore:
        previousHighScore = score

# function called when game is lost
# shows scores, message to restart game
def gameLost(score):
    dis.fill(black)
    font = pygame.font.SysFont(None, 15)
    score_text = font.render(username + " - ("+str(score)+")", True, white)
    dis.blit(score_text, [0, 0])
    font1 = pygame.font.SysFont(None, 25)
    game_over_text = font1.render("Game Over! Enter to play again.", True, white)
    dis.blit(game_over_text, [5, height/2 - 25])

    if score_post_success:
        score_text = font.render("Score posted on server", True, white)
        dis.blit(score_text, [150, 0])

# function called when game is closed
# shows messages
def gameClosed(score):
    dis.fill(black)
    font = pygame.font.SysFont(None, 15)
    score_text = font.render(username + " - ("+str(score)+")", True, white)
    dis.blit(score_text, [0, 0])
    font1 = pygame.font.SysFont(None, 25)
    game_over_text = font1.render("See you soon " + username, True, white)
    dis.blit(game_over_text, [5, height/2 - 25])

# displays scores on the game UI as game progresses
def showScore(score):
    font = pygame.font.SysFont(None, 15)
    score_text = font.render(username + " - ("+str(score)+")", True, black)
    dis.blit(score_text, [0, 0])
    #pygame.display.update()
    showTier()
    
#draw the snake's shape
def drawSnake(snake_shape):
    #print(snake_shape)
    for x in snake_shape:
        pygame.draw.rect(dis, black, [x[0], x[1], snake_size, snake_size])

# run the game until it is over
async def main():
    global gamespeed
    global previousHighScore
    await getUserInfo()
    #asyncio.run(postScore(0))
    global black
    #initialize pygame
    pygame.init()
    # game board
    pygame.display.set_caption('Snake game by Shivansh Goel DNHS APCSP')

    #place the snake in the middle of the screen in the beginning
    snake_x = width/2
    snake_y = height/2
    x1_change = 0
    y1_change = 0
    score=0
    oldscore=0
    score_increment=1
    snake_shape = []
    # snake starts with length of 1
    snake_len = 1
    game_quit=False
    game_lost=False
    game_lost_disp=False
    score_posted=False
    is_beginner = False
    
    if gamespeed == 2:
        is_beginner = True

    # initial mouse position - randomized
    mouse_x = round(random.randrange(0, width - mouse_size) / 10.0) * 10.0
    mouse_y = round(random.randrange(0, height - mouse_size) / 10.0) * 10.0

    pygame.draw.rect(dis, black, [snake_x, snake_y, snake_size, snake_size])

    #the clock
    clock = pygame.time.Clock()    
    
    # check when game is over
    while not game_quit:
        # increment game speed after gamer get 10 more points than before
        if score - oldscore > 10:
            oldscore += 10
            if gamespeed < 10:
                gamespeed += 1
            else:
                print("God Tier")
        
        # clock tick with gamespeed. This controls how fast the game moves
        clock.tick(gamespeed)
 
        # check for user events (up | down | left | right | close | enter)
        for event in pygame.event.get():
            # close the game
            if event.type == pygame.QUIT:
                game_quit = True
                dis.fill(black)
                gameClosed(score)
            # if the event is key down, check for which key
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
                # enter key restarts the game (when the previous game is lost)
                elif event.key == pygame.K_RETURN and game_lost:
                    await RequestHandler.clearHighScore(req)
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

        # if the snake hits the wall then game ends, except when it is beginner mode (did this for my little sister)
        # in case of beginners the snake wraps around and comes out of the other side of the screen
        if snake_x >= width or snake_x < 0 or snake_y >= height or snake_y < 0:
            if is_beginner: 
                if snake_x >=width:
                    snake_x = 0
                elif snake_x <= 0:
                    snake_x = width
                elif snake_y >= height:
                    snake_y = 0
                elif snake_y <= 0:
                    snake_y = height
            else:
                game_lost = True
                dis.fill(black)

        # make snake move 
        snake_x += x1_change
        snake_y += y1_change
        dis.fill(almond)

        # to make things interesting, provide different colored snakes with different score increments
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
                print("lost")
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
                if username != "Guest":
                    await postScore(score)
                score_posted=True

        pygame.display.update()
        await asyncio.sleep(0)

if __name__ == "__main__":
    asyncio.run(main())