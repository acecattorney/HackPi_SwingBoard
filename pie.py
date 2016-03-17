# #!/usr/bin/env python2.7  



from Tkinter import *
from math import *
from heapq import *

import RPi.GPIO as GPIO  
GPIO.setmode(GPIO.BCM)  
channel = 17
GPIO.setup(channel, GPIO.IN, pull_up_down=GPIO.PUD_UP)

####################################
# init
####################################

score = 0

def init(data):
    data.mode = "Main Menu"
    data.scoreList = []
    data.nameList = []
    data.score = 0
    data.name = ""
    data.temporalLength = 100
    data.time = data.temporalLength

####################################
# mode dispatcher
####################################

def mousePressed(event, data):
    if (data.mode == "Main Menu"):             mainMenuMousePressed(event, data)
    elif (data.mode == "Play"):                    playMousePressed(event, data)
    elif (data.mode == "High Scores"):        highScoreMousePressed(event, data)
    elif (data.mode == "Entering Score"): enteringScoreMousePressed(event, data)

def keyPressed(event, data):
    if (data.mode == "Main Menu"):               mainMenuKeyPressed(event, data)
    elif (data.mode == "Play"):                      playKeyPressed(event, data)
    elif (data.mode == "High Scores"):          highScoreKeyPressed(event, data)
    elif (data.mode == "Entering Score"):   enteringScoreKeyPressed(event, data)

def timerFired(data):
    if (data.mode == "Main Menu"):                      mainMenuTimerFired(data)
    elif (data.mode == "Play"):                             playTimerFired(data)
    elif (data.mode == "High Scores"):                 highScoreTimerFired(data)
    elif (data.mode == "Entering Score"):          enteringScoreTimerFired(data)

def redrawAll(canvas, data):
    if (data.mode == "Main Menu"):               mainMenuRedrawAll(canvas, data)
    elif (data.mode == "Play"):                      playRedrawAll(canvas, data)
    elif (data.mode == "High Scores"):          highScoreRedrawAll(canvas, data)
    elif (data.mode == "Entering Score"):   enteringScoreRedrawAll(canvas, data)

####################################
# Main Menu mode
####################################

def mainMenuMousePressed(event, data):
    if (event.y > data.height/3 and event.y < data.height*2/3):
        data.mode = 'Play'
        GPIO.add_event_detect(channel, GPIO.RISING, callback=score_callback, bouncetime=150)
        global score
        score = 0
    elif (event.y > data.height*2/3 and event.y < data.height):
        data.mode = 'High Scores'

def mainMenuKeyPressed(event, data):
    pass

def mainMenuTimerFired(data):
    pass

def mainMenuRedrawAll(canvas, data):
    canvas.create_rectangle(0, data.height/3, data.width, data.height*2/3, fill = "cyan")
    canvas.create_rectangle(0, data.height*2/3, data.width, data.height, fill = "orange")
    canvas.create_text(data.width/2, data.height/2, text = "Click here to play!", font="Helvetica 25 bold")
    canvas.create_text(data.width/2, data.height*5/6, text = "High Scores", font="Helvetica 25")
    canvas.create_text(data.width/2, data.height/6, text = "Swing Board", font="Helvetica 30")
    

####################################
# Entering Score mode
####################################

def enterHighScore(data):
    global score
    print data.scoreList
    heappush(data.scoreList, (score, data.name))
    score = 0
    data.name = ""
    data.mode = "Main Menu"

    print(data.scoreList)
    print(data.nameList)

def enteringScoreMousePressed(event, data):
    data.mode = "Main Menu"

def enteringScoreKeyPressed(event, data):
    if (event.keysym.isalnum() and len(event.keysym) == 1):
        data.name += event.keysym
    elif (event.keysym == "BackSpace" and len(data.name) > 0):
        data.name = data.name[0:len(data.name)-1]
    elif (event.keysym == "Return" and len(data.name) > 0):
        enterHighScore(data)
        data.name = ""
        score = 0

def enteringScoreTimerFired(data):
    pass

def enteringScoreRedrawAll(canvas, data):
    canvas.create_text(data.width/2, data.height/4, text = "You got a high score!")
    canvas.create_text(data.width/2, data.height*3/8, text = "Score: " + str(score))
    canvas.create_text(data.width/2, data.height/2, text = "Please enter your name!")
    canvas.create_text(data.width/2, data.height*3/4, text = data.name)

####################################
# High Score mode
####################################

def highScoreMousePressed(event, data):
    data.mode = "Main Menu"

def highScoreKeyPressed(event, data):
    pass

def highScoreTimerFired(data):
    pass

def highScoreRedrawAll(canvas, data):
    canvas.create_text(data.width/2, data.height/7, text = "HIGH SCORES")
    topscores = nlargest(5, data.scoreList)
    for i in range(len(topscores)):
        canvas.create_text(data.width/2, data.height*(i+2)/7, 
            text = str(i+1) + ". " + topscores[i][1] + "   " + str(topscores[i][0]))
    
####################################
# Play mode
####################################

def score_callback(channel):
    global score
    score += 1

def playMousePressed(event, data):
    pass

def playKeyPressed(event, data):
    pass

def playTimerFired(data):
    if data.time <= 0:
        data.mode = "Entering Score"
        GPIO.remove_event_detect(channel)
        data.time = data.temporalLength
    else:
        data.time -= 1

def playRedrawAll(canvas, data):
    canvas.create_text(data.width/2, data.height/2, text = "Blow the paper to score!")
    canvas.create_text(data.width/3, data.height*2/3, text = "Score: " + str(score))
    canvas.create_text(data.width*3/4, data.height*2/3, text = "Time " + str(data.time))

####################################
# run function
####################################

def run(width=300, height=300):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        redrawAll(canvas, data)
        canvas.update()    

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 100 # milliseconds
    init(data)
    # create the root and the canvas
    root = Tk()
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.pack()
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    GPIO.cleanup()
    print("bye!")

run(800, 400)
