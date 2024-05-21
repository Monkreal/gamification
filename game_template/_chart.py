import matplotlib.pyplot as plt

def create(subssesion):
    #Place here your result function to Picture
    #Store in Static/PDF/Charts
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.96)
    plt.savefig('_static/PDF/charts/chart.png')
    plt.close()