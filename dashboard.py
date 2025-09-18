import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="Coffee Sales Dashboard",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_data():
    # Load the dataset
    data = pd.read_csv('data/Coffe_sales.csv')

    # Calculate total sales
    data['total_sales'] = data['money']

    # Add day of week and month
    data['Date'] = pd.to_datetime(data['Date'])
    data['day_of_week'] = data['Weekday']
    data['month'] = data['Month_name']

    # Extract hour from hour_of_day
    data['hour'] = data['hour_of_day']

    # Use Time_of_Day from CSV
    data['time_of_day'] = data['Time_of_Day']

    # No payment method needed

    # Product line from coffee_name
    data['product_line'] = data['coffee_name']

    # For temporal analysis
    data['month_year'] = data['Date'].dt.to_period('M').astype(str)

    return data

data = load_data()


# Ensure date column is datetime
if 'Date' in data.columns:
    data['year'] = data['Date'].dt.year
    data['month_num'] = data['Date'].dt.month

# Sidebar filters
st.sidebar.title("Filters")
st.sidebar.markdown("---")

# Date range filter
if 'Date' in data.columns:
    min_date = data['Date'].min()
    max_date = data['Date'].max()

    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        data = data[(data['Date'].dt.date >= start_date) & (data['Date'].dt.date <= end_date)]

# Product filter
if 'product_line' in data.columns:
    products = st.sidebar.multiselect(
        "Select Products",
        options=data['product_line'].unique(),
        default=data['product_line'].unique()
    )
    data = data[data['product_line'].isin(products)]

# Main dashboard
st.title("☕ Coffee Sales Dashboard")
st.markdown("---")

# Key metrics section
st.subheader("Key Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    # Calculate total sales
    total_sales = data['total_sales'].sum() if 'total_sales' in data.columns else 0
    st.metric(label="Total Sales", value=f"${total_sales:,.2f}")


with col2:
    total_orders = data.shape[0]
    st.metric(label="Number of Transactions", value=f"{total_orders:,}")

with col3:
    avg_ticket = data['total_sales'].mean() if 'total_sales' in data.columns and total_orders > 0 else 0
    st.metric(label="Average Ticket", value=f"${avg_ticket:,.2f}")

with col4:
    if 'product_line' in data.columns:
        popular_product = data['product_line'].value_counts().index[0] if not data.empty else "N/A"
        st.metric(label="Most Popular Product", value=popular_product)

st.markdown("---")

# First row of charts
st.subheader("Sales Analysis")
col1, col2 = st.columns(2)

with col1:
    # 📊 Sales by Coffee Type
    if 'product_line' in data.columns and 'total_sales' in data.columns:
        sales_by_product = data.groupby('product_line')['total_sales'].sum().reset_index()
        sales_by_product = sales_by_product.sort_values('total_sales', ascending=False)
        
        fig = px.bar(
            sales_by_product, 
            x='product_line', 
            y='total_sales',
            title="📊 Sales by Coffee Type",
            color='product_line',
            labels={'product_line': 'Product:', 'total_sales': 'Total Sales ($)'}
        )
        fig.update_layout(showlegend=False, 
                            yaxis_tickprefix='$',
                            yaxis_tickformat=',.0f'
                          )
        fig.update_traces(
        hovertemplate='<b>Product:</b> %{x}<br><b>Sales:</b> $%{y:,.0f}<extra></extra>'
    )
        st.plotly_chart(fig, use_container_width=True)

with col2:
    # ⏰ Sales by Hour of Day
    if 'hour' in data.columns and 'total_sales' in data.columns:
        sales_by_hour = data.groupby('hour')['total_sales'].sum().reset_index()
        
        fig = px.line(
            sales_by_hour,
            x='hour',
            y='total_sales',
            title="⏰ Sales by Hour of Day",
            labels={'hour': 'Product:', 'total_sales': 'Total Sales ($)'}
        )
        fig.update_layout(xaxis=dict(tickmode='linear', dtick=1))
        fig.update_traces(hovertemplate='<b>Product:</b> %{x}<br><b>Sales:</b> $%{y:,.0f}<extra></extra>')
        st.plotly_chart(fig, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    # 🌅 Sales by Time of Day
    if 'time_of_day' in data.columns and 'total_sales' in data.columns:
        time_order = ['Morning', 'Afternoon', 'Evening', 'Night']
        sales_by_tod = data.groupby('time_of_day')['total_sales'].sum().reset_index()
        sales_by_tod['time_of_day'] = pd.Categorical(sales_by_tod['time_of_day'], categories=time_order, ordered=True)
        sales_by_tod = sales_by_tod.sort_values('time_of_day')
        
        fig = px.pie(
            sales_by_tod,
            values='total_sales',
            names='time_of_day',
            title="🌅 Sales by Time of Day",
            hole=0.4
        )
        fig.update_traces(textposition='inside', textinfo='percent+label',
                          hovertemplate='<b>Product:</b> %{label}<br><b>Sales:</b> $%{value:,.0f}<extra></extra>')
        st.plotly_chart(fig, use_container_width=True)

# Third row of charts
st.subheader("Temporal Analysis")
col1, col2 = st.columns(2)

with col1:
    # 📅 Sales by Weekday
    if 'Weekday' in data.columns and 'total_sales' in data.columns:
        day_order = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        full_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        # Map short weekday names to full names
        weekday_map = dict(zip(day_order, full_names))
        # Replace values in Weekday column
        data['Weekday_full'] = data['Weekday'].map(weekday_map)
        # Group by full names
        sales_by_weekday = data.groupby('Weekday_full')['total_sales'].sum().reindex(full_names).reset_index()
        sales_by_weekday = sales_by_weekday.rename(columns={'Weekday_full': 'Weekday'})

        if sales_by_weekday['total_sales'].sum() == 0 or sales_by_weekday.empty:
            st.info("No sales data available for weekdays in the selected range.")
        else:
            fig = px.bar(
                sales_by_weekday,
                x='Weekday',
                y='total_sales',
                title="📅 Sales by Weekday",
                labels={'Weekday': 'Product:', 'total_sales': 'Total Sales ($)'}
            )
            fig.update_traces(hovertemplate='<b>Product:</b> %{x}<br><b>Sales:</b> $%{y:,.0f}<extra></extra>')
            st.plotly_chart(fig, use_container_width=True)

with col2:
    # 📅 Sales by Month
    if 'Month_name' in data.columns and 'total_sales' in data.columns:
        short_months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        full_months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        month_map = dict(zip(short_months, full_months))
        data['Month_full'] = data['Month_name'].map(month_map)
        # Group by full names
        sales_by_month = data.groupby('Month_full')['total_sales'].sum().reindex(full_months).reset_index()
        sales_by_month = sales_by_month.rename(columns={'Month_full': 'Month'})

        if sales_by_month['total_sales'].sum() == 0 or sales_by_month.empty:
            st.info("No sales data available for months in the selected range.")
        else:
            fig = px.bar(
                sales_by_month,
                x='Month',
                y='total_sales',
                title="📅 Sales by Month",
                labels={'Month': 'Product:', 'total_sales': 'Total Sales ($)'}
            )
            fig.update_layout(xaxis_tickangle=-45)
            fig.update_traces(hovertemplate='<b>Product:</b> %{x}<br><b>Sales:</b> $%{y:,.0f}<extra></extra>')
            st.plotly_chart(fig, use_container_width=True)

# Fourth row - Revenue Trends Over Time
st.subheader("Revenue Trends Over Time")

# Daily trends
if 'order_date' in data.columns and 'total_sales' in data.columns:
    daily_sales = data.groupby('order_date')['total_sales'].sum().reset_index()
    
    fig = px.line(
        daily_sales,
        x='order_date',
        y='total_sales',
        title="📈 Daily Revenue Trends",
        labels={'order_date': 'Date', 'total_sales': 'Total Sales ($)'}
    )
    st.plotly_chart(fig, use_container_width=True)

# Monthly trends
if 'month_year' in data.columns and 'total_sales' in data.columns:
    monthly_sales = data.groupby('month_year')['total_sales'].sum().reset_index()
    
    fig = px.line(
        monthly_sales,
        x='month_year',
        y='total_sales',
        title="📈 Monthly Revenue Trends",
        labels={'month_year': 'Month', 'total_sales': 'Total Sales ($)'}
    )
    st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("Coffee Sales Dashboard | Created with Streamlit")