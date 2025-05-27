from datetime import date, datetime
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import streamlit as st
from utils.estimate_tax import estimate_retirement_tax

def read_fit_data(path):
    #path = "../data/Stats_Table.csv"
    df = pd.read_csv(path)
    df = df.rename(columns={'Year': 'year', 'US Equity ': 'US_equity', 'US Bond ': 'US_bond'})
    df = df[['year', 'US_equity', 'US_bond']]
    mu_equity, sigma_equity = stats.norm.fit(df['US_equity'])
    #mu_equity_lognormal = mu_equity - 0.5 * sigma_equity ** 2
    #print(f"For us equity normal distribution estimated - mu : {mu_equity} and sigma is {sigma_equity}")
    mu_bond, sigma_bond = stats.norm.fit(df['US_bond'])
    #mu_bond_lognormal = mu_bond - 0.5 * sigma_bond ** 2
    return df, mu_equity, sigma_equity, mu_bond, sigma_bond


def calculate_portfolio(start_val, expense, income, ssn_earning, investment_return,
                        state_tax_rate, retirement_contribution, filing, estimated_yrly_tax):
    # calculate total net inflow from SSN and any other income post tax
    '''
    estimated_tax = estimate_retirement_tax(income=income, expense=expense, ssn_earning=ssn_earning,
                                            retirement_contribution=retirement_contribution,
                                            filing=filing, state_tax_rate=state_tax_rate)'''
    amount_earned_after_tax = (ssn_earning + income - estimated_yrly_tax)

    # if you need to withdraw additional money to cover expense, then you need to pay tax
    additional_withdrawal = (expense - amount_earned_after_tax)

    # calculate investment income based on equity-bond ratio
    if additional_withdrawal > 0:
        #tax_on_withdrawal = additional_withdrawal * tax_rate
        investment_income = (start_val - additional_withdrawal) * investment_return
    else:
        tax_on_withdrawal = 0
        investment_income = start_val * investment_return
    # derive end of the year portfolio value
    end_portfolio_value = start_val + investment_income + amount_earned_after_tax - expense

    return end_portfolio_value


#simulation function

def monte_carlo_simulation(starting_portfolio, mu_equity, sigma_equity,mu_bond, sigma_bond, state_tax_rate, portfolio_mix,
                           return_df, yrly_expenses, total_incomes, total_ssn_earnings, distribution_type,
                           no_simulations, no_years, retirement_contributions, filing, estimated_yrly_taxes):
    #initilize simulation returns as Numpy arrays
    simulation_returns = np.zeros((no_years, no_simulations))
    for i in range(no_simulations):
        port_val = starting_portfolio
        #expense = yrly_expense
        for j in range(no_years):
            if distribution_type == 'normal':
                eq_return = np.random.normal(mu_equity, sigma_equity)
                bd_return = np.random.normal(mu_bond, sigma_bond)
            elif distribution_type == 'empirical': #empirical distribution
                eq_return = np.random.choice(return_df['US_equity'])
                bd_return = np.random.choice(return_df['US_bond'])
            return_rate = (portfolio_mix * eq_return * 0.01 + (1 - portfolio_mix) * bd_return * 0.01)
            port_val = calculate_portfolio(start_val=port_val, expense=yrly_expenses[j], income=total_incomes[j],
                                           ssn_earning=total_ssn_earnings[j], investment_return=return_rate,
                                           state_tax_rate=state_tax_rate, retirement_contribution=retirement_contributions[j],
                                           filing=filing, estimated_yrly_tax=estimated_yrly_taxes[j])
            simulation_returns[j, i] = np.round(port_val,2)
    return simulation_returns

# simulation function choosing choices in bulk but not much time difference
def monte_carlo_simulation_bulk(starting_portfolio, mu_equity, sigma_equity,mu_bond, sigma_bond, tax_rate, portfolio_mix,
                           return_df, yrly_expenses, total_incomes, total_ssn_earnings, distribution_type='normal',
                           no_simulations=10000, no_years=30):
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

def print_outcomes(sim_returns, inflation, dist_type):
    sim_returns_percentiles = {}
    sim_returns_current_percentiles = {}
    sim_returns_percentiles["sig_below_avg"] = np.ceil(np.percentile(sim_returns, 10, axis=1))
    sim_returns_percentiles["below_avg"] = np.ceil(np.percentile(sim_returns, 25, axis=1))
    sim_returns_percentiles["average"] = np.ceil(np.percentile(sim_returns, 50, axis=1))
    sim_returns_percentiles["above_avg"] = np.ceil(np.percentile(sim_returns, 75, axis=1))
    sim_returns_current = [sim_returns[i] / ((1 + inflation * 0.01) ** (i + 1)) for i in range(len(sim_returns))]

    sim_returns_current_percentiles["sig_below_avg"] = np.ceil(np.percentile(sim_returns_current, 10, axis=1))
    sim_returns_current_percentiles["below_avg"] = np.ceil(np.percentile(sim_returns_current, 25, axis=1))
    sim_returns_current_percentiles["average"] = np.ceil(np.percentile(sim_returns_current, 50, axis=1))
    sim_returns_current_percentiles["above_avg"] = np.ceil(np.percentile(sim_returns_current,75, axis=1))
    data = {
        "current $": [sim_returns_current_percentiles["sig_below_avg"][-1], sim_returns_current_percentiles["below_avg"][-1],
                      sim_returns_current_percentiles["average"][-1], sim_returns_current_percentiles["above_avg"][-1]],
        "Future $": [sim_returns_percentiles["sig_below_avg"][-1], sim_returns_percentiles["below_avg"][-1],
                     sim_returns_percentiles["average"][-1], sim_returns_percentiles["above_avg"][-1]]
    }
    data["current $"] = [f"{val:,.0f}" for val in data["current $"]]
    data["Future $"] = [f"{val:,.0f}" for val in data["Future $"]]
    indexes = ["Significantly Below Average Market Return", "Below Average Market Return", "Average Market Return", "Best Case Market Return"]
    df = pd.DataFrame(data, index=indexes)
    df.index.name = f"Model: {dist_type} Distribution"
    #df = df.round(0)
    return df,sim_returns_percentiles, sim_returns_current_percentiles

def plot_portfolio(portfolio, case, inCurrentDoller=True):
    current_year = date.today().year
    future_years = [current_year+i for i in range(len(portfolio))]
    fig, ax = plt.subplots(figsize=(10,6))
    ax.plot(future_years, portfolio, color='blue')
    ax.set_xlabel('Year')
    ax.set_ylabel('Portfolio Value')
    val = 'current($)' if inCurrentDoller else 'future($)'
    ax.set_title(f'Portfolio Value for {case} in {val}')
    st.pyplot(fig)

#create detailed portfolio dataframe
def portfolio_yearly_dataframe(future_years,total_ssn_earnings, total_incomes,estimated_taxes,
                               yrly_expenses, starting_portfolio, ending_balances ):
    current_year = datetime.now().year
    years = list(range(current_year, current_year + future_years))
    finance_df = pd.DataFrame(index=years)
    finance_df["SSN Earning"] = np.ceil(total_ssn_earnings)
    finance_df["Income"] = np.ceil(total_incomes)
    finance_df["Estimated Tax"] = np.ceil(estimated_taxes)
    finance_df["Earning after Tax"] = np.round((finance_df["SSN Earning"] + finance_df["Income"] - finance_df["Estimated Tax"]),0)
    finance_df['Total Expense'] = np.ceil(yrly_expenses)
    finance_df["Additional Withdrawal"] = np.maximum(0.0,(finance_df['Total Expense'] - finance_df["Earning after Tax"]))
    finance_df["Ending Balance"] = ending_balances
    finance_df["Start Balance"] = finance_df["Ending Balance"].shift(1).fillna(starting_portfolio)
    finance_df = finance_df[
        ["Start Balance", "Income", "SSN Earning","Estimated Tax", "Earning after Tax", 'Total Expense', "Additional Withdrawal",
         "Ending Balance"]]

    return finance_df