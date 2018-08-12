import sys
import os
import matplotlib
import math
import random
import argparse
import matplotlib.pyplot as plt
import numpy as np
import time

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


def simulate_elo_static(
    nb_players,
    nb_games,
    nb_placement,
    min_skill,
    delta_skill,
    sleep_time=1,
    verbose=False,
):
    players = []
    for i in range(nb_players):
        skill = min_skill + i * delta_skill
        players.append(Player("Elo of PlayerSkill(" + str(skill) + ")", skill, 1500))

    normal_games = nb_games - nb_placement
    # A journey consists of playing each player once. Each player will play journeys completely so the nb_games and nb_placement might not be respected
    nb_journeys = math.ceil(nb_placement / float(nb_players - 1))
    actual_placement_games = nb_journeys * nb_players
    # Playing the placement games with a high Knormal_games
    for journey in range(nb_journeys):
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
    nb_journeys = math.ceil(normal_games / float(nb_players - 1))
    for journey in range(nb_journeys):
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
        xy=(actual_placement_games, 1500),
        xycoords="data",
        xytext=(actual_placement_games, 1550),
        verticalalignment="top",
        arrowprops=dict(facecolor="black", shrink=0.05),
    )

    plt.rcParams["figure.figsize"] = (13, 10)
    for p in players:
        plt.plot(nb_games, p.elo_history, label=p.name, linewidth=3)

    leg = plt.legend(loc=1, ncol=2, mode="expand", shadow=True, fancybox=True)
    leg.get_frame().set_alpha(0.5)
    plt.show(block=False)
    time.sleep(sleep_time)
    plt.close()


def simulate_elo_dynamic(
    nb_players, nb_games, min_skill, delta_skill, sleep_time=1, verbose=False
):
    print("Initializing displays...")
    plt.ion()
    # Set up plot
    figure, ax = plt.subplots(nb_players)
    common_x = []
    list_of_y = []
    for l in range(nb_players):
        list_of_y.append([])
    lines = []
    for l in range(nb_players):
        # Autoscale ON
        lines.append(ax[l].plot(common_x, list_of_y[l], "--", linewidth=3)[0])
        ax[l].set_xlim(0, 10)
        ax[l].set_ylim(1000, 2000)
        ax[l].set_autoscalex_on(True)
        ax[l].set_autoscaley_on(False)
        ax[l].grid()

    graphSize = 10
    print("Initialized")

    players = []
    for i in range(nb_players):
        skill = min_skill + i * delta_skill
        players.append(Player("Elo of PlayerSkill(" + str(skill) + ")", skill, 1500))

    # A journey consists of playing each player once. Each player will play journeys completely so the nb_games and nb_placement might not be respected
    nb_journeys = math.ceil(nb_games / float(nb_players - 1))
    for journey in range(nb_journeys):
        for i in range(nb_players):
            # Each player will play against each other the same amount of times
            player1 = players[i]
            for j in range(nb_players):
                if j <= i:
                    continue
                player2 = players[j]
                player1.play_and_update(player2)

        common_x = np.arange(0, len(players[0].elo_history), 1)
        for l in range(nb_players):
            # Update data
            lines[l].set_xdata(common_x)
            lines[l].set_ydata(players[l].elo_history)
            # Need both of these in order to rescale
            ax[l].relim()
            ax[l].autoscale_view()

        # We need to draw *and* flush
        figure.canvas.draw()
        figure.canvas.flush_events()
        time.sleep(sleep_time)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Creates a number of players with varying skills, simulates matches against each other and follows their elo rating evolution"
    )
    parser.add_argument("nb_players", type=int, help="Number of players to create")
    parser.add_argument(
        "nb_games", type=int, help="Number of games each player will play"
    )
    parser.add_argument("nb_placements", type=int, help="Number of placement games")
    parser.add_argument("min_skill", type=int, help="Skill of the worst player")
    parser.add_argument("delta_skill", type=int, help="Skill gap between players")
    parser.add_argument(
        "--sleeptime",
        type=float,
        default=1,
        help="How much to sleep between graphical updates",
    )
    parser.add_argument(
        "--static",
        action="store_true",
        help="If not present, will output the dynamic version instead",
    )

    # Not used here but might be useful. No -v => args.verbosity=0, -v => args.verbosity=1, -vv => args.verbosity=2, etc.
    parser.add_argument("-v", "--verbosity", action="count", default=0)
    args = parser.parse_args()

    if args.nb_players <= 1:
        print("At least 2 players are needed")
        sys.exit()
    if args.static:
        while True:
            simulate_elo_static(
                args.nb_players,
                args.nb_games,
                args.nb_placements,
                args.min_skill,
                args.delta_skill,
                args.sleeptime,
                verbose=args.verbosity,
            )
    else:
        simulate_elo_dynamic(
            args.nb_players,
            args.nb_games,
            args.min_skill,
            args.delta_skill,
            args.sleeptime,
            verbose=False,
        )

