import sys
import os
import matplotlib
import math
import random
import argparse
import matplotlib.pyplot as plt
import numpy as np
import time


def randomize_is_winner(proba_of_win):
    precision = 10000
    rand = random.randint(0, precision)
    if rand >= precision * proba_of_win:
        # Lost
        return 0
    # Won
    return 1


def simulate_duel(proba_of_win, nb_matchs, nb_points_per_match):
    match_wins = 0
    for i in range(nb_matchs):
        nb_points = 0
        for j in range(nb_points_per_match):
            nb_points += randomize_is_winner(proba_of_win)
        if nb_points > nb_points_per_match / 2:
            match_wins += 1
    print(
        "Player A won {} matchs over {} matchs ({} points played per match)".format(
            match_wins, nb_matchs, nb_points_per_match
        )
    )


def main():
    proba_of_win = 0.51
    print(
        "Player A has a probability of {} to win any point during the match".format(
            proba_of_win
        )
    )
    # 101 points played per match
    simulate_duel(proba_of_win, 100, 101)
    simulate_duel(proba_of_win, 100, 101)
    simulate_duel(proba_of_win, 100, 101)
    # 1001 points played per match
    simulate_duel(proba_of_win, 100, 1001)
    simulate_duel(proba_of_win, 100, 1001)
    simulate_duel(proba_of_win, 100, 1001)
    # 10001 points played per match
    simulate_duel(proba_of_win, 100, 10001)
    simulate_duel(proba_of_win, 100, 10001)
    simulate_duel(proba_of_win, 100, 10001)


if __name__ == "__main__":
    main()
