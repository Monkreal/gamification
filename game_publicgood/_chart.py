import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np

def create(subssesion, rounds):
    text = []
    publicgood = []

    for round in range(rounds):
        round += 1
        s = subssesion.in_round(round)
        
        text.append('Runde ' + str(round))
        publicgood.append(s.publicgood)

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))

    y_pos = np.arange(len(text))
    plt.bar(y_pos, publicgood, align='center', alpha=0.7)
    plt.xticks(y_pos, text)
    plt.ylabel('Anzahl Punkte im öffentlichen Pool')
    plt.tick_params(axis='x', which='both', bottom=False)

    plt.tight_layout()
    plt.subplots_adjust(top=1)
    plt.savefig('_static/PDF/charts/chart.png')
    plt.close()