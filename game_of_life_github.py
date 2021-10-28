

import sys
import pip
from subprocess import check_call, call
from copy import deepcopy


def install(package):
    try:
        pip.main(["install",  package])
    except AttributeError:
        check_call([sys.executable, '-m', 'pip', 'install', package])
    call([sys.executable, __file__])


# Try to import pygame
# If it fails, then try to install it
try:
    import pygame
except ModuleNotFoundError:
    print("pygame is not installed\n"
        + "The program will try to install it\n"
        + "If it fails, please manually install pygame package\n")
    install("pygame")

    
# Dimensions of the window
windowWidth = 700
windowHeight = 750
cellWidth = 20
cellHeight = 20
cellBorderThickness = 1
upperGapHeight = 50


# Initilize the window and the clock
pygame.init()
window = pygame.display.set_mode((windowWidth, windowHeight))
pygame.display.set_caption("Game of Life")
clock = pygame.time.Clock()


# Initialize images used in the program
binLogo = pygame.image.load("binLogo.png")
soundOffLogo = pygame.image.load("soundOffLogo.png")
soundOnLogo = pygame.image.load("soundOnLogo.png")


# Set the volume
music = pygame.mixer.music.load("music.wav")
pygame.mixer.music.play(-1) # music will play in an infinite loop
volume = 1.0


# Initialize fonts
fpsFont = pygame.font.SysFont("comicsans", 25, True)
topTextFont = pygame.font.SysFont("comicsans", 16, True)


# Colors used in the window
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
CYAN = (0, 255, 255)
BACKGROUND_COLOR = (40, 40, 70)
BORDER_COLOR = (100, 100, 100)


# Directions
UP = 0
LEFT = 1
DOWN = 2
RIGHT = 3


# fps is the number of generations in a second
# Initially it is set to 10
# Max fps is set to 30, while min fps is set to 1
MAX_FPS = 30
MIN_FPS = 1
fps = 10


class Cell:
    def __init__(self, row, col, width, height, alive):
        self.row = row
        self.col = col
        self.width = width
        self.height = height
        self.alive = alive
        self.nextGenAlive = self.alive
        self.numberOfAliveNeighbors = 0

    def draw(self):
        pygame.draw.rect(window, BORDER_COLOR, (self.col*self.width, self.row*self.height+upperGapHeight, self.width, self.height), cellBorderThickness)
        if self.alive:
            pygame.draw.rect(window, WHITE, (self.col*self.width+cellBorderThickness, self.row*self.height+upperGapHeight+cellBorderThickness, self.width-cellBorderThickness, self.height-cellBorderThickness))
            
    def updateState(self):
        self.alive = self.nextGenAlive

    def changeState(self):
        self.alive = not self.alive
        self.nextGenAlive = self.alive
        

def redrawWindow(cells, initializing = False):
    # Fill the background and write fps
    window.fill(BACKGROUND_COLOR)
    fpsText = fpsFont.render("FPS: {}".format(fps), 1, WHITE)
    window.blit(fpsText, (585, 10))

    if initializing:
        initText = topTextFont.render("Press G to run the game", 1, CYAN)
        window.blit(initText, (240, 3))
        initText = topTextFont.render("Use arrow keys to adjust fps", 1, CYAN)
        window.blit(initText, (220, 26))
        window.blit(binLogo, (10, 10))
        if volume == 1:
            window.blit(soundOnLogo, (60, 10))
        else:
            window.blit(soundOffLogo, (60, 10))
    else:
        inGameText = topTextFont.render("Press S to set cells", 1, CYAN)
        window.blit(inGameText, (260, 15))

        # The Play-Pause Button
        if pause:
            pygame.draw.polygon(window, WHITE, ((10, 10), (10, 40), (36, 25))) # Draw a triangle pointing right
        else:
            pygame.draw.rect(window, WHITE, (10, 10, 10, 30)) # Draw 2 thin vertical rectangle
            pygame.draw.rect(window, WHITE, (30, 10, 10, 30))

        # The Restart Button
        pygame.draw.circle(window, WHITE, (75, 25), 20, 6)
        pygame.draw.rect(window, BACKGROUND_COLOR, (50, 25, 25, 25))
        pygame.draw.polygon(window, WHITE, ((50, 20), (70, 20), (60, 38)))

        # The Forward Button
        pygame.draw.polygon(window, WHITE, ((109, 10), (109, 40), (135, 25)))
        pygame.draw.polygon(window, WHITE, ((124, 10), (124, 40), (150, 25)))

    # Draw every cell
    for row in cells:
        for cell in row:
            cell.draw()
    pygame.display.update()


def checkNeighbors(cells):
    # Traverse over the 2 dimensional array
    # and find numbers of neighbors for every cell
    for row in range(len(cells)):
        for col in range(len(cells[0])):
            if cells[row][col].alive:
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        try:
                            if not (i == 0 and j == 0) and row+i > -1 and col+j > -1:
                                cells[row+i][col+j].numberOfAliveNeighbors += 1
                        except:
                            pass

    # If there are exactly 3 neighbors around a dead cell, it comes to life in the next generation
    # If there are less than 2 or greater than 3 neighbors around a living cell, it dies in the next generation
    for row in range(len(cells)):
        for col in range(len(cells[0])):
            if not cells[row][col].alive and cells[row][col].numberOfAliveNeighbors == 3:
                cells[row][col].nextGenAlive = True
            elif cells[row][col].alive and (cells[row][col].numberOfAliveNeighbors < 2 or cells[row][col].numberOfAliveNeighbors > 3):
                cells[row][col].nextGenAlive = False
            cells[row][col].numberOfAliveNeighbors = 0


# Update the state of every cell
def updateAllCells(cells):
    for row in cells:
        for cell in row:
            cell.updateState()

def clearTable():
    global cells
    for row in cells:
        for cell in row:
            cell.alive = False
            cell.nextGenAlive = False


# Initialize the very first pattern
def initCells():
    global cells, fps, running, initialPattern, volume
    clearButtonIsSelected = False
    soundButtonIsSelected = False
    row = -1
    col = -1
    
    while True:
        for event in pygame.event.get():
            # If you click the cross in the window, the program ends
            if event.type == pygame.QUIT:
                running = False
                return
            # Get the position where you press the left button of the mouse
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT:
                # Check whether the clear button is selected
                if 0 < event.pos[0] < 50 and 0 < event.pos[1] < 50:
                    clearButtonIsSelected = True
                    # Check whether the sound button is selected
                elif 50 < event.pos[0] < 100 and 0 < event.pos[1] < 50:
                    soundButtonIsSelected = True
                else:
                    col = event.pos[0]//cellWidth
                    row = (event.pos[1]-upperGapHeight)//cellHeight
            # Check whether the left button is relased or not
            elif event.type == pygame.MOUSEBUTTONUP and event.button == LEFT:
                # Clear all the living cells
                if clearButtonIsSelected:
                    clearTable()
                    clearButtonIsSelected = False
                # Change the sound status
                elif soundButtonIsSelected:
                    volume = 1 if volume==0 else 0
                    pygame.mixer.music.set_volume(volume)
                    soundButtonIsSelected = False
                # Change the status of the selected cell
                elif row > -1 and col > -1:
                    try:
                        cells[row][col].changeState()
                    except:
                        pass

        # Press G to run the game
        keys = pygame.key.get_pressed()
        if keys[pygame.K_g]:
            break
        # Press up arrow key to increase fps
        elif keys[pygame.K_UP] and fps < MAX_FPS:
            fps += 1
            pygame.time.delay(80)
        # Press down arrow key to decrease fps
        elif keys[pygame.K_DOWN] and fps > MIN_FPS:
            fps -= 1
            pygame.time.delay(80)
            
        redrawWindow(cells, True)
    # Everytime you set cells, the initial pattern is updated
    initialPattern = deepcopy(cells)
    running = True


# Initialize cells on the board and control states
# All cells are dead at the very beginning
cells = [[Cell(i, j, cellWidth, cellHeight, False) for j in range(windowWidth//cellWidth)] for i in range((windowHeight-50)//cellHeight)]
initialPattern = None
running = True
pause = False
buttonSelected = None

# Initialize cells and store the initial pattern in the board
initCells()

while running:
    clock.tick(fps)

    for event in pygame.event.get():
        # If you click the cross in the window, the program ends
        if event.type == pygame.QUIT:
            running = False
        # Check whether you pressed a button or not
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT:
            if 0 < event.pos[0] < 50 and 0 < event.pos[1] < 50: # pause-play button
                buttonSelected = "P"
            elif 50 < event.pos[0] < 100 and 0 < event.pos[1] < 50: # replay button
                buttonSelected = "R"
            elif 100 < event.pos[0] < 150 and 0 < event.pos[1] < 50: # forward button
                buttonSelected = "F"
        elif event.type == pygame.MOUSEBUTTONUP and event.button == LEFT:
            # If it is paused, then it is not paused anymore
            # If it is not  paused, then it is paused now
            if buttonSelected == "P":
                pause = not pause
            # Load the initial pattern and pause
            elif buttonSelected == "R":
                cells = deepcopy(initialPattern)
                pause = True
            # Go to the next generation manually
            # You can use it only if the program is paused
            elif buttonSelected == "F" and pause:
                checkNeighbors(cells)
                updateAllCells(cells)
            buttonSelected = None

    # Get keys which are pressed
    keys = pygame.key.get_pressed()
        
    # Go back to reset the pattern if S is pressed
    if keys[pygame.K_s]:
        initCells()
        continue

    # Redraw the window for every generation
    redrawWindow(cells)

    # If the program is not paused, go to the next generation
    if not pause:
        checkNeighbors(cells)
        updateAllCells(cells)

# Quit and close the window
pygame.quit()








