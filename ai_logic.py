# using the Z3 solver for predicate logic
#   USE: pip3 install z3-solver
from z3 import *


class MinesweeperAI:

    #create and define the board for the AI to use
    def __init__(self, height, width):
        self.rows = height
        self.cols = width

        self.solver = Solver()

        # mine[r][c] = Bool variable representing “cell (r,c) is a mine” (true = mine, false = safe)
        self.mine = [[Bool(f"m_{r}_{c}") for c in range(self.cols)] for r in range(self.rows)]

        self.opened = set()
        self.flags = set()

        self.cache_safe = {}
        self.cache_mine = {}

        self.neighbor_sets = {
            (r, c): list(self.neighbors(r, c))
            for r in range(self.rows)
            for c in range(self.cols)
        }

        self.frontier = set()   #spaces around the numbered spaces (spaces to look at next)


    #finds the neighbors around a space (excluding self)
    def neighbors(self, r, c):
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    yield nr, nc


    #adds numbered spaces to solver's knowledge base
    def add_observation(self, r, c, number, defer_update=False):
        if (r, c) in self.opened:
            return
        
        self.opened.add((r, c))

        self.solver.add(self.mine[r][c] == False)

        if number == 0:
            return

        neighbor_exprs = [If(self.mine[nr][nc], 1, 0) for nr, nc in self.neighbor_sets[(r, c)]]
        self.solver.add(Sum(neighbor_exprs) == number)

        for nr, nc in self.neighbor_sets[(r, c)]:
            if (nr, nc) not in self.opened and (nr, nc) not in self.flags:
                self.frontier.add((nr, nc))

        self.frontier.discard((r, c))

        self.cache_safe.clear()
        self.cache_mine.clear()

        if not defer_update:
            self.update_flags_deterministic()


    # checks spaces that are unknown neighbors of frontier spaces (spaces next to numbered spaces)
    # assume the space is safe and prove by contridiction if the space is safe or not
    # updates the z3 solver with information about the space
    def update_flags_deterministic(self):
        if self.frontier:
            candidates = list(self.frontier)
        else:
            candidates = [(r, c) for r in range(self.rows) for c in range(self.cols)        #checking unknown spaces if frontier is empty
                          if (r, c) not in self.opened and (r, c) not in self.flags]

        newly_flagged = set()


        #see if each candidate space is a mine or not
        for (r, c) in candidates:
            if (r, c) in self.opened or (r, c) in self.flags:
                continue

            key = (r, c)
            if key not in self.cache_mine:
                self.solver.push()
                self.solver.add(self.mine[r][c] == False)
                self.cache_mine[key] = (self.solver.check() == unsat)
                self.solver.pop()

            if self.cache_mine[key]:
                newly_flagged.add((r, c))

        if newly_flagged:
            for (r, c) in newly_flagged:
                self.flags.add((r, c))
                self.solver.add(self.mine[r][c] == True)
                self.frontier.discard((r, c))

            self.cache_safe.clear()
            self.cache_mine.clear()


    #based on the solver's logic determining a space to be safe,
    #make that move on the board
    def make_safe_move(self):
        self.update_flags_deterministic()

        frontier_list = list(self.frontier)

        for (r, c) in frontier_list:
            if (r, c) in self.opened or (r, c) in self.flags:
                continue

            key = (r, c)
            if key not in self.cache_safe:
                self.solver.push()
                self.solver.add(self.mine[r][c] == True)
                self.cache_safe[key] = (self.solver.check() == unsat)
                self.solver.pop()

            if self.cache_safe[key]:
                self.frontier.discard((r, c))
                return (r, c)

        for r in range(self.rows):
            for c in range(self.cols):
                if (r, c) in self.opened or (r, c) in self.flags:
                    continue

                key = (r, c)
                if key not in self.cache_safe:
                    self.solver.push()
                    self.solver.add(self.mine[r][c] == True)
                    self.cache_safe[key] = (self.solver.check() == unsat)
                    self.solver.pop()

                if self.cache_safe[key]:
                    return (r, c)

        return None

    #if no real moves are available, the AI MUST make a choice based on probability
    def make_random_move(self):
        self.update_flags_deterministic()

        candidates = list(self.frontier) + [
            (r, c)
            for r in range(self.rows)
            for c in range(self.cols)
            if (r, c) not in self.opened and (r, c) not in self.flags
        ]

        for (r, c) in candidates:
            if (r, c) in self.opened or (r, c) in self.flags:
                continue

            self.solver.push()
            self.solver.add(self.mine[r][c] == False)
            res = self.solver.check()
            self.solver.pop()

            if res == sat:
                return (r, c)

        return None


    def get_flags(self):
        return set(self.flags)


    def reset(self):
        self.__init__(self.rows, self.cols)
