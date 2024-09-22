from collections import deque

def SolveMaze(Maze):
    rows, cols = len(maze),len(maze[0])
    start = "S"
    goal = "E"
    
    for r in range(rows):
        for c in range(cols):
            if Maze[r][c] == start:
                start = r, c
                break
        else: continue
        break
    else:
        return None
    
    queue = deque()
    queue.appendleft((start[0], start[1], 0))
    directions = [[0, 1], [0, -1], [1, 0], [-1, 0]]
    visited = [[False] * cols for _ in range(rows)]
     
    
    
    
    
    
    
    return




maze = [
    ["S", 1, 0, 0, 0],
    [0, 1, 0, 1, 0],
    [0, 0, 0, 1, 0],
    [0, 1, 1, 1, 0],
    [0, 0, 0, 0, "E"]
]

SolveMaze(maze)