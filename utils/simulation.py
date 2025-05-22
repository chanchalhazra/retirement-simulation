import numpy as np
from utils.utilities import calculate_portfolio

# simulation function
def monte_carlo_simulation(distribution_type='normal', no_simulations=10000, no_years=30):
    #initilize simulation returns as Numpy arrays
    simulation_returns = np.zeros((no_years, no_simulations))
    for i in range(no_simulations):
        port_val = starting_portfolio
        #expense = yrly_expense
        for j in range(no_years):
            if distribution_type == 'normal':
                #eq_return = np.random.normal(mu_equity, sigma_equity)
                eq_return = np.random.normal(mu_equity, sigma_equity)
                #eq_return = np.random.normal(loc=8, scale=15)
                #print(f"eq return {eq_return}")
                bd_return = np.random.normal(mu_bond, sigma_bond)
            elif distribution_type == 'empirical': #empirical distribution
                eq_return = np.random.choice(df['US_equity'])
                #print(f"eq return {eq_return}")
                bd_return = np.random.choice(df['US_bond'])
            #print(f"Bond return {bd_return}")
            port_val = calculate_portfolio(start_val=port_val, expense=yrly_expenses[j], income=total_incomes[j],
                                            ssn_earning=total_ssn_earnings[j], eq_ret_rate=eq_return, bd_ret_rate=bd_return)
            #print(f"port val {port_val}")
            simulation_returns[j, i] = np.round(port_val,2)
    return simulation_returns

# simulation function choosing choices in bulk but not much time difference
def monte_carlo_simulation_bulk(distribution_type = 'normal', no_simulations = 10000, no_years = 30):
    #initilize simulation returns as Numpy arrays
    simulation_returns = np.zeros((future_years, no_simulations))
    for i in range(no_simulations):
        port_val = starting_portfolio
        if distribution_type == 'normal':
            eq_returns = np.random.normal(loc=mu_equity, scale=sigma_equity, size=future_years)
            bd_returns = np.random.normal(loc=mu_bond, scale=sigma_bond, size=future_years)
        elif distribution_type == 'empirical': #empirical distribution
            eq_returns = np.random.choice(df['US_equity'], size=future_years)
            #print(f"eq return {eq_return}")
            bd_returns = np.random.choice(df['US_bond'], size=future_years)
        for j in range(future_years):
            port_val = calculate_portfolio(start_val=port_val, expense=yrly_expenses[j], income=total_incomes[j],
                                        ssn_earning=total_ssn_earnings[j], eq_ret_rate=eq_returns[j], bd_ret_rate=bd_returns[j])
            #print(f"port val {port_val}")
            simulation_returns[j, i] = np.round(port_val,2)
    return simulation_returns