import pygame
import math
from queue import PriorityQueue

# This is for the windows
WIDTH = 700
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("Pathfinding Visualization Tool")

# This is for the color 
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)

# This is the spot || grid
class Spot:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

    def get_position(self):
        return self.row, self.col

    def closed(self):
        return self.color == TURQUOISE
        
    def open(self):
        return self.color == PURPLE

    def obstacle(self):
        return self.color == BLACK

    def start(self):
        return self.color == ORANGE

    def end(self):
        return self.color == GREEN

    def reset(self):
        self.color = WHITE

    def make_start(self):
        self.color = ORANGE

    def make_closed(self):
        self.color = TURQUOISE

    def make_open(self):
        self.color = PURPLE

    def make_obstacle(self):
        self.color = BLACK

    def make_end(self):
        self.color = GREEN

    def make_path(self):
        self.color = YELLOW

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].obstacle(): # were moving down
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].obstacle(): # were moving up
            self.neighbors.append(grid[self.row - 1][self.col])

        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].obstacle(): # were moving right
            self.neighbors.append(grid[self.row][self.col + 1])

        if self.row < 0 and not grid[self.row][self.col - 1].obstacle(): # were moving left
            self.neighbors.append(grid[self.row][self.col - 1])


    # we comparing other spots from this to other spot
    def __lt__(self, other): # lt stands for less than
        return False


def heuristic(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    return abs(x1 - x2) + abs(y1 - y2) # returning absolute distance


def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()


def algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {} # Keep track were we came from
    g_score = {spot: float("inf") for row in grid for spot in row} # inf is infinity in python
    g_score[start] = 0 # the g_score is set to zero
    f_score = {spot: float("inf") for row in grid for spot in row} # inf is infinity in python
    f_score[start] = heuristic(start.get_position(), end.get_position()) # the f_score is the heuristic

    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)
        # drawing the path
        if current == end:
            reconstruct_path(came_from, end, draw) # making the path
            end.make_end()
            return True

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1
            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + heuristic(neighbor.get_position(), end.get_position())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()

        draw()

        if current != start:
            current.make_closed()

    return False


def make_grid(rows, width):
    grid = [] # blank list
    gap = width // rows # // is integer division

    for i in range(rows):
        grid.append([]) # adding 2D blank list
        for j in range(rows):
            spot = Spot(i, j, gap, rows)
            grid[i].append(spot) # add spot in the grid

    return grid


def draw_grid(win, rows, width):
    gap = width // rows
    
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap)) # (x, y)
        for j in range(rows):
            pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width)) # (x, y)


def draw(win, grid, rows, width):
    win.fill(WHITE) # filling the entire screen in white

    for row in grid:
        for spot in row:
            spot.draw(win)

    draw_grid(win, rows, width)
    pygame.display.update() # take what are we drawing and upate that draw in display


# getting the position of mouse where we clicked
def clicked_position(pos, rows, width):
    gap = width // rows
    y, x = pos

    row = y // gap
    col = x // gap

    return row, col


# this take a window
def main(win, width):
    ROWS = 50
    grid = make_grid(ROWS, width)

    start = None
    end = None

    run = True
    while run:
        draw(win, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if pygame.mouse.get_pressed()[0]: # if click the left mouse button
                pos = pygame.mouse.get_pos() # get the positon of a mouse
                row, col = clicked_position(pos, ROWS, width)
                spot = grid[row][col]
                if not start and spot != end:
                    start = spot
                    start.make_start()
                elif not end and spot != start:
                    end = spot
                    end.make_end()
                elif spot != end and spot != start:
                    spot.make_obstacle()
                
            elif pygame.mouse.get_pressed()[2]: # if click the right mouse button
                pos = pygame.mouse.get_pos() # get the positon of a mouse
                row, col = clicked_position(pos, ROWS, width)
                spot = grid[row][col]
                spot.reset()
                if spot == start:
                    start = None
                elif spot == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for spot in row:
                            spot.update_neighbors(grid)

                    algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)

                if event.key == pygame.K_c: # ctrl c to clear the board
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)

    pygame.quit()

main(WIN, WIDTH)