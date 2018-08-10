import sys
import os
import matplotlib
import math
import random
import argparse
import matplotlib.pyplot as plt
import numpy as np

# 40 for new players, 20 afterwards
K_FACTOR = 40
DIVIDER = 400


class Player(object):
    """
    Represents a player, its skill and its current elo points 
    """

    def __init__(self, name, skill, elo=1500, k_factor=K_FACTOR):
        self.name = name
        self.skill = skill
        self.elo = elo
        self.k_factor = k_factor
        self.elo_history = [elo]

    def __repr__(self):
        s = "Player name : {}, actual skill = {} elo rating {}".format(
            self.name, self.skill, self.elo
        )
        return s

    def expected_result(self, other):
        """Returns the expected value of the match against an other player (0 means a guaranteed loss, 1 means a guaranteed win)
        
        Arguments:
            other {Player} -- The second player
        """
        return float(1) / (1 + math.pow(10, float(other.elo - self.elo) / DIVIDER))

    def play(self, other):
        """Returns the result (0 if loss, 1 if won) of a game against an other player 
        
        Arguments:
            other {Player} -- The second player
        """
        proba_of_wining = float(self.skill) / (self.skill + other.skill)
        precision = 10000
        rand = random.randint(0, precision)
        if rand >= precision * proba_of_wining:
            # Loss
            return 0
        return 1

    def play_and_update(self, other, verbose=False):
        """Plays against an other player and updates both elo ratings depending on the output of the match
        
        Arguments:
            other {Player} -- Other player
        """
        expected = self.expected_result(other)
        result = self.play(other)
        delta_points = self.k_factor * (result - expected)
        self.elo = self.elo + delta_points
        self.elo_history.append(self.elo)
        other.elo = other.elo - delta_points
        other.elo_history.append(other.elo)

        if verbose:
            print(
                "expected by skill={}, expected by elo={}, result={}, delta_points={}".format(
                    float(self.skill) / (self.skill + other.skill),
                    expected,
                    result,
                    delta_points,
                )
            )


def main(verbose=False):
    nb_players = 10
    min_skill = 10
    delta_skill = 4
    while True:
        players = []
        for i in range(nb_players):
            skill = min_skill + i * delta_skill
            players.append(Player("Skill_" + str(skill), skill, 1500))

        placement_games = 2
        normal_games = placement_games * 4
        # Playing the placement games with a high K
        for journey in range(placement_games):
            for i in range(nb_players):
                # Each player will play against each other the same amount of times
                player1 = players[i]
                for j in range(nb_players):
                    if j <= i:
                        continue
                    player2 = players[j]
                    player1.play_and_update(player2)
        # Playing the normal games with a lower K
        for p in players:
            p.k_factor = p.k_factor / 2.0
        for journey in range(normal_games):
            for i in range(nb_players):
                # Each player will play against each other the same amount of times
                player1 = players[i]
                for j in range(nb_players):
                    if j <= i:
                        continue
                    player2 = players[j]
                    player1.play_and_update(player2)

        # Making cool graphs about what happened
        nb_games = np.arange(0, len(players[0].elo_history), 1)

        ax = plt.subplot(111)
        ax.annotate(
            "End of placement games",
            xy=(placement_games * len(players), 1500),
            xycoords="data",
            xytext=(placement_games * len(players), 1600),
            verticalalignment="top",
            arrowprops=dict(facecolor="black", shrink=0.05),
        )

        for p in players:
            plt.plot(nb_games, p.elo_history, label=p.name + " elo")

        leg = plt.legend(loc="best", ncol=2, mode="expand", shadow=True, fancybox=True)
        leg.get_frame().set_alpha(0.5)
        plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Creates a number of players with varying skills, simulates matches against each other and follows their elo rating evolution"
    )
    # parser.add_argument("nb_players", help="Number of players to create")
    # Not used here but might be useful. No -v => args.verbosity=0, -v => args.verbosity=1, -vv => args.verbosity=2, etc.
    parser.add_argument("-v", "--verbosity", action="count", default=0)
    args = parser.parse_args()

    main(verbose=args.verbosity)

