from constants import *
from atomic_move import *
from network import *

class Checker:
    def __init__(self, board, alliance, is_king, row, col):
        self.board = board
        self.alliance = alliance # R or G
        self.is_king = is_king
        self.row = row
        self.col = col

        self.dir = 1 # green moves forward
        if self.alliance == R: # red moves backward
            self.dir = -1

    def get_pos(self):
        return (self.row, self.col) # convert row and col to tuple

    def set_pos(self, pos):
        self.row, self.col = pos

    def get_adjacent_squares(self): # return all adjacent diagonals
        diags = []
        if 0 <= self.row + self.dir < 8:
            if self.col + 1 < 8:
                diags.append((self.row + self.dir, self.col + 1))
            if self.col - 1 >= 0:
                diags.append((self.row + self.dir, self.col - 1))
        if 0 <= self.row - self.dir < 8:
            if self.col + 1 < 8:
                diags.append((self.row - self.dir, self.col + 1))
            if self.col - 1 >= 0:
                diags.append((self.row - self.dir, self.col - 1))
        return diags

    # recursively generate all legal jumps
    def generate_jumps(self, all_possible_jump_seqs, curr_list=[]):
        diags = self.get_adjacent_squares()
        jump_candidates = []
        for pos in diags:
            other = self.board.get_checker(pos)
            if self.is_enemy(other):
                enemy_row, enemy_col = pos
                if enemy_row - self.row == self.dir or self.is_king:
                    row_dir = enemy_row - self.row
                    col_dir = enemy_col - self.col
                    dest_row = enemy_row + row_dir
                    dest_col = enemy_col + col_dir
                    if self.board.get_checker((dest_row, dest_col)) is None:
                        move = AtomicMove(self.board, self, self.get_pos(), (dest_row, dest_col), other)
                        jump_candidates.append(move)
        for jump in jump_candidates:
            new_list = curr_list + [jump]
            all_possible_jump_seqs.append(new_list)
            jump.make()
            self.generate_jumps(all_possible_jump_seqs, new_list)
            jump.undo()

    # decorator for generate_jumps to turn it into a getter
    def get_jumps(self):
        all_possible_jump_seqs = []
        self.generate_jumps(all_possible_jump_seqs)
        return all_possible_jump_seqs

    # get all legal moves JUST FOR THIS CHECKER, including standard diagonals and jumps
    def get_legal_moves(self):
        legal_moves = self.get_jumps()
        diags = self.get_adjacent_squares()
        for pos in diags:
            other = self.board.get_checker(pos)
            row, col = pos
            if (other is None) and (row - self.row == self.dir or self.is_king):
                move = AtomicMove(self.board, self, self.get_pos(), pos)
                legal_moves.append([move])
        return legal_moves

    # return true if the checker is defended by an ally or is on a corner
    # a defended checker is not necessarily safe because non-edge checkers can be
    # captured on two diagonals (edge checkers cannot be captured at all)
    def is_defended(self):
        defended = False
        if self.row == 0 or self.row == 7 or self.col == 0 or self.col == 7:
            defended = True

        diags = self.get_adjacent_squares()
        for pos in diags:
            other = self.board.get_checker(pos)
            if (other is not None and other.alliance == self.alliance) and (self.row - other.row == self.dir or other.is_king):
                defended = True

        return defended
        
    def is_enemy(self, other):
        if other is not None and other.alliance != self.alliance:
            return True
        else:
            return False

    def __str__(self):
        return str((self.row, self.col))

    def __repr__(self):
        return self.__str__()
