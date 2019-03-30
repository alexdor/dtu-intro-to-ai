import json
from functools import reduce
from itertools import permutations, product, repeat
from operator import iconcat
from random import choices, randint
from timeit import default_timer as timer

import click
import numpy as np

space_size = 1296
colors = [1, 2, 3, 4, 5, 6]
# make the game
class Mastermind:
    # initialize the variables
    def __init__(self, goal):
        self.colors = colors
        self.set = permutations(self.colors, 4)
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
        answer += repeat("B", black)
        answer += repeat("W", white)
        answer += repeat("", 4 - black - white)
        self.turn_counter += 1
        # check for a win after each guess
        if answer == ["B", "B", "B", "B"]:
            self.win = True
        return answer

    # GAME SOLVING FUNCTIONS STARTING HERE
    def do_minimax(self, array):

        solution_maxes = np.full([self.space_size], self.space_size + 1, dtype=int)

        for j in np.where(array[5] == 1)[0]:
            possible_solutions = np.zeros(
                [14]
            )  # there are 14 possible answers to a code
            for i in np.where(array[4] == 1)[
                0
            ]:  # index i corresponds to possible solution data set

                combination = array[0:4, i]
                temp_goal = array[0:4, j]
                white, black = self.get_white_and_black(combination, temp_goal)

                # calculation of remaining combinations
                if (white == 0) and (black == 4):
                    possible_solutions[0] += 1
                elif (white == 0) and (black == 3):
                    possible_solutions[1] += 1
                elif (white == 2) and (black == 2):
                    possible_solutions[2] += 1
                elif (white == 1) and (black == 2):
                    possible_solutions[3] += 1
                elif (white == 0) and (black == 2):
                    possible_solutions[4] += 1
                elif (white == 3) and (black == 1):
                    possible_solutions[5] += 1
                elif (white == 2) and (black == 1):
                    possible_solutions[6] += 1
                elif (white == 1) and (black == 1):
                    possible_solutions[7] += 1
                elif (white == 0) and (black == 1):
                    possible_solutions[8] += 1
                elif (white == 4) and (black == 0):
                    possible_solutions[9] += 1
                elif (white == 3) and (black == 0):
                    possible_solutions[10] += 1
                elif (white == 2) and (black == 0):
                    possible_solutions[11] += 1
                elif (white == 1) and (black == 0):
                    possible_solutions[12] += 1
                elif (white == 0) and (black == 0):
                    possible_solutions[13] += 1

            solution_maxes[j] = np.amax(possible_solutions)
        return array[0:4, np.argmin(solution_maxes)]

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

def run(goal, verbose):
    # initialize array with all possible combinations and information if part of solution set and information if part of unused set
    thing = np.transpose(list(product(colors, repeat=4)))

    number_set = np.concatenate(
        (thing, np.ones(dtype=int, shape=[2, space_size])), axis=0
    )
    # initialize the game
    game = Mastermind(goal)

    # initial guess
    combo = np.array([1, 1, 2, 2])
    if verbose:
        line = '|'.join(str(x).center(12) for x in ["Turn","Guess","Outcome"])
        print(f"\n{line}")
        print('-' * (len(line) + 5))

    # start the turn clock, check for a win after each round
    while game.turn_counter < 12 and not game.win:
        # requires a string of ex. "1 1 1 1" to parse correctly.
        # check if the guess is the valid format
        # don't uptick the turn counter for an invalid format
        if len(combo) != 4 or not set(combo).issubset(game.colors):
            raise (
                "Something went wrong, I made an invalid guess"
            )
        guess = game.guess(combo, game.goal)
        if verbose:
            print('|'.join(str(x).center(12)  for x in [game.turn_counter,combo,guess]))
        game.update_solutions_dataset(number_set, combo, guess)
        # calculate number of solutions in the solution data set:
        possible_solutions = np.count_nonzero(number_set[4])

        # check if there is only one element left in the solution data set:
        if possible_solutions == 1:
            combo = number_set[0:4, np.argwhere(number_set[4] == 1)[0][0]]
        else:
            combo = game.do_minimax(number_set)
    if verbose:
        print("\n")
    return {"result": game.win, "turns": game.turn_counter, "goal": goal}


# TODO: Implement a way for a user to play as both players
# TODO: Plot all the things
# TODO: FINISH THE REPORT!!!!


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "--file",
    default="mastermind_test.json",
    help="A file name to write the output of the test",
    type=click.File(mode="a"),
)
@click.option("--time", default=False, help="Time each game", type=click.BOOL)
@click.option(
    "--verbose",
    default=False,
    help="Print verbose output of each round",
    type=click.BOOL,
)
def test(file, time,verbose):
    """This command plays a game with the AI for every possible combination.
        If you want to also check the time it takes for a game to be played you can enable the --time=True flag
    """
    click.echo("Starting the test")
    file.write("[")
    with click.progressbar(list(product(colors, repeat=4))) as bar:
        for goal in bar:
            timing = []
            if time:
                for i in range(4):
                    start = timer()
                    run(goal, verbose)
                    end = timer()
                    timing.append(end - start)
            if time:
                start = timer()
                res = run(goal,verbose)
                end = timer()
                timing.append(end - start)
                res["time"] = np.mean(timing)
            else:
                res = run(goal,verbose)
            file.write(json.dumps(res))
            file.write(",\n")
    file.write("]")


@cli.command()
@click.option(
    "--verbose",
    default=False,
    help="Print verbose output of each round",
    type=click.BOOL,
)
def play(verbose):
    """This command plays a game with the AI
        You can enable verbose mode by using the --verbose=True flag
    """
    # click.echo("Dropped the database")
    res = ""
    while True:
        try:
            res = click.prompt("Please type 4 numbers from 1 till 6")
            res = res.split(" ")
            res = [r.split(",") for r in res if r]
            res = reduce(iconcat, res, [])
            res = [int(r) for r in res]
        except ValueError:
            click.echo(
                "Invalid guess. Make sure you're guessing four items from the 1 till 6 (e.g. '5 5 4 3')"
            )
            continue
        if len(res) != 4 or not set(res).issubset(colors):
            click.echo(
                "Invalid guess. Make sure you're guessing four items from the 1 till 6 (e.g. '5 5 4 3')"
            )
            continue
        break
    results = run(res, verbose)
    click.echo(
        f"I {'won' if results['result'] else 'lost'} this game after {results['turns']} {'turn' if results['turns'] == 1 else 'turns'}"
    )


if __name__ == "__main__":
    cli()
