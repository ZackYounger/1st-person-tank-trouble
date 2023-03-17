import time
import sys
from copy import deepcopy
from random import randint
 
sys.setrecursionlimit(10000)
 
def buildmaze(boxes):
   
    route = [(1,1)]
    global allsquares
    allsquares = [(1,1)]
##    global maze
    maze = [[1 for i in range(boxes + 1)]for j in range(boxes + 1)]
    maze[1][1] = 0
    step(maze, (1,1), route, boxes)
    return maze
   
def step(maze, coords, route, boxes):
    availableMoves = [(0,1),(1,0),(0,-1),(-1,0)]   #(y,x), [E,S,W,N]
    checkSurroundings = [[(-1,0),(-1,1),(0,1),(1,1),(1,0)],[(0,1),(1,1),(1,0),(1,-1),(0,-1)],[(1,0),(1,-1),(0,-1),(-1,-1),(-1,0)],[(0,-1),(-1,-1),(-1,0),(-1,1),(0,1)]]   #[E,S,W,N][Moves move clockwise]
    for i, move in enumerate(deepcopy(availableMoves)):
        inspectCoords = (coords[0] + move[0], coords[1] + move[1])
        #print(coords,inspectCoords)
        if inspectCoords[0] != 0 and inspectCoords[1] != 0 and inspectCoords[0] != boxes-1 and inspectCoords[1] != boxes-1 and inspectCoords not in allsquares:
            if any(maze[inspectCoords[0]+checkSurroundings[i][chosen][0]][inspectCoords[1]+checkSurroundings[i][chosen][1]] == 0 for chosen in range(len(checkSurroundings[0]))):
                availableMoves.remove(move)
                #print(f"I just removed {move,inspectCoords} because of its surroundings {i}")
                #for chosen in range(len(checkSurroundings[0])):
                    #print(maze[inspectCoords[0]+checkSurroundings[i][chosen][0]][inspectCoords[1]+checkSurroundings[i][chosen][1]],(inspectCoords[0]+checkSurroundings[i][chosen][0],inspectCoords[1]+checkSurroundings[i][chosen][1]))
        else:
            availableMoves.remove(move)
            #print(f"I just removed {move} because of edges")
    #print(availableMoves)
    if len(availableMoves) != 0:
        selected = randint(0,len(availableMoves)-1)
        newCoords = (coords[0] + availableMoves[selected][0], coords[1] + availableMoves[selected][1])
        route.append(newCoords)
        allsquares.append(newCoords)
    else:
        route.remove(coords)
        newCoords = route[len(route) - 1]
       
    maze[newCoords[0]][newCoords[1]] = 0
    ##refresh_screen(maze)
   
    #print(route)
    if newCoords != (1,1):
        step(maze, newCoords, route, boxes)

if __name__ == "__main__":
    maze = buildmaze(20)
    print(maze)
