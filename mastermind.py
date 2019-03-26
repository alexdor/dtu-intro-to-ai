import itertools
from random import choices, randint

import numpy as np

space_size = 1296
# make the game
class Mastermind:
    # initialize the variables
    def __init__(self):
        self.colors = [1, 2, 3, 4, 5, 6]
        self.set = itertools.permutations(self.colors, 4)
        self.goal = choices(self.colors, k=4)
        self.turn_counter = 0
        self.win = False

    # calculate the black/white pegs for a guess
    def guess(self, combination, goal):
        temp_goal = goal[:]
        black = 0
        for i in range(len(temp_goal)):
            if combination[i] == temp_goal[i]:
                black += 1
        correct_colors = 0
        matched_combo = [0] * 4
        matched_goal = [0] * 4
        for m in range(4):
            for n in range(4):
                if (
                    (temp_goal[n] == combination[m])
                    and (matched_goal[n] == 0)
                    and (matched_combo[m] == 0)
                ):
                    correct_colors += 1
                    matched_goal[n] += 1
                    matched_combo[m] += 1
        # black pegs count into the correct colors calculation
        # so we just subtract the 2 to find white
        white = correct_colors - black
        answer = []
        answer += list(itertools.repeat("B", black))
        answer += list(itertools.repeat("W", white))
        answer += list(itertools.repeat("nope", 4 - len(answer)))
        self.turn_counter += 1
        # check for a win after each guess
        if answer == ["B", "B", "B", "B"]:
            self.win = True
        return answer


# GAME SOLVING FUNCTIONS STARTING HERE

# perform minimax algorithm to dataset
def do_minimax(array):
    var_list_2 = [10000] * space_size
    for j in range(space_size):  # index j corresponds to unused data set
        if array[5, j] == 1:
            var_list_1 = [0] * 14  # there are 14 possible answers to a code
            for i in range(
                space_size
            ):  # index i corresponds to possible solution data set
                combination = array[0:4, i]
                if array[4, i] == 1:
                    temp_goal = array[0:4, j]
                    black = 0
                    for k in range(len(temp_goal)):
                        if array[k, i] == temp_goal[k]:
                            black += 1
                    correct_colors = 0
                    matched_combo = [0] * 4
                    matched_goal = [0] * 4
                    for m in range(4):
                        for n in range(4):
                            if (
                                (temp_goal[n] == combination[m])
                                and (matched_goal[n] == 0)
                                and (matched_combo[m] == 0)
                            ):
                                correct_colors += 1
                                matched_goal[n] += 1
                                matched_combo[m] += 1
                    # black pegs count into the correct colors calculation
                    # so we just subtract the 2 to find white
                    white = correct_colors - black

                    # calculation of remaining combinations
                    if (white == 0) and (black == 4):
                        var_list_1[0] += 1
                    elif (white == 0) and (black == 3):
                        var_list_1[1] += 1
                    elif (white == 2) and (black == 2):
                        var_list_1[2] += 1
                    elif (white == 1) and (black == 2):
                        var_list_1[3] += 1
                    elif (white == 0) and (black == 2):
                        var_list_1[4] += 1
                    elif (white == 3) and (black == 1):
                        var_list_1[5] += 1
                    elif (white == 2) and (black == 1):
                        var_list_1[6] += 1
                    elif (white == 1) and (black == 1):
                        var_list_1[7] += 1
                    elif (white == 0) and (black == 1):
                        var_list_1[8] += 1
                    elif (white == 4) and (black == 0):
                        var_list_1[9] += 1
                    elif (white == 3) and (black == 0):
                        var_list_1[10] += 1
                    elif (white == 2) and (black == 0):
                        var_list_1[11] += 1
                    elif (white == 1) and (black == 0):
                        var_list_1[12] += 1
                    elif (white == 0) and (black == 0):
                        var_list_1[13] += 1

            var_list_2[j] = max(var_list_1)
    print("Worst case scenario:", min(var_list_2), "options after this round.")
    return array[0:4, np.argmin(var_list_2)]


# update possible solution dataset array based on code and code response (ground_truth)
def update_solutions_dataset(array, tested_code, ground_truth):
    # read number of black and white pegs
    ground_truth_white = ground_truth.count("W")
    ground_truth_black = ground_truth.count("B")

    # determine black and white pegs for all codes
    for i in range(space_size):
        combination = array[0:4, i]
        black = 0
        for k in range(len(tested_code)):
            if array[k, i] == tested_code[k]:
                black += 1
        correct_colors = 0
        matched_combo = [0] * 4
        matched_tested_code = [0] * 4
        for m in range(4):
            for n in range(4):
                if (
                    (tested_code[n] == combination[m])
                    and (matched_tested_code[n] == 0)
                    and (matched_combo[m] == 0)
                ):
                    correct_colors += 1
                    matched_tested_code[n] += 1
                    matched_combo[m] += 1
        # black pegs count into the correct colors calculation
        # so we just subtract the 2 to find white
        white = correct_colors - black
        # set cell to 0 if solution is incompatible with last feedback (black/white combination)
        if (ground_truth_white != white) or (ground_truth_black != black):
            array[4, i] = 0  # 0 means code is not part of solution set anymore


# disable used code in dataset array
def update_dataset(array, code):
    for i in range(space_size):
        if (
            (array[0, i] == code[0])
            and (array[1, i] == code[1])
            and (array[2, i] == code[2])
            and (array[3, i] == code[3])
        ):
            array[4, i] = 0  # 0 means code is not part of solution set anymore
            array[5, i] = 0  # 0 means code is not part of unused set anymore


# initialize array with all possible combinations and information if part of solution set and information if part of unused set
number_set = np.empty(dtype=int, shape=[6, space_size])
i = 0
for a in range(1, 7):
    for b in range(1, 7):
        for c in range(1, 7):
            for d in range(1, 7):
                number_set[0, i] = a
                number_set[1, i] = b
                number_set[2, i] = c
                number_set[3, i] = d
                number_set[4, i] = 1  # 1 means code is part of solution set
                number_set[5, i] = 1  # 1 means code is part of unused set
                i += 1

# initialize the game
game = Mastermind()

# initial guess
combo = np.array([2, 2, 4, 5])

# start the turn clock, check for a win after each round
while game.turn_counter <= 50 and not game.win:
    # requires a string of ex. "1 1 1 1" to parse correctly.
    print("Give me a combination of the elements 1,2,3,4,5,6. Ya fucking idiot.")
    # combo=input("1 line, 4 numbers, 3 spaces. It'll break if you don't do that exactly.").split()
    combo = list(map(int, combo))
    print(combo)
    # check if the guess is the valid format
    # don't uptick the turn counter for an invalid format
    # i'm not that big of an asshole
    if len(combo) != 4 or set(combo).issubset(game.colors) != True:
        print(
            "Invalid guess, moron. Make sure you're guessing four items from the list (e.g. '5 5 4 3')"
        )
        continue
    print(game.guess(combo, game.goal))
    print("goal is " + str(game.goal))

    update_solutions_dataset(number_set, combo, game.guess(combo, game.goal))
    # calculate number of solutions in the solution data set:
    m = 0
    for k in range(space_size):
        if number_set[4, k] == 1:
            m += 1
            buffer = k
    # check if there is only one element left in the solution data set:
    if m == 1:
        combo = number_set[0:4, buffer]
    else:
        update_dataset(number_set, combo)
        combo = do_minimax(number_set)
# if we leave that game loop, print the win/loss statement
if game.win:
    print("I guess that was a pretty good game. I guess.")
else:
    print("Haha, loser.")
