from scipy.stats import weibull_min
import numpy as np
import matplotlib.pyplot as plt

def fit_weibull(speed_data):
    """
    Fit a 2-parameter Weibull to the input wind-speed array.
    Returns: k (shape), A (scale).
    """
    k, loc, A = weibull_min.fit(speed_data, floc=0)
    return k, A

def plot_weibull(speed_data, k, A, height, bins=30):
    """
    Plot the observed wind-speed histogram (density) and overlay the
    fitted Weibull PDF with parameters k, A.
    """
    counts, edges = np.histogram(speed_data, bins=bins, density=True)
    centers = 0.5*(edges[:-1] + edges[1:])
    pdf = weibull_min.pdf(centers, k, loc=0, scale=A)

    plt.figure()
    plt.bar(centers, counts,
            width=(edges[1]-edges[0]),
            alpha=0.6,
            label='Observed')
    plt.plot(centers, pdf, lw=2,
             label=f'Weibull k={k:.2f}, A={A:.2f}')
    plt.title(f"Weibull Distribution Fit at {height} m")
    plt.xlabel('Wind Speed [m/s]')
    plt.ylabel('Probability Density')
    plt.legend()
    plt.grid(True)
    plt.show()
