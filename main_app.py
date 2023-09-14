import streamlit as st
import pandas as pd
from datetime import date
import plotly.express as px
import altair as alt
import os
import base64

logo_image = os.path.abspath("./app/static/marketing.bi_keboola.png")

logo_html = f"""<div style="display: flex; justify-content: flex-end;"><img src="data:image/png;base64,{base64.b64encode(open(logo_image, "rb").read()).decode()}" style="width: 100px; margin-left: -10px;"></div>"""
html_footer = f"""
 <div style="display: flex; justify-content: flex-end;margin-top: 12%">
        <div>
            <p><strong>Version:</strong> 1.1</p>
        </div>
         <div style="margin-left: auto;">
            <img src="data:image/png;base64,{base64.b64encode(open(logo_image, "rb").read()).decode()}" style="width: 400px;">
        </div>
    </div>
"""

# Set the page width
st.set_page_config(
    page_title="Google Universal Analytics vs GA4 Performance Comparison",
    layout="wide",  # Use "wide" layout for a wider page
    initial_sidebar_state="expanded"  # Expand the sidebar by default
)

# Title
 # Set up Streamlit container with title and logo
with st.container():
    st.markdown(f"{logo_html}", unsafe_allow_html=True)
    st.title("Google Universal Analytics vs GA4 performance comparison")

# Read data from CSV
df = pd.read_csv("/data/in/tables/COMPARISON.csv")
df["date"] = pd.to_datetime(df["date"]).dt.date
source = ["All sources"] + df["source"].unique().tolist()
medium = ["All mediums"] + df["medium"].unique().tolist()
campaign = ["All campaigns"] + df["campaign"].unique().tolist()

# Filters
with st.container():
    st.header("Filters")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", date(2023, 1, 1))
    with col2:    
        end_date = st.date_input("End Date", date(2023, 12, 31))
    source_selection = st.selectbox("Select a Source", options=source, key="source_selection")
    medium_selection = st.selectbox("Select a Medium", options=medium, key="medium_selection")
    campaign_selection = st.selectbox("Select a Campaign", options=campaign, key="campaign_selection")
    
    # Define filter conditions
    date_condition = (df['date'] >= start_date) & (df['date'] <= end_date)
    
    if source_selection != "All sources":
        source_condition = (df["source"] == source_selection)
    else:
        source_condition = True  # No filtering on source
    
    if medium_selection != "All mediums":
        medium_condition = (df["medium"] == medium_selection)
    else:
        medium_condition = True  # No filtering on medium
    
    if campaign_selection != "All campaigns":
        campaign_condition = (df["campaign"] == campaign_selection)
    else:
        campaign_condition = True  # No filtering on campaign
    
    # Apply the combined filter condition
    filtered_df = df[date_condition & source_condition & medium_condition & campaign_condition]
    # Display the filtered DataFrame or perform any actions with it

# Charts
with st.container():
    # Group and aggregate the data
    agg_df_users = filtered_df.groupby("date")[['ua_users', 'ga4api_users', 'ga4export_users', 'ga4_ua_users']].sum().reset_index()
    agg_df_sessions = filtered_df.groupby("date")[['ua_sessions', 'ga4api_sessions', 'ga4export_sessions', 'ga4_ua_sessions']].sum().reset_index()
    agg_df_transactions = filtered_df.groupby("date")[['ua_transactions', 'ga4api_transactions', 'ga4export_transactions', 'ga4_ua_transactions']].sum().reset_index()
    
    # Create Altair charts for each aggregation
    charts = []

    for agg_df, title in zip([agg_df_users, agg_df_sessions, agg_df_transactions], ['Users', 'Sessions', 'Transactions']):
        melted_df = pd.melt(agg_df, id_vars=['date'], var_name='source', value_name='value')

        chart = alt.Chart(melted_df).mark_line().encode(
            x='date:T',
            y=alt.Y('value:Q', axis=alt.Axis(title=title)),
            color='source:N',
            tooltip=['date:T', 'value:Q']
        ).properties(
            width=600,
            height=400,
            title=title
        )
        
        charts.append(chart)

    # Show the Altair charts using Streamlit
    for chart in charts:
        st.altair_chart(chart, use_container_width=True)

    agg_df_comparison = filtered_df.groupby("date")[['ga4_ua_users', 'ga4_ua_sessions', 'ga4_ua_transactions']].sum().reset_index()
    # Melt the DataFrame to reshape it
    melted_df_comparison = pd.melt(agg_df_comparison, id_vars=['date'], var_name='source', value_name='value')

    # Create an Altair grouped bar chart

    chart = alt.Chart(melted_df_comparison).mark_bar().encode(
        x='date:T',
        y=alt.Y('value:Q', axis=alt.Axis(title='Value')),
        color='source:N',
        tooltip=['date:T', 'value:Q']
    ).properties(
        width=600,
        height=400,
        title="GA4 metrics recalculated to GA UA methodology"
    )

    # Show the Altair grouped bar chart using the Streamlit Altair component
    st.altair_chart(chart, use_container_width=True)

# Display HTML footer
st.markdown(html_footer, unsafe_allow_html=True)

# Hide Made with streamlit from footer
hide_streamlit_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
        """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
