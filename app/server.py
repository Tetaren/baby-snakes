import bottle
import os
import json
import heapq
import copy
import random
from bottle import HTTPResponse

shout = "I am babysnakes, I am babysnakes, I am the world."

@bottle.route("/")
def index():
    return "Your Battlesnake is alive!"

@bottle.post('/start')
def start():
    # data = bottle.request.json
    # game_id = data['game_id']

    head_url = 'https://i.ytimg.com/vi/6l2uKRLmIdQ/hqdefault.jpg'

    response = {"color":"#f4d7f3", "headType":"shades", "tailType":"round-bum"}
    return HTTPResponse(
        status=200,
        headers={"Content-Type": "application/json"},
        body=json.dumps(response),
    )


@bottle.post("/ping")
def ping():
    """
    Used by the Battlesnake Engine to make sure your snake is still working.
    """
    return HTTPResponse(status=200)

@bottle.post('/move')
def move():
    data = bottle.request.json

    move = get_move(data)

    response = {'move':move, 'shout':shout}
    return HTTPResponse(
        status=200,
        headers={"Content-Type": "application/json"},
        body=json.dumps(response),
    )


def get_move(data):
    me = get_me(data)
    moves = get_possible_moves_from_flood(data)
    map = make_map(data, True)

    #Here would be a good place to use conditionals for our move behaviour
    #Plot out new states

    #print(str(confidence(data)) + "\n")
    tastyDistance = 8

    print(tastyDistance)
    if me["health"] < 60 or food_eval(map, data["food"], me["body"][0])[0] < tastyDistance:
        shout = "The wine is flowing!"
        return hungry(data, moves)
    elif confidence(data) > 0:
        shout = "Just like Columbus he get murderous on purpose"
        return kill(data, moves)
    elif me["health"] < 70:
        shout = "The wine is flowing!"
        return hungry(data, moves)
    else:
        shout = "I think maybe this is what America was supposed to be like"
        return default(data, moves)


def get_me(data):
    return data["you"]

def make_extra_dangerous_flood_map(data, map):
    extra_dangerous_flood_map = copy.deepcopy(map)
    board = data["board"]
    for snake in board["snakes"]:
        if snake["id"] == data["you"]["id"]:
            extra_dangerous_flood_map[snake["body"][0].get(u'y')][snake["body"][0].get(u'x')] = 2 #ME
        else:
            extra_dangerous_flood_map[snake["body"][0].get(u'y')][snake["body"][0].get(u'x')] = 3 #ENEMY
        # # Make flood map see safety where snakes cannot move in the next turn (don't get cut off by another snake)
        if snake["body"][0].get(u'y') + 1 < board["height"] and snake["id"] != data["you"]["id"]:
            tempY = snake["body"][0].get(u'y') + 1
            tempX = snake["body"][0].get(u'x')
            extra_dangerous_flood_map[tempY][tempX] = 1
        if (snake["body"][0].get(u'x') + 1) < board["width"] and snake["id"] != data["you"]["id"]:
            tempX = snake["body"][0].get(u'x') + 1
            tempY = snake["body"][0].get(u'y')
            extra_dangerous_flood_map[tempY][tempX] = 1
        if (snake["body"][0].get(u'x') - 1) >= 0 and snake["id"] != data["you"]["id"]:
            tempX = snake["body"][0].get(u'x') - 1
            tempY = snake["body"][0].get(u'y')
            extra_dangerous_flood_map[tempY][tempX] = 1
        if snake["body"][0].get(u'y') - 1 >= 0 and snake["id"] != data["you"]["id"]:
            tempY = snake["body"][0].get(u'y') - 1
            tempX = snake["body"][0].get(u'x')
            extra_dangerous_flood_map[tempY][tempX] = 1

        # now include a second danger spot
        if snake["body"][0].get(u'y') + 2 < board["height"] and snake["id"] != data["you"]["id"]:
            tempY = snake["body"][0].get(u'y') + 2
            tempX = snake["body"][0].get(u'x')
            extra_dangerous_flood_map[tempY][tempX] = 1
        if (snake["body"][0].get(u'x') + 2) < board["width"] and snake["id"] != data["you"]["id"]:
            tempX = snake["body"][0].get(u'x') + 2
            tempY = snake["body"][0].get(u'y')
            extra_dangerous_flood_map[tempY][tempX] = 1
        if (snake["body"][0].get(u'x') - 2) >= 0 and snake["id"] != data["you"]["id"]:
            tempX = snake["body"][0].get(u'x') - 2
            tempY = snake["body"][0].get(u'y')
            extra_dangerous_flood_map[tempY][tempX] = 1
        if snake["body"][0].get(u'y') - 2 >= 0 and snake["id"] != data["you"]["id"]:
            tempY = snake["body"][0].get(u'y') - 2
            tempX = snake["body"][0].get(u'x')
            extra_dangerous_flood_map[tempY][tempX] = 1

    # print(extra_dangerous_flood_map)
    #if data["you"]["name"] == "babysnakes":
        #print("EXTRA Dangerous Floor Map")
        #print(extra_dangerous_flood_map)
    return extra_dangerous_flood_map;

def make_dangerous_flood_map(data, map):
    dangerous_flood_map = copy.deepcopy(map)
    board = data["board"]
    # if data["you"]["name"] == "babysnakes":
    #     print(dangerous_flood_map)
    for snake in board["snakes"]:
        if snake["id"] == data["you"]["id"]:
            dangerous_flood_map[snake["body"][0].get(u'y')][snake["body"][0].get(u'x')] = 2 #ME
        else:
            dangerous_flood_map[snake["body"][0].get(u'y')][snake["body"][0].get(u'x')] = 3 #ENEMY
        # # Make flood map see safety where snakes cannot move in the next turn (don't get cut off by another snake)
        if (snake["body"][0].get(u'y')) + 1 < board["height"] and snake["id"] != data["you"]["id"]:
            tempY = snake["body"][0].get(u'y') + 1
            tempX = snake["body"][0].get(u'x')
            dangerous_flood_map[tempY][tempX] = 1
        if ((snake["body"][0].get(u'x')) + 1) < board["width"] and snake["id"] != data["you"]["id"]:
            tempX = snake["body"][0].get(u'x') + 1
            tempY = snake["body"][0].get(u'y')
            dangerous_flood_map[tempY][tempX] = 1
        if ((snake["body"][0].get(u'x')) - 1) >= 0 and snake["id"] != data["you"]["id"]:
            tempX = snake["body"][0].get(u'x') - 1
            tempY = snake["body"][0].get(u'y')
            dangerous_flood_map[tempY][tempX] = 1
        if (snake["body"][0].get(u'y')) - 1 >= 0 and snake["id"] != data["you"]["id"]:
            tempY = snake["body"][0].get(u'y') - 1
            tempX = snake["body"][0].get(u'x')
            dangerous_flood_map[tempY][tempX] = 1

    #if data["you"]["name"] == "babysnakes":
        #print("Dangerous Floor Map")
        #print(dangerous_flood_map)
    return dangerous_flood_map

def get_possible_moves_from_flood(data):
    map = make_flood_map(data)
    possible_moves = []
    babysnakes = get_me(data)
    head = babysnakes["body"][0]
    board = data["board"]

    x = head["x"]
    y = head["y"]
    # print(map)

    if y != 0 and map[y - 1][x] == 0:
        possible_moves.append({"direction": "up", "count": 0})

    if y != (board["height"] - 1) and map[y + 1][x] == 0:
        possible_moves.append({"direction": "down", "count": 0})

    if x != 0 and map[y][x - 1] == 0:
        possible_moves.append({"direction": "left", "count": 0})

    if x != (board["width"] - 1) and map[y][x + 1] == 0:
        possible_moves.append({"direction": "right", "count": 0})

    # Run flood fill on all possible moves
    for move in possible_moves:
        move_coords = get_move_coordinates(head, move["direction"])
        temp_map = copy.deepcopy(map)
        filled = []
        flood_fill(temp_map, move_coords["x"], move_coords["y"], filled)
        move["count"] = len(filled)

    # Run flood fill on dangerous possible moves
    for move in possible_moves:
        move_coords = get_move_coordinates(head, move["direction"])
        temp_map = make_dangerous_flood_map(data,map)
        filled = []
        flood_fill(temp_map, move_coords["x"], move_coords["y"], filled)
        if len(filled) > 0:
            move["count"] = len(filled)

    # Run flood fill on extra dangerous possible moves
    for move in possible_moves:
        move_coords = get_move_coordinates(head, move["direction"])
        temp_map = make_extra_dangerous_flood_map(data,map)
        filled = []
        flood_fill(temp_map, move_coords["x"], move_coords["y"], filled)
        if len(filled) > 0:
            move["count"] = len(filled)

    babysnakesLength = len(babysnakes["body"])
    final_moves = []
    for move in possible_moves:
        dangerousLength = babysnakesLength
        if (move["count"] > dangerousLength):
            final_moves.append(move["direction"])

    # If all moves are smaller than our body, return the biggest one
    if len(final_moves) is 0 and len(possible_moves) > 0:
        sorted_possible_moves = sorted(possible_moves, key=lambda move: move["count"], reverse=True)
        final_moves.append(sorted_possible_moves[0]["direction"])

    return final_moves


def flood_fill(map, x, y, filled):
    if map[y][x] == 0:
        # Mark as visited
        map[y][x] = 1
        filled.append({'x': x, 'y': y})

        # Check surrounding spots:
        if x > 0:
            flood_fill(map, x - 1, y, filled)
        if x < len(map[y]) - 1:
            flood_fill(map, x + 1, y, filled)
        if y > 0:
            flood_fill(map, x, y - 1, filled)
        if y < len(map) - 1:
            flood_fill(map, x, y + 1, filled)


def get_move_coordinates(head, move):
    x = head["x"]
    y = head["y"]

    if move == 'left':
        return {'x': x - 1, 'y': y}
    if move == 'right':
        return {'x': x + 1, 'y': y}
    if move == 'up':
        return {'x': x, 'y': y - 1}
    if move == 'down':
        return {'x': x, 'y': y + 1}

    print("Invalid move passed in to get_move_coordinates")


def make_flood_map(data):
    wall_coords = []
    map = []
    babysnakes = get_me(data)
    board = data["board"]

    for y in range(board["height"]):
        row = []
        for j in range(board["width"]):
            row.append(0)
        map.append(row)

    for snake in board["snakes"]:
        # Cut off end of tail, since this will move on the next turn
        for body in snake["body"][:-1]:
            wall_coords.append(body)

    for snake in board["snakes"]:
        if snake["id"] != data["you"]["id"]:
            if confidenceVS(data,snake) <= 0:
                wall_coords.append({u'y': snake["body"][0].get(u'y') + 1, u'x': snake["body"][0].get(u'x'), u'object': u'point'})
                wall_coords.append({u'y': snake["body"][0].get(u'y') - 1, u'x': snake["body"][0].get(u'x'), u'object': u'point'})
                wall_coords.append({u'y': snake["body"][0].get(u'y'), u'x': snake["body"][0].get(u'x') + 1, u'object': u'point'})
                wall_coords.append({u'y': snake["body"][0].get(u'y'), u'x': snake["body"][0].get(u'x') - 1, u'object': u'point'})

    for wall in wall_coords:
        if not ((wall.get('y') < 0) or (wall.get('y') >= board["height"]) or (wall.get('x') < 0) or (wall.get('x') >= board["width"])):
            map[wall["y"]][wall["x"]] = 8

    return map


def default(data, flood_fill_moves):
    
    #Acquire a fear of death
    dangersUp, dangersDown, dangersLeft, dangersRight = fear(data,flood_fill_moves)
    
    for direction in flood_fill_moves:
        if (moveOK(dangersUp, dangersDown, dangersLeft, dangersRight,direction)):
            return direction
    #if we get here we are already dead
    return flood_fill_moves[0]

def kill(data, flood_fill_moves):

    #Acquire a fear of death
    dangersUp, dangersDown, dangersLeft, dangersRight = fear(data,flood_fill_moves)
    babysnakes = get_me(data)
    map = make_map(data, True)
    board = data["board"]

    enemy = snake_eval(map, data, board["snakes"], babysnakes["body"][0])
    if not len(enemy):
        return default(data, flood_fill_moves)

    # print ("enemy")
    # print enemy

    targets = [{u'y': enemy[1]["y"]+1, u'x': enemy[1]["x"], u'object': u'point'},
                {u'y': enemy[1]["y"]-1, u'x': enemy[1]["x"], u'object': u'point'},
                {u'y': enemy[1]["y"], u'x': enemy[1]["x"]+1, u'object': u'point'},
                {u'y': enemy[1]["y"], u'x': enemy[1]["x"]-1, u'object': u'point'}]

    # print targets

    random.shuffle(targets)

    for target in targets:
        if not (target.get('x') == babysnakes["body"][0].get('x') and target.get('y') == babysnakes["body"][0].get('y')):
            if not ((target.get('y') < 0) or (target.get('y') >= board["height"]) or (target.get('x') < 0) or (target.get('x') >= board["width"])):
                # print target
                move = get_astar_move(babysnakes["body"][0], target, data)
                if moveOK(dangersUp, dangersDown, dangersLeft, dangersRight, move):
                    #print ("On the mission")
                    return move
    #print ("afraid")
    return default(data, flood_fill_moves)


def fear(data, flood_fill_moves):
    babysnakes = get_me(data)
    head = babysnakes["body"][0]
    board = data["board"]

    x = head["x"]
    y = head["y"]

    dangersLeft = False
    dangersRight = False
    dangersUp = False
    dangersDown = False

    if (len(babysnakes["body"]) > 1):
        firstBody = babysnakes["body"][1]
        xfirstBody = firstBody["x"]
        yfirstBody = firstBody["y"]
        
        #Do not move where flood fill map found to be dangerous, where my body is, where walls are
        if ('up' not in flood_fill_moves) or (y - 1 == yfirstBody) or (y == 0) :
            #Do not move up
            dangersUp = True
        if ('down' not in flood_fill_moves) or (y + 1 == yfirstBody) or (y == board["height"] - 1):
            #Do not move down
            dangersDown = True
        if ('left' not in flood_fill_moves) or (x - 1 == xfirstBody) or (x == 0):
            #Do not move left
            dangersLeft = True
        if ('right' not in flood_fill_moves) or (x + 1 == xfirstBody) or (x == board["width"] - 1):
            #Do not move right
            dangersRight = True

    return dangersUp, dangersDown, dangersLeft, dangersRight

def moveOK(dangersUp, dangersDown, dangersLeft, dangersRight, direction):
    if (direction == 'up'):
        if (dangersUp):
            return False
        else:
            return True
    elif (direction == 'down'):
        if (dangersDown):
            return False
        else:
            return True
    elif (direction == 'left'):
        if (dangersLeft):
            return False
        else:
            return True
    elif (direction == 'right'):
        if (dangersRight):
            return False
        else:
            return True
    else:
        # print "this move is probably not ok: "
        return False

 
def hungry(data, flood_fill_moves):
    babysnakes = get_me(data)
    map = make_map(data, True)
    board = data["board"]
    if not len(board["food"]):
        return default(data, flood_fill_moves)

    food = food_eval(map, board["food"], babysnakes["body"][0])
    if not len(food):
        return default(data, flood_fill_moves)

    move = get_astar_move(babysnakes["body"][0], food[1], data)

    if move in flood_fill_moves:
        return move
    else:
        return default(data, flood_fill_moves)


def food_eval(map, data_food, our_head):
        food_distance = []
        for food in data_food:
            food_distance.append(get_distance(our_head, food))
        sorted(food_distance)
        return food_distance[0]

def snake_eval(map, data, data_snakes, our_head):
    snake_distance = []
    for snake in data_snakes:
        snakeHead = snake["body"][0]
        if snake["id"] != data["you"]["id"]:
            snake_distance.append(get_distance(our_head, snakeHead))
    sorted(snake_distance)
    # print ("snake_distance")
    # print(snake_distance[0])
    return snake_distance[0]


def get_distance(our_head, food_coords):
    x_distance = abs(our_head["x"] - food_coords["x"])
    y_distance = abs(our_head["y"] - food_coords["y"])
    return [ x_distance + y_distance , food_coords]


def make_map(data, excludeFood):
    wall_coords = []
    map = []
    board = data["board"]

    for y in range(board["height"]):
        row = []
        for j in range(board["width"]):
            row.append(0)
        map.append(row)


    for snake in board["snakes"]:
        head_counter = 0
        if snake["id"] == data["you"]["id"]:
            for body in snake["body"][1:]:
                wall_coords.append(body)
        else:
            for body in snake["body"]:
                if (head_counter == 0):
                    wall_coords.append(body)
                    wall_coords.append(body)
                    wall_coords.append(body)
                wall_coords.append(body)


    for wall in wall_coords:
        x = wall["x"]
        y = wall["y"]

        map[y][x] = 1
    
    if (not excludeFood):
        for food in board["food"]:
            wall_coords.append(food)

    for wall in wall_coords:
        x = wall["x"]
        y = wall["y"]

        map[y][x] += 1
    return map


def confidence(data):
    lengthMe = len(get_me(data)["body"])
    maxDiff = 0
    for snake in data["board"]["snakes"]:
        if snake["id"] != data["you"]["id"]:
            diff = lengthMe - len(snake["body"])
            if maxDiff <  diff:
                maxDiff = diff
    return maxDiff

def confidenceVS(data, snake):
    lengthMe = len(get_me(data)["body"])
    lengthThem = len(snake["body"])
    return lengthMe - lengthThem

def get_astar_move(start, goal, data):
    # print("start")
    # print(start)
    # print("goal")
    # print(goal)
    start = (start["x"], start["y"])
    goal = (goal["x"], goal["y"])
    board = data["board"]
    wall_coords     = []
    start           = tuple(start)
    goal            = tuple(goal)

    for snake in board["snakes"]:
        if snake["id"] == data["you"]["id"]:
            for body in snake["body"][1:]:
                wall_coords.append((body["x"], body["y"]))
        else:
            for body in snake["body"]:
                wall_coords.append((body["x"], body["y"]))

    a = AStar()

    a.init_grid(board["height"],board["width"],wall_coords,start,goal)

    solution = a.solve()

    if solution:
        return convert_direction(start, solution[1])

    return None


def convert_direction(start, coord):

    if start[0] > coord[0]:
        return "left"
    elif start[0] < coord[0]:
        return "right"

    if start[1] > coord[1]:
        return "up"

    return "down"


'''
Thanks to Laurent Luce for supplying A*
https://github.com/laurentluce/python-algorithms/
'''

class Cell(object):
    def __init__(self, x, y, reachable):
        """Initialize new cell.
        @param reachable is cell reachable? not a wall?
        @param x cell x coordinate
        @param y cell y coordinate
        @param g cost to move from the starting cell to this cell.
        @param h estimation of the cost to move from this cell
                 to the ending cell.
        @param f f = g + h
        """
        self.reachable = reachable
        self.x = x
        self.y = y
        self.parent = None
        self.g = 0
        self.h = 0
        self.f = 0


class AStar(object):
    def __init__(self):
        # open list
        self.opened = []
        heapq.heapify(self.opened)
        # visited cells list
        self.closed = set()
        # grid cells
        self.cells = []
        self.grid_height = None
        self.grid_width = None

    def init_grid(self, width, height, walls, start, end):
        """Prepare grid cells, walls.
        @param width grid's width.
        @param height grid's height.
        @param walls list of wall x,y tuples.
        @param start grid starting point x,y tuple.
        @param end grid ending point x,y tuple.
        """
        self.grid_height = height
        self.grid_width = width
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                if (x, y) in walls:
                    reachable = False
                else:
                    reachable = True
                self.cells.append(Cell(x, y, reachable))
        self.start = self.get_cell(*start)
        self.end = self.get_cell(*end)

    def get_heuristic(self, cell):
        """Compute the heuristic value H for a cell.
        Distance between this cell and the ending cell multiply by 10.
        @returns heuristic value H
        """
        return 10 * (abs(cell.x - self.end.x) + abs(cell.y - self.end.y))

    def get_cell(self, x, y):
        """Returns a cell from the cells list.
        @param x cell x coordinate
        @param y cell y coordinate
        @returns cell
        """
        return self.cells[x * self.grid_height + y]

    def get_adjacent_cells(self, cell):
        """Returns adjacent cells to a cell.
        Clockwise starting from the one on the right.
        @param cell get adjacent cells for this cell
        @returns adjacent cells list.
        """
        cells = []
        if cell.x < self.grid_width-1:
            cells.append(self.get_cell(cell.x+1, cell.y))
        if cell.y > 0:
            cells.append(self.get_cell(cell.x, cell.y-1))
        if cell.x > 0:
            cells.append(self.get_cell(cell.x-1, cell.y))
        if cell.y < self.grid_height-1:
            cells.append(self.get_cell(cell.x, cell.y+1))
        return cells

    def get_path(self):
        cell = self.end
        path = [(cell.x, cell.y)]
        while cell.parent is not self.start:
            cell = cell.parent
            path.append((cell.x, cell.y))

        path.append((self.start.x, self.start.y))
        path.reverse()
        return path

    def update_cell(self, adj, cell):
        """Update adjacent cell.
        @param adj adjacent cell to current cell
        @param cell current cell being processed
        """
        adj.g = cell.g + 10
        adj.h = self.get_heuristic(adj)
        adj.parent = cell
        adj.f = adj.h + adj.g

    def solve(self):
        """Solve maze, find path to ending cell.
        @returns path or None if not found.
        """
        # add starting cell to open heap queue
        heapq.heappush(self.opened, (self.start.f, self.start))
        while len(self.opened):
            # pop cell from heap queue
            f, cell = heapq.heappop(self.opened)
            # add cell to closed list so we don't process it twice
            self.closed.add(cell)
            # if ending cell, return found path
            if cell is self.end:
                return self.get_path()
            # get adjacent cells for cell
            adj_cells = self.get_adjacent_cells(cell)
            for adj_cell in adj_cells:
                if adj_cell.reachable and adj_cell not in self.closed:
                    if (adj_cell.f, adj_cell) in self.opened:
                        # if adj cell in open list, check if current path is
                        # better than the one previously found
                        # for this adj cell.
                        if adj_cell.g > cell.g + 10:
                            self.update_cell(adj_cell, cell)
                    else:
                        self.update_cell(adj_cell, cell)
                        # add adj cell to open list
                        heapq.heappush(self.opened, (adj_cell.f, adj_cell))


@bottle.post("/end")
def end():
    """
    Called every time a game with your snake in it ends.
    """
    data = bottle.request.json
    print("END:", json.dumps(data))
    return HTTPResponse(status=200)


def main():
    bottle.run(
        application,
        host=os.getenv("IP", "0.0.0.0"),
        port=os.getenv("PORT", "8080"),
        debug=os.getenv("DEBUG", True),
    )


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == "__main__":
    main()
