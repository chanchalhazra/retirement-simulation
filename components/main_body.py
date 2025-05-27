import streamlit as st
import numpy as np
from utils.utilities import (read_fit_data, print_outcomes,
                             monte_carlo_simulation, portfolio_yearly_dataframe)
from utils.estimate_tax import estimate_retirement_tax
from components.main_details import component_yrly_balances
from utils.optimize_portfolio_mix import optimize_portfolio_mix

def main_content(filing, future_years, total_ssn_earnings, total_incomes, total_401K_contributions, yrly_expenses, starting_portfolio, portfolio_mix,
            sig_below_avg, below_avg, average, above_avg, distribution_option,inflation, COLA_rate, sim_runs,
                 estimated_yrly_taxes, residing_state, est_statetax_rate):
    # Read the data and fit the data to ding mu and sigma
    path = "./data/Stats_Table.csv"
    return_df, mu_fitted_equity, sigma_fitted_equity, mu_fitted_bond, sigma_fitted_bond = read_fit_data(path)
    np.random.seed(2345)
    #if total_incomes
    with st.expander("**🛠 Optionally tune these parameters, that are derived using past 100 years of market data**", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            mu_equity = st.number_input("Equity market return", 0.0, 20.0, mu_fitted_equity, step=0.1)
            sigma_equity = st.number_input("Equity return std deviation)", 0.0, 20.0, sigma_fitted_equity, step=0.1)
        with col2:
            mu_bond = st.number_input("Bond market return", 0.0,20.0,mu_fitted_bond, step=0.1)
            sigma_bond= st.number_input("Bond return std deviation", 0.0, 20.0, sigma_fitted_bond, step=0.1)
        with col3:
            portfolio_mix = 0.01*st.number_input("Adjust Portfolio Equity(%)", min_value=0.0, max_value=100.0, value=portfolio_mix, step=1.0)
            expense_reduction = 0.01*st.number_input("Reduce expenses by(%)", min_value=0.0, max_value=100.0, value=0.0,step=1.0)
            if expense_reduction > 0.0:
                total_expense = yrly_expenses[0]*(1-expense_reduction)
                yrly_expenses = [total_expense * (1 + 0.01 * inflation) ** i for i in range(future_years)]

        st.write(f"Starting portfolio balance: {f"{starting_portfolio:,.0f}"}"
                 f" | Starting yearly expense {f"{yrly_expenses[0]:,.0f}"}  | {residing_state} Resident, estimated state tax rate {est_statetax_rate}")

    # Run simulations and calculate port folio
    tax_rate = 0.1
    sim_returns = monte_carlo_simulation(starting_portfolio, mu_equity, sigma_equity, mu_bond, sigma_bond, est_statetax_rate, portfolio_mix,
                           return_df, yrly_expenses, total_incomes, total_ssn_earnings, distribution_type='normal',
                           no_simulations=sim_runs, no_years=future_years, retirement_contributions=total_401K_contributions,
                                         filing=filing, estimated_yrly_taxes=estimated_yrly_taxes)

    #sim_returns_current = [sim_returns[i]/((1+inflation*0.01)**(i+1)) for i in range(future_years)]
    # Empirical simulation
    sim_returns_empirical = monte_carlo_simulation(starting_portfolio, mu_equity, sigma_equity, mu_bond, sigma_bond,est_statetax_rate, portfolio_mix,
                                         return_df, yrly_expenses, total_incomes, total_ssn_earnings, distribution_type='empirical',
                                         no_simulations=sim_runs, no_years=future_years, retirement_contributions=total_401K_contributions,
                                         filing=filing, estimated_yrly_taxes=estimated_yrly_taxes)
    #sim_returns_empirical_current = [sim_returns_empirical[i]/((1 + inflation * 0.01)**(i+1)) for i in range(future_years)]
    #Display results
    df, sim_returns_percentiles, sim_returns_current_percentiles = print_outcomes(sim_returns,inflation, dist_type="normal")
    df_emp, sim_returns_percentiles_emp, sim_returns_current_percentiles_emp = print_outcomes(sim_returns_empirical,inflation,
                                                                                         dist_type="empirical")
    # Future value to current value conversion factors with average inflation
    #current_value_factors = np.array([(1 + inflation * 0.01) ** (i + 1) for i in range(future_years)])
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
        distribution = st.radio("Probability Distribution choice", ("normal", "empirical"))
    #create details dataframes
    if distribution == "normal":
        if currency == "future":
            sig_below_avg_df = portfolio_yearly_dataframe(future_years,total_ssn_earnings, total_incomes, estimated_yrly_taxes,
                                                          yrly_expenses, starting_portfolio,
                                                          ending_balances=sim_returns_percentiles["sig_below_avg"])

            below_avg_df = portfolio_yearly_dataframe(future_years, total_ssn_earnings, total_incomes, estimated_yrly_taxes,
                                                          yrly_expenses, starting_portfolio, ending_balances=sim_returns_percentiles["below_avg"])

            avg_df = portfolio_yearly_dataframe(future_years, total_ssn_earnings, total_incomes, estimated_yrly_taxes, yrly_expenses,
                                                starting_portfolio, ending_balances=sim_returns_percentiles["average"])

            above_avg_df = portfolio_yearly_dataframe(future_years, total_ssn_earnings, total_incomes, estimated_yrly_taxes,
                                                           yrly_expenses, starting_portfolio,ending_balances=sim_returns_percentiles["above_avg"])
        else:
            #sig_below_avg_current = [sig_below_avg[i] / ((1 + inflation * 0.01) ** (i + 1)) for i in range(future_years)]
            sig_below_avg_df = portfolio_yearly_dataframe(future_years, total_ssn_earnings, total_incomes, estimated_yrly_taxes,
                                                           yrly_expenses, starting_portfolio,
                                                          ending_balances=sim_returns_current_percentiles["sig_below_avg"])

            below_avg_df = portfolio_yearly_dataframe(future_years, total_ssn_earnings, total_incomes, estimated_yrly_taxes,
                                                      yrly_expenses, starting_portfolio,
                                                      ending_balances=sim_returns_current_percentiles["below_avg"])

            avg_df = portfolio_yearly_dataframe(future_years, total_ssn_earnings, total_incomes, estimated_yrly_taxes,
                                                yrly_expenses, starting_portfolio,
                                                ending_balances=sim_returns_current_percentiles["average"])

            above_avg_df = portfolio_yearly_dataframe(future_years, total_ssn_earnings, total_incomes, estimated_yrly_taxes,
                                                      yrly_expenses, starting_portfolio,
                                                      ending_balances=sim_returns_current_percentiles["above_avg"])
    elif distribution == "empirical":
        if currency == "future":
            sig_below_avg_df = portfolio_yearly_dataframe(future_years, total_ssn_earnings, total_incomes, estimated_yrly_taxes,
                                                          yrly_expenses, starting_portfolio,
                                                          ending_balances=sim_returns_percentiles_emp["sig_below_avg"])

            below_avg_df = portfolio_yearly_dataframe(future_years, total_ssn_earnings, total_incomes, estimated_yrly_taxes,
                                                      yrly_expenses, starting_portfolio,
                                                      ending_balances=sim_returns_percentiles_emp["below_avg"])

            avg_df = portfolio_yearly_dataframe(future_years, total_ssn_earnings, total_incomes, estimated_yrly_taxes,
                                                yrly_expenses, starting_portfolio,
                                                ending_balances=sim_returns_percentiles_emp["average"])

            above_avg_df = portfolio_yearly_dataframe(future_years, total_ssn_earnings, total_incomes, estimated_yrly_taxes,
                                                      yrly_expenses, starting_portfolio,
                                                      ending_balances=sim_returns_percentiles_emp["above_avg"])
        else:
            sig_below_avg_df = portfolio_yearly_dataframe(future_years, total_ssn_earnings, total_incomes, estimated_yrly_taxes,
                                                          yrly_expenses, starting_portfolio,
                                                          ending_balances=sim_returns_current_percentiles_emp["sig_below_avg"])

            below_avg_df = portfolio_yearly_dataframe(future_years, total_ssn_earnings, total_incomes, estimated_yrly_taxes,
                                                      yrly_expenses, starting_portfolio,
                                                      ending_balances=sim_returns_current_percentiles_emp["below_avg"])

            avg_df = portfolio_yearly_dataframe(future_years, total_ssn_earnings, total_incomes, estimated_yrly_taxes,
                                                yrly_expenses, starting_portfolio,
                                                ending_balances=sim_returns_current_percentiles_emp["average"])

            above_avg_df = portfolio_yearly_dataframe(future_years, total_ssn_earnings, total_incomes, estimated_yrly_taxes,
                                                      yrly_expenses, starting_portfolio,
                                                      ending_balances=sim_returns_current_percentiles_emp["above_avg"])

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
