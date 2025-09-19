import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime

st.set_page_config(
    page_title="Coffee Sales Analytics",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_data():
    data = pd.read_csv('data/Coffee_sales.csv')
    data['total_sales'] = data['money']
    
    data['Date'] = pd.to_datetime(data['Date'])
    data['day_of_week'] = data['Weekday']
    data['month'] = data['Month_name']
    data['hour'] = data['hour_of_day']
    data['time_of_day'] = data['Time_of_Day']
    data['cash_type'] = data['cash_type']
    data['product_line'] = data['coffee_name']
    data['City'] = data['City']
    data['month_year'] = data['Date'].dt.to_period('M').astype(str)

    return data

data = load_data()

if 'Date' in data.columns:
    data['Date'] = pd.to_datetime(data['Date'])
    data['year'] = data['Date'].dt.year
    data['month_num'] = data['Date'].dt.month
    data['quarter'] = data['Date'].dt.quarter

# Sidebar filters
st.sidebar.title("🔎 Filters")
st.sidebar.markdown("---")

# Date filter with preset options
if 'Date' in data.columns:
    min_date = data['Date'].min()
    max_date = data['Date'].max()
    
    date_preset = st.sidebar.selectbox(
        "Quick Period",
        options=["Custom", "Last 7 days", "Last 30 days", "This month", "This quarter", "This year", "Previous year"],
        index=5  
    )
    
    today = pd.to_datetime(datetime.now().date())
    if date_preset == "Last 7 days":
        start_date = today - pd.Timedelta(days=7)
        end_date = today
    elif date_preset == "Last 30 days":
        start_date = today - pd.Timedelta(days=30)
        end_date = today
    elif date_preset == "This month":
        start_date = today.replace(day=1)
        end_date = today
    elif date_preset == "This quarter":
        current_quarter = (today.month - 1) // 3 + 1
        start_date = pd.Timestamp(datetime(today.year, 3 * current_quarter - 2, 1))
        end_date = today
    elif date_preset == "This year":
        start_date = pd.Timestamp(datetime(today.year, 1, 1))
        end_date = today
    elif date_preset == "Previous year":
        start_date = pd.Timestamp(datetime(today.year - 1, 1, 1))
        end_date = pd.Timestamp(datetime(today.year - 1, 12, 31))
    else:
        date_range = st.sidebar.date_input(
            "Select period",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        if len(date_range) == 2:
            start_date, end_date = date_range
        else:
            start_date, end_date = min_date, max_date
    
    data = data[(data['Date'] >= pd.to_datetime(start_date)) & 
                (data['Date'] <= pd.to_datetime(end_date))]

# Location filter
with st.sidebar.expander("📍 Location", expanded=True):
    if 'City' in data.columns:
        cities = st.multiselect(
            "Cities",
            options=data['City'].unique(),
            default=data['City'].unique(),
        )
        data = data[data['City'].isin(cities)]

# Product filter
with st.sidebar.expander("☕ Products", expanded=False):
    if 'product_line' in data.columns:
        products = st.multiselect(
            "Product Lines",
            options=data['product_line'].unique(),
            default=data['product_line'].unique(),
        )
        data = data[data['product_line'].isin(products)]

# Time of day filter
with st.sidebar.expander("⏰ Time of Day", expanded=False):
    if 'time_of_day' in data.columns:
        times_of_day = st.multiselect(
            "Time Periods",
            options=data['time_of_day'].unique(),
            default=data['time_of_day'].unique(),
        )
        data = data[data['time_of_day'].isin(times_of_day)]

# Payment method filter
with st.sidebar.expander("💳 Payment", expanded=False):
    if 'cash_type' in data.columns:
        payment_methods = st.multiselect(
            "Payment Methods",
            options=data['cash_type'].unique(),
            default=data['cash_type'].unique(),
        )
        data = data[data['cash_type'].isin(payment_methods)]

st.sidebar.markdown("---")

# Main dashboard
st.title("☕ Coffee Sales Dashboard")
st.markdown("---")

# Key metrics section
st.subheader("Key Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
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
st.subheader("Sales Analysis:")
col1, col2 = st.columns(2)

with col1:
    if 'product_line' in data.columns and 'total_sales' in data.columns:
        sales_by_product = data.groupby('product_line')['total_sales'].sum().reset_index()
        sales_by_product = sales_by_product.sort_values('total_sales', ascending=False)
        
        fig = px.bar(
            sales_by_product,
            x='product_line',
            y='total_sales',
            title="📊 Sales by Coffee Type",
            color='product_line',
            labels={'product_line': '', 'total_sales': 'Total Sales ($)'}
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

with col2:
    if 'hour' in data.columns and 'total_sales' in data.columns and 'City' in data.columns:
        sales_by_hour_city = data.groupby(['hour', 'City'])['total_sales'].sum().reset_index()
        fig = px.line(
            sales_by_hour_city,
            x='hour',
            y='total_sales',
            color='City',
            title="⏰ Sales by Hour of Day",
            labels={'hour': '', 'total_sales': ''}
        )
        fig.update_layout(xaxis=dict(tickmode='linear', dtick=1))
        st.plotly_chart(fig, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
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
        st.plotly_chart(fig, use_container_width=True)

with col2:
    if 'cash_type' in data.columns and 'total_sales' in data.columns:
        sales_by_payment = data.groupby('cash_type')['total_sales'].sum().reset_index()
        fig = px.bar(
            sales_by_payment,
            x='total_sales',    
            y='cash_type',
            color='cash_type',
            orientation='h',
            title="💳 Sales by Payment Method",
            labels={'cash_type': '', 'total_sales': ''}
        )
        st.plotly_chart(fig)

# Third row of charts
col1, col2 = st.columns(2)

with col1:
    if 'Weekday' in data.columns and 'total_sales' in data.columns and 'City' in data.columns:
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        sales_by_weekday_city = data.groupby(['Weekday', 'City'])['total_sales'].sum().reset_index()
        sales_by_weekday_city['Weekday'] = pd.Categorical(
            sales_by_weekday_city['Weekday'], 
            categories=day_order, 
            ordered=True
        )
        sales_by_weekday_city = sales_by_weekday_city.sort_values('Weekday')
        
        fig = px.bar(
            sales_by_weekday_city,
            x='Weekday',
            y='total_sales',
            color='City',
            title="📅 Sales by Weekday",
            labels={'Weekday': '', 'total_sales': 'Total Sales ($)'},
            barmode='group'
        )
        fig.update_xaxes(tickvals=day_order, ticktext=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
        st.plotly_chart(fig, use_container_width=True)

with col2:
    if 'Month_name' in data.columns and 'total_sales' in data.columns and 'City' in data.columns:
        full_months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        short_months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        month_map = dict(zip(full_months, short_months))
        
        sales_by_month_city = data.groupby(['Month_name', 'City'])['total_sales'].sum().reset_index()
        sales_by_month_city['Month_name'] = pd.Categorical(
            sales_by_month_city['Month_name'], 
            categories=full_months, 
            ordered=True
        )
        sales_by_month_city = sales_by_month_city.sort_values('Month_name')
        sales_by_month_city['Month_abbr'] = sales_by_month_city['Month_name'].map(month_map)
        
        fig = px.bar(
            sales_by_month_city,
            x='Month_abbr',
            y='total_sales',
            color='City',
            title="📅 Sales by Month",
            labels={'Month_abbr': '', 'total_sales': ''},
            barmode='group'
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

st.subheader("Sales Trend Over Time")
if 'month_year' in data.columns and 'City' in data.columns and 'total_sales' in data.columns:
    monthly_sales = data.groupby(['month_year', 'City'])['total_sales'].sum().reset_index()
    monthly_sales['date'] = pd.to_datetime(monthly_sales['month_year'])
    monthly_sales = monthly_sales.sort_values('date')
    
    fig = px.line(
        monthly_sales,
        x='date',
        y='total_sales',
        color='City',
        title="📈 Monthly Sales Trend",
        labels={'date': 'Month', '': '', 'City': 'City'}
    )
    st.plotly_chart(fig, use_container_width=True)
    
st.markdown("---")
st.markdown("Coffee Sales Dashboard | 2025 Lucas Milanez. All rights reserved.")