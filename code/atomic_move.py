from constants import *

"""
Represent a single action, either a slide diagonal or a jump.  An entire move
may be a composition of single actions (a series of jumps).
"""

class AtomicMove:
    def __init__(self, board, checker, start, end, victim=None):
        self.board = board
        self.checker = checker
        self.start = (checker.row, checker.col) # start position of the piece
        self.is_king_at_start = self.checker.is_king # is the piece a king before the move?
        self.end = end # end position of the piece
        self.victim = victim # If the move results in a capture, put it here!

    # make a single move
    def make(self):
        self.board.set_checker(self.start, None)
        self.board.set_checker(self.end, self.checker)
        self.checker.set_pos(self.end)
        # green pieces become kings when the reach row 7, and red pieces become kinds
        # when they reach row 0
        if self.checker.alliance == G and self.end[0] == 7 or \
        self.checker.alliance == R and self.end[0] == 0:
            self.checker.is_king = True
        if self.victim is not None: # this is a jump
            self.board.set_checker(self.victim.get_pos(), None) # remove the jumped checker from the board

    # completely undo the single move
    # moves can only be undone in the reverse of the order in which they were made
    def undo(self):
        self.board.set_checker(self.start, self.checker)
        self.checker.set_pos(self.start)
        self.checker.is_king = self.is_king_at_start
        self.board.set_checker(self.end, None)
        if self.victim is not None:
            self.board.set_checker(self.victim.get_pos(), self.victim) # restore victim to the board

    def __str__(self):
        return "%s --> %s" % (self.start, self.end)

    def __repr__(self):
        return self.__str__()
