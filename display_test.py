import matplotlib.pyplot as plt
import matplotlib
import random
import argparse
import math


def generate_point(t, index, last_point):
    if index == 0:
        return math.sin(t / float(10))
    if index == 1:
        return last_point + random.randint(-(index + 1), index + 1) * math.sqrt(t)

    return last_point + random.randint(-(index + 1), index + 1)


def test_display(nb_curves):
    print("Initializing displays...")
    plt.ion()
    # Set up plot
    figure, ax = plt.subplots(nb_curves)
    common_x = [0]
    list_of_y = []
    for l in range(nb_curves):
        list_of_y.append([0])
    lines = []
    for l in range(nb_curves):
        # Autoscale ON
        lines.append(ax[l].plot(common_x, list_of_y[l], "--")[0])
        ax[l].set_xlim(0, 30)
        ax[l].set_ylim(0, 1)
        ax[l].set_autoscalex_on(True)
        ax[l].set_autoscaley_on(True)
        ax[l].grid()

    graphSize = 100
    setBack = 0
    print("Initialized")

    t = -1
    while True:
        t = t + 1
        common_x.append(t)
        for l in range(nb_curves):
            y = generate_point(t, l, list_of_y[l][-1])
            list_of_y[l].append(y)
            # Update data
            lines[l].set_xdata(common_x)
            lines[l].set_ydata(list_of_y[l])
            # Need both of these in order to rescale
            ax[l].relim()
            ax[l].autoscale_view()

        # if len(common_x) > graphSize:
        #     common_x = common_x[setBack:graphSize]
        #     for l in range(nb_curves):
        #         list_of_y[l] = list_of_y[l][setBack:graphSize]
        #         # Update data (with the new _and_ the old points)
        #         lines[l].set_xdata(common_x)
        #         lines[l].set_ydata(list_of_y[l])
        #         # Need both of these in order to rescale
        #         ax[l].relim()
        #         ax[l].autoscale_view()

        # We need to draw *and* flush
        figure.canvas.draw()
        figure.canvas.flush_events()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Testing some display related stuff with matplotlib"
    )
    parser.add_argument("nb_curves", type=int, help="Number of curves")

    args = parser.parse_args()

    test_display(args.nb_curves)
