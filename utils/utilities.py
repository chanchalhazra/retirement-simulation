from datetime import date, datetime
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import streamlit as st

def read_fit_data(path):
    #path = "../data/Stats_Table.csv"
    df = pd.read_csv(path)
    df = df.rename(columns={'Year': 'year', 'US Equity ': 'US_equity', 'US Bond ': 'US_bond'})
    df = df[['year', 'US_equity', 'US_bond']]
    mu_equity, sigma_equity = stats.norm.fit(df['US_equity'])
    #mu_equity_lognormal = mu_equity - 0.5 * sigma_equity ** 2
    print(f"For us equity normal distribution estimated - mu : {mu_equity} and sigma is {sigma_equity}")
    mu_bond, sigma_bond = stats.norm.fit(df['US_bond'])
    #mu_bond_lognormal = mu_bond - 0.5 * sigma_bond ** 2
    return df, mu_equity, sigma_equity, mu_bond, sigma_bond


def calculate_portfolio(start_val, expense, income, ssn_earning, eq_ret_rate, bd_ret_rate, tax_rate, portfolio_mix):
    # calculate total net inflow from SSN and any other income post tax
    amount_earned_after_tax = (ssn_earning * (1 - tax_rate)) + income * (1 - tax_rate)

    # if you need to withdraw additional money to cover expense, then you need to pay tax
    additional_withdrawal = (expense - amount_earned_after_tax)
    # tax_on_withdrawal = additional_withdrawal*tax_rate if additional_withdrawal >0 else 0

    # calculate investment income based on equity-bond ratio
    if additional_withdrawal > 0:
        tax_on_withdrawal = additional_withdrawal * tax_rate
        investment_income = (start_val - additional_withdrawal) * (
                    portfolio_mix * eq_ret_rate * 0.01 + (1 - portfolio_mix) * bd_ret_rate * 0.01)
    else:
        tax_on_withdrawal = 0
        investment_income = start_val * (portfolio_mix * eq_ret_rate * 0.01 + (1 - portfolio_mix) * bd_ret_rate * 0.01)
    # print(investment_income)

    # derive end of the year portfolio value
    end_portfolio_value = start_val + investment_income + amount_earned_after_tax - expense - tax_on_withdrawal
    '''
    df_portfolio = pd.DataFrame({'Starting Balance': start_val,
                                 'Investment Income': investment_income,
                                 'income': income,
                                 'SSN earning': ssn_earning,
                                 'Amount Earned After Tax': amount_earned_after_tax,
                                 'expense': expense,
                                 'additional_withdrawal': additional_withdrawal,
                                 'tax_on_withdrawal': tax_on_withdrawal,
                                 'Portfolio Value': end_portfolio_value})'''

    return end_portfolio_value


#simulation function

def monte_carlo_simulation(starting_portfolio, mu_equity, sigma_equity,mu_bond, sigma_bond, tax_rate, portfolio_mix,
                           return_df, yrly_expenses, total_incomes, total_ssn_earnings, distribution_type,
                           no_simulations, no_years):
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
                eq_return = np.random.choice(return_df['US_equity'])
                #print(f"eq return {eq_return}")
                bd_return = np.random.choice(return_df['US_bond'])
            #print(f"Bond return {bd_return}")
            port_val = calculate_portfolio(start_val=port_val, expense=yrly_expenses[j], income=total_incomes[j],
                                            ssn_earning=total_ssn_earnings[j], eq_ret_rate=eq_return, bd_ret_rate=bd_return,
                                           tax_rate=tax_rate, portfolio_mix=portfolio_mix)
            #print(f"port val {port_val}")
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

def print_outcomes(sim_returns,sim_returns_current, dist_type):
    sig_below_avg = np.ceil(np.percentile(sim_returns, 10, axis=1))
    below_avg = np.ceil(np.percentile(sim_returns, 25, axis=1))
    average = np.ceil(np.percentile(sim_returns, 50, axis=1))
    above_avg = np.ceil(np.percentile(sim_returns, 75, axis=1))
    #sim_returns_current = (sim_returns/((1+inflation*0.01)**future_years))
    sig_below_avg_current = np.ceil(np.percentile(sim_returns_current, 10, axis=1))
    below_avg_current = np.ceil(np.percentile(sim_returns_current, 25, axis=1))
    average_current = np.ceil(np.percentile(sim_returns_current, 50, axis=1))
    above_avg_current = np.ceil(np.percentile(sim_returns_current,75, axis=1))
    data = {
        "current $": [sig_below_avg_current[-1], below_avg_current[-1], average_current[-1], above_avg_current[-1]],
        "Future $": [sig_below_avg[-1], below_avg[-1], average[-1], above_avg[-1]]
    }
    data["current $"] = [f"{val:,.0f}" for val in data["current $"]]
    data["Future $"] = [f"{val:,.0f}" for val in data["Future $"]]
    indexes = ["Significantly Below Average", "Below Average", "Average", "Above Average"]
    df = pd.DataFrame(data, index=indexes)
    df.index.name = f"Using {dist_type} Distribution"
    #df = df.round(0)
    return df,sig_below_avg, below_avg, average, above_avg, sig_below_avg_current, below_avg_current, average_current, above_avg_current

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
def portfolio_yearly_dataframe(future_years,total_ssn_earnings, total_incomes,tax_rate,
                               yrly_expenses, starting_portfolio, ending_balances):
    current_year = datetime.now().year
    years = list(range(current_year, current_year + future_years))
    finance_df = pd.DataFrame(index=years)
    finance_df["SSN Earning"] = np.ceil(total_ssn_earnings)
    finance_df["Income"] = np.ceil(total_incomes)
    finance_df["Earning after Tax"] = np.ceil((finance_df["SSN Earning"] + finance_df["Income"]) * (1 - tax_rate))
    finance_df['expense'] = np.ceil(yrly_expenses)
    finance_df["Additional Withdrawal"] = (finance_df['expense'] - finance_df["Earning after Tax"])
    finance_df["ending balance"] = ending_balances
    finance_df["Start Balance"] = finance_df["ending balance"].shift(1).fillna(starting_portfolio)
    finance_df = finance_df[
        ["Start Balance", "Income", "SSN Earning", "Earning after Tax", 'expense', "Additional Withdrawal",
         "ending balance"]]

    return finance_df