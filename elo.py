import sys
import os
import matplotlib
import math
import random
import argparse

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
        other.elo = other.elo - delta_points
        if verbose:
            print(
                "expected={}, result={}, delta_points={}".format(
                    expected, result, delta_points
                )
            )


def main(verbose=False):
    a = Player("A", 20, 1500)
    b = Player("B", 10, 1500)
    print(a)
    print(b)
    for i in range(1000):
        a.play_and_update(b, True)
        print(a)
        print(b)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Creates a number of players with varying skills, simulates matches against each other and follows their elo rating evolution"
    )
    # parser.add_argument("nb_players", help="Number of players to create")
    # Not used here but might be useful. No -v => args.verbosity=0, -v => args.verbosity=1, -vv => args.verbosity=2, etc.
    parser.add_argument("-v", "--verbosity", action="count", default=0)
    args = parser.parse_args()

    main(verbose=args.verbosity)

