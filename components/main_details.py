
import streamlit as st
import numpy as np
import pandas as pd

def component_yrly_balances(df1, df2, df3, df4):
    with st.container():
        #st.markdown("#### Portfolio Detailed Table")
        tab1, tab2, tab3, tab4 = st.tabs(["Significantly Below Average", "Below Average", "Average", "Best Case"])
        with tab1:
            st.caption("90% of simulated market returns are better than these returns")
            st.dataframe(df1,use_container_width=True)
            st.bar_chart(df1[["ending balance","expense"]],use_container_width=True)

        with tab2:
            st.caption("75% of simulated market returns are better than these returns")
            st.dataframe(df2, use_container_width=True)
            st.bar_chart(df2[["ending balance","expense"]], use_container_width=True)

        with tab3:
            st.caption("50% of simulated market returns are better than this value")
            st.dataframe(df3, use_container_width=True)
            st.bar_chart(df3[["ending balance","expense"]], use_container_width=True)

        with tab4:
            st.caption("75% of simulated market returns are better than this value")
            st.dataframe(df4, use_container_width=True)
            st.bar_chart(df4[["ending balance","expense"]], use_container_width=True)