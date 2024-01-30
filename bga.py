import matplotlib.pyplot as plt
import numpy as np


def expected_win_rate(delta_elo):
    return 1 - 1 / (1 + 10 ** (delta_elo / 400))


print(expected_win_rate(583.81 - 332.54))

# ELO difference range: from 0 to 800
delta_elos = np.arange(0, 501, 1)
win_rates = [100 * expected_win_rate(delta) for delta in delta_elos]

print(expected_win_rate(583.81 - 332.54))

plt.figure(figsize=(10, 6))
plt.plot(delta_elos, win_rates)
plt.xlabel("ELO Difference (Player - Opponent)")
plt.ylabel("Expected Win Rate")
plt.title("Expected Win Rate vs ELO Difference (BoardGameArena)")
plt.xticks(np.arange(0, 501, 25))
plt.yticks(np.arange(50, 100, 1))  # Ticks for win rates at intervals of 0.1
# Adding a finer grid for better readability
plt.grid(True, which="both", linestyle="-", linewidth=0.5)
plt.show()

nb_wins_to_match_a_loss = [
    (1 / (1 - expected_win_rate(delta)) - 1) for delta in delta_elos
]

plt.figure(figsize=(10, 6))
plt.plot(delta_elos, nb_wins_to_match_a_loss)
plt.xlabel("ELO Difference (Player - Opponent)")
plt.ylabel("Number of wins")
plt.title("Number of wins to compensate a loss")
plt.xticks(np.arange(0, 501, 25))
plt.yticks(np.arange(0, 20, 1))  # Ticks for win rates at intervals of 0.1


# Adding a finer grid for better readability
plt.grid(True, which="both", linestyle="-", linewidth=0.5)
plt.show()
