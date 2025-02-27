import numpy as np
import matplotlib.pyplot as plt

def fit_polynomial(x, y, degree=5):
    """
    Fit a polynomial of given degree to the provided data points.
    
    Parameters:
        x (list or np.array): X-coordinates of data points
        y (list or np.array): Y-coordinates of data points
        degree (int): Degree of the polynomial (default is 5)
    
    Returns:
        np.poly1d: A polynomial function fitted to the data
    """
    coefficients = np.polyfit(x, y, degree)
    polynomial = np.poly1d(coefficients)
    return polynomial

def plot_fitted_polynomial(x, y, polynomial):
    """
    Plot the original data points and the fitted polynomial curve.
    
    Parameters:
        x (list or np.array): X-coordinates of data points
        y (list or np.array): Y-coordinates of data points
        polynomial (np.poly1d): The fitted polynomial function
    """
    x_range = np.linspace(min(x), max(x), 100)
    y_fitted = polynomial(x_range)
    
    plt.scatter(x, y, color='red', label='Data Points')
    plt.plot(x_range, y_fitted, label='Fitted Polynomial', linestyle='--')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.legend()
    plt.title('5th Degree Polynomial Fit')
    plt.show()

# Example usage:
if __name__ == "__main__":
    # Example data points
    x_data = np.array([19.8, 17.7, 15.2, 12.2, 8.4])
    y_data = np.array([12, 14, 16, 18, 20])
    
    # Fit a 5th-degree polynomial
    poly_function = fit_polynomial(x_data, y_data, degree=5)
    
    # Display the polynomial equation
    print("Fitted Polynomial:")
    print(poly_function)
    
    # Plot the fitted polynomial
    plot_fitted_polynomial(x_data, y_data, poly_function)
