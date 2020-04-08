import sys
import os
import matplotlib
import math
import random
import argparse
import matplotlib.pyplot as plt
import numpy as np
import time


"""
    We'll use the elo settings that are estimated on this page: 
    https://leagueoflegends.fandom.com/wiki/Elo_rating_system

    Season 2 :
    Bronze: Between 0 and 1149 (Team: 0-1249) (Top 100%)
    Silver: Between 1150 and 1499 (Team: 1250-1449) (Top 68%-13%)  Majority of Active Player Base
    Gold: Between 1500 and 1849 (Team: 1450-1649) (Top 13%-1.5%)
    Platinum: Between 1850 and 2199 (Team: 1650-1849) (Top 1.5%-0.1%)
    Diamond: 2200 and above (Team: 1850+) (Top 0.1%) 

    Current distribution (updated in march 2020 on this site):
    https://www.esportstales.com/league-of-legends/rank-distribution-percentage-of-players-by-tier

    Rank 	    Top%    Rank 	    Top%    Rank 	    Top%
    Iron IV 	98.84 	Silver II 	47.9 	Diamond IV 	2.1
    Iron III 	98.4 	Silver I 	38.9 	Diamond III 0.85
    Iron II 	97.2 	Gold IV 	31.7 	Diamond II 	0.60
    Iron I 	    95.0 	Gold III 	22.4 	Diamond I 	0.28
    Bronze IV 	91.3 	Gold II 	16.7 	Master 	    0.099
    Bronze III 	85.7 	Gold I 	    12.1 	GrandMaster 0.069
    Bronze II 	81.3 	Platinum IV 9.1 	Challenger 	0.021
    Bronze I 	75.5 	Platinum III6.0 		
    Silver IV 	68.2 	Platinum II 4.2 		
    Silver III 	57.2 	Platinum I 	3.0 		

    Based on season 2 data, going from Silver I to Gold I means :
    Going from top 38.9 % to top 12.1%
    With a linear interpolation (questionable) from season 2 data, that meant going from elo ~1335 to elo ~1505.
    This is a rough approximate but it will be used as an illustration further on.
"""
K_FACTOR = 25
STARTING_ELO = 1200
PROBA_OF_INTER = 0.1


def create_team_and_play(proba_of_inter=PROBA_OF_INTER):
    nb_inters_our_team = 0
    nb_inters_their_team = 0
    # Creating 4 teammates that might or might not be inters
    for i in range(4):
        nb_inters_our_team += randomize_is_inter(proba_of_inter)
    # Creating 5 oponents that might or might not be inters
    for i in range(5):
        nb_inters_their_team += randomize_is_inter(proba_of_inter)
    if nb_inters_our_team < nb_inters_their_team:
        # We win
        return 1
    elif nb_inters_our_team > nb_inters_their_team:
        # We lose
        return 0
    else:
        # Coin flip because everyone has the same skill
        return random.randint(0, 1)


def randomize_is_inter(proba_of_inter):
    precision = 10000
    rand = random.randint(0, precision)
    if rand >= precision * proba_of_inter:
        # Normal human being
        return 0
    # It's an inter, probably disco nunu
    return 1


def main():
    nb_wins = 0
    nb_losses = 0
    for i in range(1000000):
        if create_team_and_play():
            nb_wins += 1
        else:
            nb_losses += 1
    print(
        "Nb wins {}, nb losses {}, winrate {}".format(
            nb_wins, nb_losses, nb_wins / (nb_wins + nb_losses)
        )
    )
    # After 1000000 simulations, the result was:
    # Nb wins 535868, nb losses 464132, winrate 0.535868


if __name__ == "__main__":
    main()
