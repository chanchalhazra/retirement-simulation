import streamlit as st
import numpy as np
from utils.utilities import (read_fit_data, print_outcomes,
                             monte_carlo_simulation, portfolio_yearly_dataframe)
from components.main_details import component_yrly_balances

def main_content(future_years, total_ssn_earnings, total_incomes, yrly_expenses, starting_portfolio, portfolio_mix,
            sig_below_avg, below_avg, average, above_avg, distribution_option,inflation, COLA_rate, sim_runs):
    # Read the data and fit the data to ding mu and sigma
    path = "./data/Stats_Table.csv"
    return_df, mu_fitted_equity, sigma_fitted_equity, mu_fitted_bond, sigma_fitted_bond = read_fit_data(path)
    np.random.seed(2345)
    with st.expander("**Optionally tune these parameters  🛠️ observe the impact to your portfolio**", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            mu_equity = st.number_input("Equity market return", 0.0, 20.0, mu_fitted_equity)
            sigma_equity = st.number_input("Equity return variation(%)", 0.0, 20.0, sigma_fitted_equity)
        with col2:
            mu_bond = st.number_input("Bond market return", 0.0,20.0,mu_fitted_bond)
            sigma_bond= st.number_input("Bond return variation(%)", 0.0, 20.0, sigma_fitted_bond)
        with col3:
            portfolio_mix = st.number_input("Portfolio Equity(%)", min_value=0.0, max_value=1.0, value=portfolio_mix, step=0.1)
            expense_reduction = st.number_input("Reduce expenses by(%)-not used yet", min_value=0.0, max_value=100.0, value=2.5, step=0.1)

        with col4:
            tax_rate = 0.01*st.slider("Effective Income Tax Rate %", min_value=0, max_value=50, value=10, step=1)
            cap_gain_tax_rate = st.slider("Capital Gain Tax Rate %(not used yet)", min_value=0, max_value=50, value=10, step=1)
        st.write(f"Starting investment portfolio balance: {starting_portfolio} | Yearly expense {yrly_expenses[0]} ")
    # Run simulations and calculate port folio
    sim_returns = monte_carlo_simulation(starting_portfolio, mu_equity, sigma_equity, mu_bond, sigma_bond, tax_rate, portfolio_mix,
                           return_df, yrly_expenses, total_incomes, total_ssn_earnings, distribution_type='normal',
                           no_simulations=sim_runs, no_years=future_years)
    sim_returns_current = (sim_returns / ((1 + inflation * 0.01) ** future_years))
    # Empirical simulation
    sim_returns_empirical = monte_carlo_simulation(starting_portfolio, mu_equity, sigma_equity, mu_bond, sigma_bond, tax_rate, portfolio_mix,
                                         return_df, yrly_expenses, total_incomes, total_ssn_earnings, distribution_type='empirical',
                                         no_simulations=sim_runs, no_years=future_years)
    sim_returns_empirical_current = (sim_returns_empirical / ((1 + inflation * 0.01) ** future_years))
    #Display results
    df,sig_below_avg, below_avg, average, above_avg, sig_below_avg_current, below_avg_current, average_current, above_avg_current = print_outcomes(sim_returns, sim_returns_current, dist_type="normal")
    df_emp, sig_below_avg_emp, below_avg_emp, average_emp, above_avg_emp, sig_below_avg_emp_current, below_avg_emp_current, average_emp_current, above_avg_emp_current= print_outcomes(sim_returns_empirical, sim_returns_empirical_current, dist_type="empirical")
    with st.container():
        st.markdown("#### Portfolio Ending Balance")
        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(df, use_container_width=False)
        with col2:
            st.dataframe(df_emp, use_container_width=False)

    # create the dataframe of cash flow and investment return
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("#### Portfolio Detailed Table")
    with col2:
        currency = st.radio("In current or Future value", ("current", "future"))
    with col3:
        distribution = st.radio("Probability Distribution", ("normal", "empirical"))
    #create details dataframes
    if distribution == "normal":
        if currency == "future":
            sig_below_avg_df = portfolio_yearly_dataframe(future_years,total_ssn_earnings, total_incomes,tax_rate,
                               yrly_expenses, starting_portfolio, ending_balances=sig_below_avg)
            below_avg_df = portfolio_yearly_dataframe(future_years, total_ssn_earnings, total_incomes, tax_rate,
                                                          yrly_expenses, starting_portfolio,
                                                          ending_balances=below_avg)
            avg_df = portfolio_yearly_dataframe(future_years, total_ssn_earnings, total_incomes, tax_rate, yrly_expenses,
                                                starting_portfolio, ending_balances=average)
            above_avg_df = portfolio_yearly_dataframe(future_years, total_ssn_earnings, total_incomes, tax_rate,
                                                          yrly_expenses, starting_portfolio,
                                                          ending_balances=above_avg)
        else:
            sig_below_avg_df = portfolio_yearly_dataframe(future_years, total_ssn_earnings, total_incomes, tax_rate,
                                                          yrly_expenses, starting_portfolio,
                                                          ending_balances=sig_below_avg_current)
            below_avg_df = portfolio_yearly_dataframe(future_years, total_ssn_earnings, total_incomes, tax_rate,
                                                      yrly_expenses, starting_portfolio,
                                                      ending_balances=below_avg_current)
            avg_df = portfolio_yearly_dataframe(future_years, total_ssn_earnings, total_incomes, tax_rate,
                                                yrly_expenses,
                                                starting_portfolio, ending_balances=average_current)
            above_avg_df = portfolio_yearly_dataframe(future_years, total_ssn_earnings, total_incomes, tax_rate,
                                                      yrly_expenses, starting_portfolio,
                                                      ending_balances=above_avg_current)
    elif distribution == "empirical":
        if currency == "future":
            sig_below_avg_df = portfolio_yearly_dataframe(future_years, total_ssn_earnings, total_incomes, tax_rate,
                                                          yrly_expenses, starting_portfolio, ending_balances=sig_below_avg_emp)
            below_avg_df = portfolio_yearly_dataframe(future_years, total_ssn_earnings, total_incomes, tax_rate,
                                                      yrly_expenses, starting_portfolio,
                                                      ending_balances=below_avg_emp)
            avg_df = portfolio_yearly_dataframe(future_years, total_ssn_earnings, total_incomes, tax_rate,
                                                yrly_expenses, starting_portfolio,
                                                ending_balances=average_emp)
            above_avg_df = portfolio_yearly_dataframe(future_years, total_ssn_earnings, total_incomes, tax_rate,
                                                  yrly_expenses, starting_portfolio,
                                                  ending_balances=above_avg_emp)
        else:
            sig_below_avg_df = portfolio_yearly_dataframe(future_years, total_ssn_earnings, total_incomes, tax_rate,
                                                          yrly_expenses, starting_portfolio,
                                                          ending_balances=sig_below_avg_emp_current)
            below_avg_df = portfolio_yearly_dataframe(future_years, total_ssn_earnings, total_incomes, tax_rate,
                                                      yrly_expenses, starting_portfolio,
                                                      ending_balances=below_avg_emp_current)
            avg_df = portfolio_yearly_dataframe(future_years, total_ssn_earnings, total_incomes, tax_rate,
                                                yrly_expenses, starting_portfolio,
                                                ending_balances=average_emp_current)
            above_avg_df = portfolio_yearly_dataframe(future_years, total_ssn_earnings, total_incomes, tax_rate,
                                                      yrly_expenses, starting_portfolio,
                                                      ending_balances=above_avg_emp_current)

    component_yrly_balances(sig_below_avg_df, below_avg_df, avg_df, above_avg_df)

    '''
    # --- Form Section ---
    with st.form("user_form"):
        st.subheader("🧍 User Information")

        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First Name")
            age = st.number_input("Age", min_value=0, max_value=120)
            birth_date = st.date_input("Birth Date")
        with col2:
            last_name = st.text_input("Last Name")
            gender = st.radio("Gender", ["Male", "Female", "Other"])
            time = st.time_input("Preferred Contact Time")

        # Submit Button
        submitted = st.form_submit_button("Submit")
        if submitted:
            st.success(f"Hello, {first_name} {last_name} ({age} yrs), born on {birth_date}.")
            st.info(f"Gender: {gender}, Preferred Time: {time}")
    '''
