from board import *
import sys

"""
Run experiments using networks generated in train.py
"""

# match between network 1 and network 2 and depth 1 and depth 2 respectively (random moves for both networks with
# probability epsilon).  If the network isn't specified, random moves are used instead
def match(snw1=None, depth1=None, snw2=None, depth2=None, eps=0.05):
    board = Board()
    if snw1 is not None:
        nw1 = Network([])
        nw1.load("round_%s" % snw1)
    else:
        nw1 = "nw1"
    if snw2 is not None:
        nw2 = Network([])
        nw2.load("round_%s" % snw2)
    else:
        nw2 = "nw2"

    red_random = False
    green_random = False
    if random.random() < 0.5:
        red_network = nw1
        red_depth = depth1
        green_network = nw2
        green_depth = depth2
    else:
        red_network = nw2
        red_depth = depth2
        green_network = nw1
        green_depth = depth1

    # full disclosure, accidentally left this in during data generation,
    # may have had a small impact
    # eps = 0.05
    curr_player = G
    while True:
        if curr_player == G:
            res = move_helper(green_depth, G, green_network, board, eps)
            curr_player = R
            if not res:
                if green_network == nw1:
                    # Network 2 wins!
                    return 1
                else:
                    # Network 1 wins!
                    return 0
                break
        elif curr_player == R:
            res = move_helper(red_depth, R, red_network, board, eps)
            curr_player = G
            if not res:
                if red_network == nw1:
                    # Network 2 wins!
                    return 1
                else:
                    # Network 1 wins!
                    return 0
                break

def move_helper(depth, alliance, network, board, eps):
    if random.random() < eps or type(network) == str:
        legal_moves = board.get_legal_moves(alliance)
        if len(legal_moves) == 0:
            return False
        else:
            make_move_seq(random.choice(legal_moves))
            return True
    else:
        move_seq = board.get_best_move_ab(depth, alliance, network)
        if move_seq is None:
            return False
        else:
            make_move_seq(move_seq)
            return True

def resolve_name(alliance):
    if alliance == G:
        return "Green"
    else:
        return "Red"

def make_move_seq(move_seq):
    for atomic_move in move_seq:
        atomic_move.make()

# conduct the experiment summarized in Table 1 of the report
# that is, play different generations of the network against a random baseline
def go_random():
    gens = [0, 1, 1000, 5000, 10000, 20000, 30000, 40000, 50000] # network generations to use (really iterations)
    res_table = {}
    for gen in gens:
        print "GENERATION %i" % gen
        for d in range(1, 4):
            print "DEPTH %i" % d
            random_wins = 0
            nw_wins = 0
            for i in range(0, 10):
                winner = match(snw1=str(gen), depth1=d, eps=0)
                if winner == 0:
                    nw_wins += 1
                else:
                    random_wins += 1
            print "NW: %i, RD: %i" % (nw_wins, random_wins)
        print "\n"

# conduct the report summarized in Table 2 of the report
# that is, play the network against different versions of itself
def go_self():
    gens = [0, 1, 1000, 5000, 10000, 20000, 30000, 40000, 50000] # network generations to use (really iterations)
    for i in range(0, len(gens)):
        for j in range(i, len(gens)):
            i_wins = 0
            for x in range(0, 10):
                winner = match(str(gens[i]), 1, str(gens[j]), 1, 0.05)
                if winner == 0:
                    i_wins += 1
            print "%i: %i | %i: %i" % (gens[i], i_wins, gens[j], 10 - i_wins)


def main():
    if sys.argv[1] == "self":
        go_self()
    elif sys.argv[1] == "random":
        go_random()
    else:
        print "invalid command, woops"

main()
