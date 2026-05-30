class Level:
    def __init__(self, id, grid, forward_spawn, backward_spawn):
        self.id = id
        self.grid = grid
        
        self.forward_spawn = forward_spawn
        self.backward_spawn = backward_spawn
        
        self.total_cubes =  sum(row.count("C") for row in self.grid)
        