from checker import *

"""
Represent an 8x8 checkers board
"""

class Board:
    def __init__(self):
        self.state = [None] * 8 # board state is an 2D array (8x8) of constants from constants.py
        for i in range(0, 8):
            self.state[i] = [None] * 8

        # here, an upper-case g or or r (G, R) may be used to represent kings
        # green and red were chosen because g and G and r and R are easier to distinguish
        # than b and B and w and W.  Everywhere else, only the G and R representations are used.
        starting_config = [
            [0, g, 0, g, 0, g, 0, g],
            [g, 0, g, 0, g, 0, g, 0],
            [0, g, 0, g, 0, g, 0, g],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [r, 0, r, 0, r, 0, r, 0],
            [0, r, 0, r, 0, r, 0, r],
            [r, 0, r, 0, r, 0, r, 0]
        ]
        self.set_state(starting_config)

    # set the board state from an input configuration a la starting configuration on line 16
    def set_state(self, config):
        for i in range(0, 8):
            for j in range(0, 8):
                if config[i][j] > 0:
                    alliance = G if config[i][j] == g or config[i][j] == G else R
                    is_king = config[i][j] == G or config[i][j] == R
                    self.state[i][j] = Checker(self, alliance, is_king, i, j)
                else:
                    self.state[i][j] = None

    def get_checker(self, pos):
        if not self.on_board(pos):
            return -1
        row, col = pos
        return self.state[row][col]

    def set_checker(self, pos, checker): # place the specified checker at the specified square
        row, col = pos
        self.state[row][col] = checker

    def on_board(self, pos): # return true if (row, col) is a valid position on the board
        row, col = pos
        return (0 <= row < 8) and (0 <= col < 8)

    # encode the board for use as input to the network
    def get_network_encoding(self):
        red_arr = []
        green_arr = []
        attacked_by_green = self.attacking(G)
        attacked_by_red = self.attacking(R)
        for i in range(0, 8):
            for j in range(0, 8):
                if self.state[i][j] is None: # empty square are all 0s
                    red_arr += [0.0, 0.0, 0.0, 0.0]
                    green_arr += [0.0, 0.0, 0.0, 0.0]
                elif self.state[i][j].alliance == R: # red squares will be [1.0, x, x, x]
                    red_arr += self.encode_space(i, j, attacked_by_green, attacked_by_red)
                    green_arr += [0.0, 0.0, 0.0, 0.0]
                elif self.state[i][j].alliance == G: # green squares will also be [1.0, x, x, x]
                    red_arr += [0.0, 0.0, 0.0, 0.0]
                    green_arr += self.encode_space(i, j, attacked_by_green, attacked_by_red)
        return green_arr + red_arr # total encoding is concaenation of red and green encodings

    def encode_space(self, row, col, attacked_by_green, attacked_by_red):
        encoding = [0.0, 0.0, 0.0, 0.0]
        checker = self.state[row][col]
        if checker is not None:
            encoding[0] = 1.0
            # the checker is safe
            if checker.alliance == R and checker not in attacked_by_green: # checker is not attacked (ie is safe)
                encoding[1] = 1.0
            elif checker.alliance == G and checker not in attacked_by_red: # ditto
                encoding[1] = 1.0
            if checker.is_defended(): # checker is defended by an ally (or on a corner)
                encoding[2] = 1.0
            if checker.is_king: # checker is a king
                encoding[3] = 1.0
        return encoding

    # unused function to count total number of kings on the board
    def count_kings(self, alliance):
        king_num
        for i in range(0, 8):
            for j in range(0, 8):
                checker = self.state[i][j]
                if checker is not None and checker.alliance == alliance:
                    king_num += 1
        return king_num

    # return a set of all checkers that are presently being "attacked" (are directly adjacent to)
    # a threatening checker of the specified alliance.  A piece is only considered attacked if it is
    # adjacent to an enemy piece and could be captured in a single legal atomic move if it was undefended.
    def attacking(self, alliance):
        attacked = set()
        legal_moves = self.get_legal_moves(alliance)
        for move_seq in legal_moves:
            for atomic_move in move_seq:
                if atomic_move.victim is not None:
                    attacked.add(atomic_move.victim)
        return attacked

    # G's enemy is R.  R's enemy is G.
    def get_enemy(self, alliance):
        if alliance == G:
            return R
        else:
            return G

    # get all legal moves for all checkers of the specified alliance
    def get_legal_moves(self, alliance):
        legal_moves = []
        for i in range(0, 8):
            for j in range(0, 8):
                checker = self.state[i][j]
                if checker is not None and checker.alliance == alliance:
                    legal_moves += checker.get_legal_moves()
        random.shuffle(legal_moves) # shuffle legal moves to prevent geographic bias
        return legal_moves

    # adapted from Wikipedia pseudo-code
    # Green is max agent.  Red is min agent.
    def ab_prune(self, depth, player, network, a=-float("inf"), b=float("inf")):
        legal_moves = self.get_legal_moves(player)
        if depth == 0 or len(legal_moves) == 0:
            network.set_input(self.get_network_encoding())
            output = network.get_output()[0]
            return output
        if player == G: # max agent
            value = -float("inf")
            for move_seq in legal_moves:
                for atomic_move in move_seq:
                    atomic_move.make()
                value = max(value, self.ab_prune(depth - 1, R, network, a, b))
                for i in range(len(move_seq) - 1, -1, -1):
                    move_seq[i].undo()
                a = max(a, value)
                if b <= a:
                    break
            return value
        else:
            value = float("inf")
            for move_seq in legal_moves:
                for atomic_move in move_seq:
                    atomic_move.make()
                value = min(value, self.ab_prune(depth - 1, G, network, a, b))
                for i in range(len(move_seq) - 1, -1, -1):
                    move_seq[i].undo()
                b = min(b, value)
                if b <= a:
                    break
            return value

    # get the value of all depth 1 moves by iterating deeper using ab_prune, and pick the one that yields
    # the best board state (green) or the worst (red)
    def get_best_move_ab(self, depth, player, network):
        legal_moves = self.get_legal_moves(player)
        best_move = None
        if player == G:
            best_move_val = -float("inf")
        else:
            best_move_val = float("inf")
        for move_seq in legal_moves:
            for atomic_move in move_seq:
                atomic_move.make()
            network.set_input(self.get_network_encoding())
            value = self.ab_prune(depth - 1, self.get_enemy(player), network)
            if player == G and value >= best_move_val:
                best_move_val = value
                best_move = move_seq
            elif player == R and value <= best_move_val:
                best_move_val = value
                best_move = move_seq
            for i in range(len(move_seq) - 1, -1, -1):
                move_seq[i].undo()
        return best_move

    # another unused summary function, this time to get the total count of pieces on the board
    def get_piece_count(self, alliance):
        count = 0
        for i in range(0, 8):
            for j in range(0, 8):
                checker = self.state[i][j]
                if checker is not None and checker.alliance == alliance:
                    #print "COOL"
                    count += 1
        return count

    # pick of a move directly from the network, move randomly with probability eps
    def get_move_from_network(self, network, alliance, eps=0.05):
        legal_moves = self.get_legal_moves(alliance)
        if len(legal_moves) > 0:
            if random.random() < eps:
                return random.choice(legal_moves)
            else:
                if alliance == G:
                    best_output = -float("inf")
                elif alliance == R:
                    best_output = float("inf")
                best_move = None
                for move_seq in legal_moves:
                    for i in range(0, len(move_seq)):
                        move_seq[i].make()
                    network.set_input(self.get_network_encoding())
                    output = network.get_output()
                    print output
                    output = output[0]
                    if (output >= best_output and alliance == G) or (output <= best_output and alliance == R):
                        best_output = output
                        best_move = move_seq
                    for i in range(len(move_seq) - 1, -1, -1):
                        move_seq[i].undo()
                return best_move
        else:
            return None

    def __str__(self):
        str = ""
        for i in range(0, 8):
            for j in range(0, 8):
                checker = self.state[i][j]
                if checker is not None:
                    if checker.alliance == G:
                        if checker.is_king:
                            str += " G "
                        else:
                            str += " g "
                    elif checker.alliance == R:
                        if checker.is_king:
                            str += " R "
                        else:
                            str += " r "
                else:
                    str += " - "
            str += "\n"
        return str
