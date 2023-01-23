import sys
import os
import matplotlib
import math
import random
import argparse
import matplotlib.pyplot as plt
import numpy as np
import time

# FIDE (chess) use K=40 for placement games and K=20 afterwads (or k=10 for high elo): https://en.wikipedia.org/wiki/Elo_rating_system
# LOL (season 2) seems to use K=100 for placement games and K=25 afterwards: https://leagueoflegends.fandom.com/wiki/Elo_rating_system
K_FACTOR_PLACEMENTS = 100
K_FACTOR = 25
DIVIDER = 400
STARTING_ELO = 1200
FORCED_WINRATE = 0.536
"""
0.536 is the theoretical winrate of a player in elo hell. 
Elo hell is here defined as: 
- Any other player has a probability of ruining the game of 0.1 (a.k.a. inter)
- If both teams have an equal number of inters, then the probability of wining the game is 0.5
"""


class Player(object):
    """
    Represents a player, its skill and its current elo points 
    """

    def __init__(
        self,
        name,
        skill,
        elo=STARTING_ELO,
        k_factor=K_FACTOR_PLACEMENTS,
        is_inter=False,
    ):
        self.name = name
        self.skill = skill
        self.elo = elo
        self.k_factor = k_factor
        self.elo_history = [elo]
        self.is_inter = is_inter

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

    def play_forced_winrate(self, winrate):
        proba_of_wining = winrate
        precision = 10000
        rand = random.randint(0, precision)
        if rand >= precision * proba_of_wining:
            # Loss
            return 0
        return 1

    def play_and_update(
        self, other, elohell=False, forced_win_rate=FORCED_WINRATE, verbose=False
    ):
        """Plays against an other player and updates both elo ratings depending on the output of the match

        Arguments:
            other {Player} -- Other player

        Keyword Arguments:
            elohell {bool} -- If true, a fixed winrate will be used instead (default: {False})
            forced_win_rate {[type]} -- Only used if elohell==True (default: {FORCED_WINRATE})
            verbose {bool} -- More prints (default: {False})
        """
        if not (elohell):
            result = self.play(other)
        else:
            result = self.play_forced_winrate(forced_win_rate)
        self.update(other, result, verbose=verbose)

    def update(
        self, other, result, verbose=False
    ):
        """Updates this player's ELO and the 'other' player's ELO depending on the 'result' of a game.

        Arguments:
            other {Player} -- Other player
            result {Float} -- Result of the game. 1.0 for a win against the 'other' player, 0.0 for a loss,
            0.5 for a draw.

        Keyword Arguments:
            elohell {bool} -- If true, a fixed winrate will be used instead (default: {False})
            forced_win_rate {[type]} -- Only used if elohell==True (default: {FORCED_WINRATE})
            verbose {bool} -- More prints (default: {False})
        """
        expected = self.expected_result(other)
        delta_points = self.k_factor * (result - expected)
        self.elo = self.elo + delta_points
        self.elo_history.append(self.elo)
        other.elo = other.elo - delta_points
        other.elo_history.append(other.elo)

        if verbose:
            print(
                "{} vs {}. Expected by skill={}, expected by elo={}, result={}, delta_points={}".format(
                    self.name,
                    other.name,
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
    elohell=False,
    verbose=False,
):
    players = []
    for i in range(nb_players):
        skill = min_skill + i * delta_skill
        players.append(
            Player("Elo of PlayerSkill(" + str(skill) + ")", skill, STARTING_ELO)
        )

    normal_games = nb_games - nb_placement
    # A journey consists of playing each player once. Each player will play journeys completely so the nb_games and nb_placement might not be respected
    nb_journeys = math.ceil(nb_placement / float(nb_players - 1))
    if not (elohell):
        actual_placement_games = nb_journeys * nb_players
    else:
        actual_placement_games = nb_placement
    for mode in range(2):
        # Playing the placement games with a high K (mode==0) then playing the normal games with a lower K (mode==1)
        if not (elohell):
            actual_games = nb_journeys * nb_players
            for journey in range(nb_journeys):
                for i in range(nb_players):
                    # Each player will play against each other the same amount of times
                    player1 = players[i]
                    for j in range(nb_players):
                        if j <= i:
                            continue
                        player2 = players[j]
                        player1.play_and_update(player2, verbose=verbose)
        else:
            # In elohell mode players don't play against each other, they have a fixed winrate and play each 'actual_games' games against oponents of the same elo they are actually in
            for p in players:
                for i in range(nb_placement if mode == 0 else normal_games):
                    p.play_and_update(
                        Player("FakePlayer", 10, elo=p.elo),
                        elohell=elohell,
                        forced_win_rate=FORCED_WINRATE,
                        verbose=verbose,
                    )
        # Playing the normal games with a lower K
        for p in players:
            p.k_factor = K_FACTOR
        nb_journeys = math.ceil(normal_games / float(nb_players - 1))

    # Making cool graphs about what happened
    nb_games = np.arange(0, len(players[0].elo_history), 1)

    plt.rcParams["figure.figsize"] = (13, 10)
    ax = plt.subplot(111)
    ax.annotate(
        "End of placement games",
        xy=(actual_placement_games, STARTING_ELO),
        xycoords="data",
        xytext=(actual_placement_games, STARTING_ELO + 50),
        verticalalignment="top",
        arrowprops=dict(facecolor="black", shrink=0.05),
    )

    for p in players:
        plt.plot(nb_games, p.elo_history, label=p.name, linewidth=3)

    # Caculating the average elo. This value should be constant in the normal mode but it's not because the same match will appear
    # in different positions of each player's elo_history. So just use this as a debugg tool.
    average_elo = []
    for i in range(len(players[0].elo_history)):
        avg = 0
        for p in players:
            avg += p.elo_history[i]
        average_elo.append(avg / float(len(players)))
    plt.plot(nb_games, average_elo, label="AVERAGE ELO", linewidth=6)

    leg = plt.legend(loc=1, ncol=2, mode="expand", shadow=True, fancybox=True)
    leg.get_frame().set_alpha(0.5)
    plt.show(block=False)
    time.sleep(sleep_time)
    plt.close()


def simulate_elo_dynamic(
    nb_players,
    nb_games,
    min_skill,
    delta_skill,
    sleep_time=1,
    elohell=False,
    verbose=False,
):
    if elohell:
        print("elohell option not implemented yet in the dynamic case")
        return
    print("Initializing displays...")
    plt.ion()
    # Set up plot
    plt.rcParams["figure.figsize"] = (20, 16)
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
        ax[l].set_ylim(1250, 1750)
        ax[l].set_autoscalex_on(True)
        ax[l].set_autoscaley_on(False)
        ax[l].grid()

    graphSize = 10
    print("Initialized")

    players = []
    for i in range(nb_players):
        skill = min_skill + i * delta_skill
        players.append(
            Player("Elo of PlayerSkill(" + str(skill) + ")", skill, STARTING_ELO)
        )

    # A journey consists of playing each player once. Each player will play journeys completely so the nb_games and nb_placement might not be respected
    nb_journeys = math.ceil(nb_games / float(nb_players - 1))
    # Playing the normal games with a lower K
    for p in players:
        p.k_factor = p.k_factor / 2.0
    for journey in range(nb_journeys):
        for i in range(nb_players):
            # Each player will play against each other the same amount of times
            player1 = players[i]
            for j in range(nb_players):
                if j <= i:
                    continue
                player2 = players[j]
                player1.play_and_update(
                    player2, elohell=elohell, forced_win_rate=FORCED_WINRATE
                )

        common_x = np.arange(0, len(players[0].elo_history), 1)
        for l in range(nb_players):
            # Update data
            lines[l].set_xdata(common_x)
            lines[l].set_ydata(players[l].elo_history)
            # Need both of these in order to rescale
            ax[l].relim()
            ax[l].autoscale_view()
            ax[l].legend([players[l].name])

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
    parser.add_argument(
        "--elohell",
        action="store_true",
        help="Mode where the winrate is fixed and players always play against oponents of the same skill",
    )

    # Not used here but might be useful. No -v => args.verbosity=0, -v => args.verbosity=1, -vv => args.verbosity=2, etc.
    parser.add_argument("-v", "--verbosity", action="count", default=0)
    args = parser.parse_args()

    if args.elohell:
        print(
            "Warning: the elohell option completely changes this program's behaviour, don't get fooled. Players don't play against each other anymore."
        )

    if args.nb_players <= 1 and not (args.elohell):
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
                elohell=args.elohell,
                verbose=args.verbosity,
            )
    else:
        simulate_elo_dynamic(
            args.nb_players,
            args.nb_games,
            args.min_skill,
            args.delta_skill,
            args.sleeptime,
            elohell=args.elohell,
            verbose=False,
        )
