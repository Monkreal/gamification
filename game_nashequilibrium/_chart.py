import matplotlib.pyplot as plt
import matplotlib.patches as patches

def chart(subsession, info, round = 0):
    settings = subsession.session.vars.get('settings', [])
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    xmin, xmax = 0, 3
    ymin, ymax = 0, 3

    for i in range(xmin, xmax + 1):
        ax.plot([i, i], [ymin, ymax], color='black')
    for i in range(ymin, ymax + 1):
        ax.plot([xmin, xmax], [i, i], color='black')
        
    if info:        
        dict = {
            'nn': subsession.nn,
            'np': subsession.np,
            'pn': subsession.pn,
            'pp': subsession.pp
        }

        value = max(dict, key=dict.get)
        
        if value == 'nn':
            ax.add_patch(patches.Rectangle((1, 1), 1, 1, fill=False, edgecolor='red', linewidth=5))
        elif value == 'np':
            ax.add_patch(patches.Rectangle((1, 0), 1, 1, fill=False, edgecolor='red', linewidth=5))
        elif value == 'pn':
            ax.add_patch(patches.Rectangle((2, 1), 1, 1, fill=False, edgecolor='red', linewidth=5))
        else:
            ax.add_patch(patches.Rectangle((2, 0), 1, 1, fill=False, edgecolor='red', linewidth=5))
            
        ax.text(2.75, -0.25, 'Runde ' + str(round), ha='center', va='center', fontsize=14, color='black')

    title1 = [(2, 0, settings[4][0]), (1, 0, settings[4][1])]  

    for (i, j, text) in title1:
        ax.text(j + 0.5, i - 0.5, text, ha='center', va='center', fontsize=14, color='black')
    
    title2 = [(3, 1, settings[4][0]), (3, 2, settings[4][1])]  

    for (i, j, text) in title2:
        ax.text(j + 0.5, i - 0.5, text, ha='center', va='center', fontsize=14, color='red')

    fields_with_diagonal = [(3, 0, 'Spieler 1', 'Spieler 2'), (2, 1, settings[0][0], settings[0][1]), (2, 2, settings[2][0], settings[2][1]), (1, 1, settings[1][0], settings[1][1]), (1, 2, settings[3][0], settings[3][1])]

    for (i, j, text1, text2) in fields_with_diagonal:
        ax.plot([j, j + 1], [i, i - 1], color='black')
        ax.text(j + 0.7, i - 0.3, text1, ha='center', va='center', fontsize=14, color='red')
        ax.text(j + 0.3, i - 0.7, text2, ha='center', va='center', fontsize=14, color='black')

    ax.axis('off')

    plt.tight_layout()
    plt.subplots_adjust(top=1)
    
    if info:
        plt.savefig('_static/PDF/charts/chart' + str(subsession.round_number + 1) + '.png')
    else:
        plt.savefig('_static/PDF/charts/chart1.png')
    plt.close()