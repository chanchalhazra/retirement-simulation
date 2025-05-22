import streamlit as st
import numpy as np
import pandas as pd

# Sidebar
def sidebar_inputs():
    st.sidebar.header("Planning Inputs ⚙️")
    with st.sidebar.expander("Global Settings - Optional"):
        distribution_option = st.selectbox("Choose a model", ["normal", "empirical"])
        inflation = st.number_input("Average Inflation Rate (%)", min_value=0.0, max_value=10.0, value=2.5, step=0.1)
        COLA_rate = st.slider("SSN COLA Rate", 0.01, 3.0, value=1.5, step=0.01)
        sim_runs = st.number_input("No of simulations", min_value=1000, max_value=20000, value=1000)
    with_partner = st.sidebar.toggle("Plan includes Life Partner", value=True)
    with st.sidebar.expander("Personal Details"):
        if with_partner:
            col1, col2 = st.columns(2)
            with col1:
                person1_age = st.number_input("Your Age", min_value=0, max_value=120, value=57)
                person1_expectancy = st.number_input("Plan-to age", min_value=0, max_value=120, value=90)
                retire_at1 = st.number_input("Retire At", min_value=0, max_value=120, value=62)
            with col2:
                person2_age = st.number_input("Partner Age", min_value=0, max_value=120, value=51)
                person2_expectancy = st.number_input("(P)Plan-to age", min_value=0, max_value=120, value=90)
                retire_at2 = st.number_input("(P)Retire At", min_value=0, max_value=120, value=62)
        else:
            col1, col2 = st.columns(2)
            person2_age = 0.0
            person2_expectancy = 0.0
            with col1:
                person1_age = st.number_input("Your Age", min_value=0, max_value=120, value=57)
                person1_expectancy = st.number_input("Plan-to age", min_value=0, max_value=120,value=90)
            with col2:
                retire_at1 = st.number_input("Retire At", min_value=0, max_value=120, value=62)
        future_years = max((person1_expectancy - person1_age), (person2_expectancy - person2_age))

    with st.sidebar.expander("Income Details"):
        if with_partner:
            col1, col2 = st.columns(2)
            with col1:
                person1_income = st.number_input("Your Income", min_value=0, max_value=1200000)
                person1_ssn_income = st.number_input("SSN Income", min_value=0, max_value=60000, value=36000)
                person1_ssn_start_at = st.number_input("SSN drawing at", min_value=62, max_value=150, value=65)
            with col2:
                person2_income = st.number_input("Partner Income", min_value=0, max_value=1200000)
                person2_ssn_income = st.number_input("(P)SSN income", min_value=0, max_value=60000, value=28000)
                person2_ssn_start_at = st.number_input("SSN drawing at", min_value=62, max_value=150, value=62)
            yrs_before_ssn1 = person1_ssn_start_at - person1_age
            yrs_before_ssn2 = person2_ssn_start_at - person2_age
            person1_ssn_earnings = [
                round(person1_ssn_income * ((1 + 0.01 * COLA_rate) ** (i - yrs_before_ssn1)), 2) if i >= yrs_before_ssn1 else 0
                for i in range(future_years)]
            person2_ssn_earnings = [
                round(person2_ssn_income * ((1 + 0.01 * COLA_rate) ** (i - yrs_before_ssn2)), 2) if i >= yrs_before_ssn2 else 0
                for i in range(future_years)]
            total_ssn_earnings = [a + b for a, b in zip(person1_ssn_earnings, person2_ssn_earnings)]
            person1_incomes = [person1_income if i <= (retire_at1 - person1_age) else 0 for i in range(future_years)]
            person2_incomes = [person2_income if i <= (retire_at2 - person2_age) else 0 for i in range(future_years)]
            total_incomes = [a + b for a, b in zip(person1_incomes, person2_incomes)]
        else:
            col1, col2 = st.columns(2)
            with col1:
                person1_income = st.number_input("Your Income", min_value=0, max_value=120)
                person1_ssn_income = st.number_input("SSN Income", min_value=0, max_value=60000,value=24000)
            with col2:
                person1_ssn_start_at = st.number_input("SSN drawing at", min_value=62, max_value=150, value=65)
            yrs_before_ssn1 = person1_ssn_start_at - person1_age
            total_ssn_earnings = [round(person1_ssn_income * ((1 + 0.01 * COLA_rate) ** (i - yrs_before_ssn1)),2)
                                    if i >= yrs_before_ssn1 else 0 for i in range(future_years)]
            total_incomes = [person1_income if i <= (retire_at1 - person1_age) else 0 for i in range(future_years)]
    with st.sidebar.expander("Expenses"):
        detailed_expense = st.toggle("Detail your Expense")
        if detailed_expense:
            col1, col2 = st.columns(2)
            with col1:
                mortgage = st.number_input("Yearly Mortgage", min_value=0, max_value=300000, value=0)
                property_tax = st.number_input("Property Tax", min_value=0, max_value=100000, value=0)
                utility_expense = st.number_input("Utility expenses", min_value=0, max_value=100000, value=0)
                entertainment = st.number_input("Entertainment", min_value=0, max_value=100000, value=0)
            with col2:
                mortgage_years = st.number_input("Years left", min_value=0, max_value=30)
                property_insurance = st.number_input("Property Insurance", min_value=0, max_value=120000)
                food_expense = st.number_input("Food", min_value=0, max_value=120000)
                travel_expense = st.number_input("Travel", min_value=0, max_value=120000)
            total_expense = mortgage+property_tax+property_insurance+utility_expense+entertainment+food_expense+travel_expense
        else:
            essential_expense = st.number_input("Essential Expense including mortgage", min_value=0,
                                                max_value=1200000, value=120000)
            non_essential_expense = st.number_input("Non Essential Expense like Travel", min_value=0,
                                                    max_value=1200000, value=20000)
            total_expense = essential_expense+non_essential_expense
        st.write(f"Total expense: {total_expense}")
        yrly_expenses = [total_expense * (1 + 0.01 * inflation) ** i for i in range(future_years)]

    with st.sidebar.expander("Savings and Investment"):
        starting_portfolio = st.number_input("Starting Portfolio", min_value=0, max_value=12000000,value=3000000)
        portfolio_mix = st.slider("Equity percentage", min_value=0.0, max_value=100.0, value=80.0, step=1.0)

    with st.sidebar.expander("Planning Scenarios"):
        sig_below_avg = st.slider("Significant Below Average - 90% cases perform better", min_value=0.0, max_value=100.0, value=10.0)
        below_avg = st.slider("Below Average - 75% cases perform better", min_value=0.0, max_value=100.0, value=25.0)
        average = st.slider("Average - most likely 50% cases performs better", min_value=0.0, max_value=100.0, value=50.0)
        above_avg = st.slider("Above Average 25% cases perform better", min_value=0.0, max_value=100.0, value=75.0)
    '''
# --- File Upload and Buttons ---
    st.sidebar.subheader("📎 File and Action Inputs")
    uploaded_file = st.sidebar.file_uploader("Upload the inputs file")
    if uploaded_file:
        st.sidebar.write("Uploaded file:", uploaded_file.name)
    
    if st.sidebar.button("Run Simulation"):
        st.sidebar.write("You clicked the button!")

    # --- Session State Example ---
    if "clicks" not in st.session_state:
        st.session_state.clicks = 0

    if st.sidebar.button("➕ Increment Counter"):
        st.session_state.clicks += 1
    '''
    #st.sidebar.write("🔢 Counter value:", st.session_state.clicks)
    return (future_years, total_ssn_earnings,total_incomes, yrly_expenses, starting_portfolio, portfolio_mix,
            sig_below_avg, below_avg, average, above_avg, distribution_option, inflation, COLA_rate, sim_runs)
