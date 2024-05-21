import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

def get_average(subsession):    
    count = 0
    average = 0
    
    for player in subsession.get_players():
        deal = player.field_maybe_none('deal')
        
        if deal is not None:
            average += player.deal
            count += 1
    
    if count == 0:
        return 0
    else:
        return int(average / count)
    
    
def calculate_intersection(sellercount, buyercount):
    if sellercount == 1 or buyercount == 1:
        return 0, 0
    else:
        (x1, y1), (x2, y2) = (1, 10), (sellercount, sellercount * 10)
        (x3, y3), (x4, y4) = (1, buyercount * 10 + 20), (buyercount, 30)  

        m1 = (y2 - y1) / (x2 - x1)
        b1 = y1 - m1 * x1

        m2 = (y4 - y3) / (x4 - x3)
        b2 = y3 - m2 * x3

        x_intersect = (b2 - b1) / (m1 - m2)
        y_intersect = m1 * x_intersect + b1

        return x_intersect, y_intersect
    

def create_charts(subsession, round):
    averages = []
    # Creating data points for both charts
    for round_number in range(round):
        s = subsession.in_round(round_number + 1)
        averages.append(get_average(s))
        
    sellercount = subsession.session.vars.get('sellercount', 0)
    buyercount = subsession.session.vars.get('buyercount', 0)
        
    x_intersect, y_intersect = calculate_intersection(sellercount, buyercount)    
    
    xyValues = [(i+1, avg) for i, avg in enumerate(averages)]
    
    lineData1 = [(1, 10), (sellercount, sellercount * 10)]
    lineData2 = [(1, buyercount * 10 + 20), (buyercount, 30)]
    lineData3 = [(1, y_intersect), (sellercount, y_intersect)]
    lineData4 = [(x_intersect, 0), (x_intersect, buyercount * 10 + 30)]
    
    fig, axes = plt.subplots(1, 2, figsize=(10, 6))  # 10x6 for each subplot, total 20x6

    # First chart
    ax1 = axes[0]
    x, y = zip(*lineData3)
    ax1.plot(x, y, linestyle='--', color=(0.4, 0.4, 0.4))
    
    x, y = zip(*lineData4)
    ax1.plot(x, y, linestyle='--', color=(0.4, 0.4, 0.4))
    
    x, y = zip(*lineData1)
    ax1.plot(x, y, color=(0, 0, 0))
    
    x, y = zip(*lineData2)
    ax1.plot(x, y, color=(0, 0, 0))
    
    ax1.set_title('Theoretical prediction')
    ax1.set_xlabel('Quantity')
    ax1.set_ylabel('Price')
    ax1.set_xlim(1, max(sellercount, buyercount))
    ax1.set_ylim(0, buyercount * 10 + 30)
    ax1.grid(True)
    ax1.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax1.yaxis.set_major_locator(MaxNLocator(integer=True))

    # Second chart
    ax2 = axes[1]
    x, y = zip(*xyValues)
    ax2.scatter(x, y, label='Points', color=(0, 0, 0))
    ax2.plot([1, round], [y_intersect, y_intersect], linestyle='--', color=(0.4, 0.4, 0.4))
    
    ax2.set_title('Actual average market prices')
    ax2.set_xlabel('Rounds')
    ax2.set_ylabel('Price')
    ax2.set_xlim(1, round)
    ax2.set_ylim(0, buyercount * 10 + 30)
    ax2.grid(True)
    ax2.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax2.yaxis.set_major_locator(MaxNLocator(integer=True))
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.96)
    plt.savefig('_static/PDF/charts/chart.png')
    plt.close()