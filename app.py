import streamlit as st
import numpy as np
from components.sidebar_inputs import sidebar_inputs
from components.main_body import main_content



np.random.seed(2345)

st. set_page_config(page_title="Investment Planning", page_icon="🧊",layout="wide",
                    initial_sidebar_state="expanded",
                    menu_items={'Get Help': 'https://www.fidelity.com/help',
                                'Report a bug': "mailto:support@example.com",
                                'About': "# This is a header. This is an *extremely* cool app!"})
st.markdown("#### Retirement plan (Monte Carlo) simulation 📈")
(future_years, total_ssn_earnings, total_incomes, yrly_expenses, starting_portfolio, portfolio_mix,
 sig_below_avg, below_avg, average, above_avg, distribution_option, inflation, COLA_rate, sim_runs) = sidebar_inputs()
main_content(future_years, total_ssn_earnings, total_incomes, yrly_expenses, starting_portfolio, portfolio_mix,
 sig_below_avg, below_avg, average, above_avg, distribution_option, inflation, COLA_rate, sim_runs)