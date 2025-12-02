#using the Z3 solver for predicate logic
#   USE: pip3 install z3-solver

from z3 import *
#from board import Minesweeper #code from the otherminesweeper folder




from z3 import *

class MinesweeperAI:
    def __init__(self, height, width):
        self.rows = height
        self.cols = width

        self.solver = Solver()
        self.mine = [[Bool(f"m_{r}_{c}") for c in range(self.cols)] for r in range(self.rows)]

        self.opened = set()
        self.flags = set()
        self.observed = set()

        self.cache_safe = {}
        self.cache_mine = {}

        self.neighbor_sets = {
            (r, c): list(self._neighbors(r, c))
            for r in range(self.rows)
            for c in range(self.cols)
        }

        self.frontier = set()
        self._add_static_rules()

    def _neighbors(self, r, c):
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    yield nr, nc

    def _add_static_rules(self):
        for r in range(self.rows):
            for c in range(self.cols):
                self.solver.add(Or(self.mine[r][c], Not(self.mine[r][c])))

    def add_observation(self, r, c, number, defer_update=False):
        if (r, c) in self.observed:
            return

        self.observed.add((r, c))
        self.opened.add((r, c))
        self.solver.add(self.mine[r][c] == False)

        neighbor_exprs = [If(self.mine[nr][nc], 1, 0) for nr, nc in self.neighbor_sets[(r, c)]]
        self.solver.add(Sum(neighbor_exprs) == number)

        self.cache_safe.clear()
        self.cache_mine.clear()

        for nr, nc in self.neighbor_sets[(r, c)]:
            if (nr, nc) not in self.opened and (nr, nc) not in self.flags:
                self.frontier.add((nr, nc))

        self.frontier.discard((r, c))

        if not defer_update:
            self._update_flags_deterministic()

    def process_frontier(self):
        if self.frontier:
            self._update_flags_deterministic()

    def _update_flags_deterministic(self):
        if self.frontier:
            candidates = list(self.frontier)
        else:
            candidates = [(r, c) for r in range(self.rows) for c in range(self.cols)
                          if (r, c) not in self.opened and (r, c) not in self.flags]

        newly_flagged = set()

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

    def make_safe_move(self):
        self._update_flags_deterministic()

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

    def make_random_move(self):
        self._update_flags_deterministic()

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








# from z3 import *
# from board import Minesweeper

# class MinesweeperAI:
#     def __init__(self, height, width):
#         self.rows = height
#         self.cols = width

#         # Z3 solver
#         self.solver = Solver()

#         # Boolean mine variables
#         self.mine = [[Bool(f"m_{r}_{c}") for c in range(self.cols)]
#                      for r in range(self.rows)]

#         # bookkeeping
#         self.opened = set()
#         self.flags = set()
#         self.observed = set()
#         self.cache_safe = {}
#         self.cache_mine = {}

#         # Precompute neighbors
#         self.neighbor_sets = {
#             (r, c): list(self.neighbors(r, c))
#             for r in range(self.rows)
#             for c in range(self.cols)
#         }

#         # frontier: cells adjacent to revealed cells that are candidates for checks
#         self.frontier = set()        # (r,c) pairs to consider in deterministic updates

#         self._add_static_rules()

#     # ---------- helpers ----------
#     def neighbors(self, r, c):
#         for dr in [-1, 0, 1]:
#             for dc in [-1, 0, 1]:
#                 if dr == 0 and dc == 0:
#                     continue
#                 nr, nc = r + dr, c + dc
#                 if 0 <= nr < self.rows and 0 <= nc < self.cols:
#                     yield nr, nc

#     def _add_static_rules(self):
#         for r in range(self.rows):
#             for c in range(self.cols):
#                 # explicit domain assertion (redundant for Bool, but harmless)
#                 self.solver.add(Or(self.mine[r][c], Not(self.mine[r][c])))

#     # ---------- observations ----------
#     def add_observation(self, r, c, number, defer_update=False):
#         """
#         Add a revealed cell observation.
#         If defer_update is True, the AI will not run deterministic updates now.
#         Use this during flood-fill for many cells, then call process_frontier().
#         """
#         if (r, c) in self.observed:
#             return

#         self.observed.add((r, c))
#         self.opened.add((r, c))

#         # Mark cell safe
#         self.solver.add(self.mine[r][c] == False)

#         # Add the neighbor-sum constraint (no separate hint variables)
#         neighbor_exprs = [
#             If(self.mine[nr][nc], 1, 0)
#             for nr, nc in self.neighbor_sets[(r, c)]
#         ]
#         self.solver.add(Sum(neighbor_exprs) == number)

#         # Clear caches because KB changed
#         self.cache_safe.clear()
#         self.cache_mine.clear()

#         # Add adjacent unknown neighbors to frontier for later checking
#         for nr, nc in self.neighbor_sets[(r, c)]:
#             if (nr, nc) not in self.opened and (nr, nc) not in self.flags:
#                 self.frontier.add((nr, nc))

#         # Remove the revealed cell from frontier (if present)
#         self.frontier.discard((r, c))

#         if not defer_update:
#             # run deterministic discovery now
#             self._update_flags_deterministic()

#     def process_frontier(self):
#         """
#         Run deterministic flag discovery only on the frontier.
#         Useful after adding many observations with defer_update=True.
#         """
#         # if frontier is empty nothing to do
#         if not self.frontier:
#             return

#         # run the deterministic update (only checks frontier)
#         self._update_flags_deterministic()

#     # ---------- detect guaranteed mines ----------
#     def _update_flags_deterministic(self):
#         """
#         Only checks cells in self.frontier (and if frontier empty, fallback to scanning whole board).
#         If a cell must be a mine (assuming safe => UNSAT), mark it and add constraint.
#         """
#         # Work on a snapshot of the frontier to avoid mutation during iteration
#         if self.frontier:
#             candidates = list(self.frontier)
#         else:
#             # fallback minimal scan: check all unknowns (rare)
#             candidates = [(r, c) for r in range(self.rows) for c in range(self.cols)
#                           if (r, c) not in self.opened and (r, c) not in self.flags]

#         newly_flagged = set()

#         for (r, c) in candidates:
#             # skip if it became opened/flagged in the meantime
#             if (r, c) in self.opened or (r, c) in self.flags:
#                 continue

#             key = (r, c)
#             if key in self.cache_mine:
#                 must_be_mine = self.cache_mine[key]
#             else:
#                 # If assuming safe (mine==False) is inconsistent -> must be mine
#                 self.solver.push()
#                 self.solver.add(self.mine[r][c] == False)
#                 res = self.solver.check()
#                 self.solver.pop()
#                 must_be_mine = (res == unsat)
#                 self.cache_mine[key] = must_be_mine

#             if must_be_mine:
#                 newly_flagged.add((r, c))

#         # Apply all newly flagged at once (minimizes repeated solver churn)
#         if newly_flagged:
#             for cell in newly_flagged:
#                 self.flags.add(cell)
#                 self.solver.add(self.mine[cell[0]][cell[1]] == True)
#                 # once flagged, remove from frontier
#                 self.frontier.discard(cell)

#             # after adding new facts, cache must be cleared
#             self.cache_safe.clear()
#             self.cache_mine.clear()

#     # ---------- guaranteed safe move ----------
#     def make_safe_move(self):
#         """
#         Return a guaranteed-safe coordinate (r,c) or None.
#         Prioritizes frontier candidates first for speed.
#         """
#         # ensure flags are updated for current frontier
#         self._update_flags_deterministic()

#         # First check frontier for guaranteed-safe cells
#         frontier_candidates = list(self.frontier) if self.frontier else []
#         for (r, c) in frontier_candidates:
#             if (r, c) in self.opened or (r, c) in self.flags:
#                 continue
#             key = (r, c)
#             if key in self.cache_safe:
#                 must_be_safe = self.cache_safe[key]
#             else:
#                 self.solver.push()
#                 self.solver.add(self.mine[r][c] == True)
#                 res = self.solver.check()
#                 self.solver.pop()
#                 must_be_safe = (res == unsat)
#                 self.cache_safe[key] = must_be_safe

#             if must_be_safe:
#                 # remove from frontier since we're about to open it
#                 self.frontier.discard((r, c))
#                 return (r, c)

#         # Fallback: scan all unknown cells (rare and slower)
#         for r in range(self.rows):
#             for c in range(self.cols):
#                 if (r, c) in self.opened or (r, c) in self.flags:
#                     continue
#                 key = (r, c)
#                 if key in self.cache_safe:
#                     must_be_safe = self.cache_safe[key]
#                 else:
#                     self.solver.push()
#                     self.solver.add(self.mine[r][c] == True)
#                     res = self.solver.check()
#                     self.solver.pop()
#                     must_be_safe = (res == unsat)
#                     self.cache_safe[key] = must_be_safe

#                 if must_be_safe:
#                     return (r, c)

#         return None

#     # ---------- fallback guess ----------
#     def make_random_move(self):
#         # ensure deterministic flags are updated first
#         self._update_flags_deterministic()

#         # Prefer frontier cells as guesses (they are informative)
#         for (r, c) in list(self.frontier) + [
#             (r, c) for r in range(self.rows) for c in range(self.cols)
#             if (r, c) not in self.opened and (r, c) not in self.flags
#         ]:
#             if (r, c) in self.opened or (r, c) in self.flags:
#                 continue

#             # quick satisfiability test: is (r,c) possibly safe?
#             self.solver.push()
#             self.solver.add(self.mine[r][c] == False)
#             res = self.solver.check()
#             self.solver.pop()

#             if res == sat:
#                 return (r, c)

#         return None

#     def get_flags(self):
#         return set(self.flags)

#     def reset(self):
#         # reinitialize cleanly
#         self.__init__(self.rows, self.cols)



























# from z3 import *
# #from minesweeper import Minesweeper     #needs the .vscode settings.json file for the import because why not
# from board import Minesweeper       #code from the otherminesweeper folder


# class minesweeperAI:

#     def __init__(self, height, width):
#         self.rows = height
#         self.cols = width

#         #build knowledge base
#         self.solver = Solver()

#         #add rules of minesweeper to the KB




#     # return ("safe", (row, col))
#     # return ("mine", (row, col))   # to flag it
#     # return ("guess", (row, col))  # if probability moves required

#     #move that is guarenteed to not be a mine
#     def make_safe_move(self):
#         # determine if a move is safe using predicate logic 
#         pass

#     #if there is a chance for a mine, pick the square with the least probability of being a mine
#     def make_random_move(self):
#         pass

#         #finds neighbors all around a space
#     def neighbors(self, r, c):
#         for dr in [-1,0,1]:
#             for dc in [-1,0,1]:
#                 if dr == 0 and dc == 0: 
#                     continue
#                 nr, nc = r+dr, c+dc
#                 if 0 <= nr < R and 0 <= nc < C:
#                     yield nr, nc

    
#     mineSweeperBoard = [[Bool(f"X_{i}_{j}") for j in range(self.cols)] for i in range(self.rows)]  # True = mine, False = clear


