import numpy as np
from chi2comb import chi2comb_cdf, ChiSquared


def gradient_descent(value, step_size, significance_level, chi2s, normal_coefficient):
    prob_less_than_value = chi2comb_cdf(value, chi2s, normal_coefficient)
    significance_of_value = 1 - prob_less_than_value

    fractional_error = (significance_of_value - significance_level) / significance_level

    return value + fractional_error * step_size


def compute_generalised_chi_squared_critical_value(weight_vector,
                                                   centrality_vector,
                                                   dof_vector,
                                                   normal_coefficient,
                                                   significance_level,
                                                   initial_value):
    chi2s = [ChiSquared(weight_vector[i], centrality_vector[i], dof_vector[i])
             for i in range(len(weight_vector))]

    # TODO: check experimentally or theoretically that this converges as expected
    z0 = initial_value
    z1 = np.float('inf')
    step_size = 0.1 * z0
    error_level = 0.001 * z0

    while np.abs(z0 - z1) > error_level:
        z0 = z1
        z1 = gradient_descent(z0, step_size, significance_level, chi2s, normal_coefficient)

    return z1
