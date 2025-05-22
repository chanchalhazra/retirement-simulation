import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# Sidebar or main input area
st.title("Portfolio Optimization")
equity = st.slider("Equity Allocation (%)", 0, 100, 60)
bonds = 100 - equity
st.write(f"Portfolio Mix: {equity}% Equity, {bonds}% Bonds")

# Button to trigger optimization
if st.button("Run Optimization"):
    # Simulate optimization result (replace with your real function)
    years = np.arange(0, 30)
    portfolio_value = 100000 * (1 + equity / 100 * 0.07 + bonds / 100 * 0.03) ** years

    # Create a plot
    fig, ax = plt.subplots()
    ax.plot(years, portfolio_value)
    ax.set_title("Projected Portfolio Growth")
    ax.set_xlabel("Years")
    ax.set_ylabel("Portfolio Value ($)")
    ax.grid(True)

    # Show result in modal
    with st.modal("Optimization Results", key="opt_result"):
        st.pyplot(fig)
        st.write("This curve represents projected portfolio growth based on your asset allocation.")