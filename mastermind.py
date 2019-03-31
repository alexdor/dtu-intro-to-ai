import itertools
from random import choices, randint
import json
import numpy as np

from timeit import default_timer as timer
space_size = 1296
colors = [1, 2, 3, 4, 5, 6]
# make the game
class Mastermind:
    # initialize the variables
    def __init__(self, goal):
        self.colors = colors
        self.set = itertools.permutations(self.colors, 4)
        self.goal = goal
        self.turn_counter = 0
        self.win = False
        self.space_size = space_size

    def get_white_and_black(self, combination, tested_code):
        black = sum(
            1
            for index in range(len(tested_code))
            if combination[index] == tested_code[index]
        )
        correct_colors = 0

        tmp = combination.tolist()
        for i in range(4):
            if tested_code[i] in tmp:
                correct_colors += 1
                tmp.remove(tested_code[i])

        return correct_colors - black, black

    # calculate the black/white pegs for a guess
    def guess(self, combination, goal):
        white, black = self.get_white_and_black(combination, goal)
        answer = []
        answer += itertools.repeat("B", black)
        answer += itertools.repeat("W", white)
        answer += itertools.repeat("nope", 4 - black - white)
        self.turn_counter += 1
        # check for a win after each guess
        if answer == ["B", "B", "B", "B"]:
            self.win = True
        return answer

    # GAME SOLVING FUNCTIONS STARTING HERE

    # perform minimax algorithm to dataset
    def do_minimax(self, array):
        var_list_2 = [10000] * self.space_size
        for j in range(self.space_size):  # index j corresponds to unused data set
            if array[5, j] != 1:
                continue

            var_list_1 = [0] * 14  # there are 14 possible answers to a code
            for i in range(
                self.space_size
            ):  # index i corresponds to possible solution data set
                if array[4, i] != 1:
                    continue

                combination = array[0:4, i]
                temp_goal = array[0:4, j]
                white, black = self.get_white_and_black(combination, temp_goal)

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
        # print("Worst case scenario:", min(var_list_2), "options after this round.")
        return array[0:4, np.argmin(var_list_2)]

    # update possible solution dataset array based on code and code response (ground_truth)
    def update_solutions_dataset(self, array, tested_code, ground_truth):
        # read number of black and white pegs
        ground_truth_white = ground_truth.count("W")
        ground_truth_black = ground_truth.count("B")

        # determine black and white pegs for all codes
        for i in range(self.space_size):
            combination = array[0:4, i]
            white, black = self.get_white_and_black(combination, tested_code)
            # set cell to 0 if solution is incompatible with last feedback (black/white combination)

            if (
                (ground_truth_white != white) or (ground_truth_black != black)
            ) or np.array_equal(combination, tested_code):
                array[4, i] = 0  # 0 means code is not part of solution set anymore

        # Magic math to calculate unused index
        unused_index = (
            (tested_code[0] - 1) * 216
            + (tested_code[1] - 1) * 36
            + (tested_code[2] - 1) * 6
            + tested_code[3]
            - 1
        )
        array[5, unused_index] = 0  # 0 means code is not part of unused set anymore


def run(goal):
    # initialize array with all possible combinations and information if part of solution set and information if part of unused set
    # number_set = np.ones(dtype=int, shape=[6, space_size])
    # thing=list()
    thing = np.transpose(list(itertools.product(colors, repeat=4)))

    number_set = np.concatenate(
        (thing, np.ones(dtype=int, shape=[2, space_size])), axis=0
    )
    # initialize the game
    game = Mastermind(goal)

    # initial guess
    combo = np.array([1, 1, 2, 2])

    # start the turn clock, check for a win after each round
    while game.turn_counter < 12 and not game.win:
        # requires a string of ex. "1 1 1 1" to parse correctly.
        # print("Give me a combination of the elements 1,2,3,4,5,6. Ya fucking idiot.")
        # print(combo)
        # check if the guess is the valid format
        # don't uptick the turn counter for an invalid format
        # i'm not that big of an asshole
        if len(combo) != 4 or not set(combo).issubset(game.colors):
            raise (
                "Invalid guess, moron. Make sure you're guessing four items from the list (e.g. '5 5 4 3')"
            )
        guess = game.guess(combo, game.goal)
        # print(guess)
        # print("goal is " + str(game.goal))

        game.update_solutions_dataset(number_set, combo, guess)
        # calculate number of solutions in the solution data set:
        possible_solutions = np.count_nonzero(number_set[4])

        # check if there is only one element left in the solution data set:
        if possible_solutions == 1:
            combo = number_set[0:4, np.argwhere(number_set[4] == 1)[0][0]]
        else:
            combo = game.do_minimax(number_set)
    # if we leave that game loop, print the win/loss statement
    # if game.win:
    #     print("I guess that was a pretty good game. I guess.")
    # else:
    #     print(game.turn_counter)
    #     print("Haha, loser.")
    return {"result": game.win, "turns": game.turn_counter, "goal": goal}


def main():
    with open("test.txt", "a") as file:
        file.write("[")
        for goal in list(itertools.product(colors, repeat=4)):
            time = []
            for i in range(4):
                start = timer()
                run(goal)
                end = timer()
                time.append(end-start)
            start = timer()
            res = run(goal)
            end = timer()
            time.append(end-start)
            res["time"] = np.mean(time)
            file.write(json.dumps(res))
            file.write(",\n")
        file.write("]")


if __name__ == "__main__":
    main()
