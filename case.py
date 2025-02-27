import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.ensemble import RandomForestRegressor

st.set_page_config(page_title='Draco National Park Dashboard', layout='wide')

st.markdown("""
    <style>
        .block-container {padding-top: 2.0rem;}
        .stMetric {text-align: center;}
        .css-1aumxhk, .css-1vbkxwb, .css-1d391kg {display: flex; justify-content: center;}
        .st-emotion-cache-1vbkxwb img, .st-emotion-cache-0 img {display: none !important;}
        .sidebar .sidebar-content {width: 280px !important;}
        .main {margin-left: 280px !important; padding: 20px;}
        .sidebar {background-color: #f8f9fa !important; padding: 10px;}
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>Draco National Park Visitor Analysis</h1>", unsafe_allow_html=True)

data_source = st.file_uploader("Upload Visitor Data (CSV)", type=['csv'], help="Upload the visitor data CSV file.")

if data_source is None:
    st.info("To begin, please upload a CSV file containing visitor data.")
    st.stop()

try:
    park_visitors = pd.read_csv(data_source)

    if park_visitors.empty:
        st.error("The uploaded CSV file is empty. Please upload a valid dataset with information.")
        st.stop()

    essential_fields = ["Date", "Visitor Type", "Number of Visitors", "Revenue Generated ($)", "Weather Condition"]
    missing_fields = [col for col in essential_fields if col not in park_visitors.columns]

    if missing_fields:
        st.error(f"Required columns missing: {missing_fields}. Ensure the CSV is correctly formatted and includes all necessary columns.")
        st.stop()

    park_visitors['Date'] = pd.to_datetime(park_visitors['Date'], errors='coerce')
    park_visitors.dropna(subset=['Date'], inplace=True)

    park_visitors['YearMonth'] = park_visitors['Date'].dt.strftime('%Y-%m')
    park_visitors['VisitWeek'] = park_visitors['Date'].dt.strftime('%Y-W%W')
    park_visitors['DayOfWeekName'] = park_visitors['Date'].dt.day_name()
    park_visitors['DayOfYear'] = park_visitors['Date'].dt.dayofyear

except Exception as ex:
    st.error(f"An error occurred while processing the file: {ex}")
    st.stop()

with st.sidebar:
    st.title("Navigation Menu")
    selected_section = st.radio("Go to", ["Overview", "Visitor Trends", "Visitor Type Analysis", "Revenue Analysis", "Trend Prediction"])

    st.subheader("Visitor Type Filter")
    available_visitor_types = park_visitors["Visitor Type"].unique()
    chosen_visitor_types = st.multiselect("Filter by visitor type:", available_visitor_types, default=available_visitor_types.tolist())

if not chosen_visitor_types:
    st.warning("No visitor types selected. Please select at least one visitor type to view the data.")
    st.stop()

filtered_records = park_visitors[park_visitors["Visitor Type"].isin(chosen_visitor_types)]

if filtered_records.empty:
    st.warning("No data available for the selected visitor types. Adjust your filter or upload different data.")
    st.stop()

if selected_section == "Overview":
    st.markdown(
        """
        <div style="background-color:#f8f9fa; padding:20px; border-radius:10px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1);">
            <h2 style="text-align:center; color:#333;">Overview</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )
    area1, area2 = st.columns(2)
    with area1:
        total_visitors_count = filtered_records['Number of Visitors'].sum()
        st.markdown(
            f"""
            <div style="background-color:#ffffff; padding:20px; border-radius:10px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); text-align:center;">
                <h3>Total Visitors</h3>
                <h1 style="color:#007BFF;">{total_visitors_count:,}</h1>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with area2:
        total_income = filtered_records['Revenue Generated ($)'].sum()
        st.markdown(
            f"""
            <div style="background-color:#ffffff; padding:20px; border-radius:10px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); text-align:center;">
                <h3>Total Revenue ($)</h3>
                <h1 style="color:#28A745;">${total_income:,.2f}</h1>
            </div>
            """,
            unsafe_allow_html=True,
        )

elif selected_section == "Visitor Trends":
    st.title("Visitor Trends Analysis")

    st.sidebar.subheader("Select Date Range")
    earliest_date = filtered_records['Date'].min().to_pydatetime().date()
    latest_date = filtered_records['Date'].max().to_pydatetime().date()
    start_date = st.sidebar.date_input("Start Date", earliest_date)
    end_date = st.sidebar.date_input("End Date", latest_date)

    if start_date > end_date:
        st.sidebar.error("Start date must precede the end date.")
        st.stop()

    date_filtered_records = filtered_records[(filtered_records['Date'] >= pd.to_datetime(start_date)) & (filtered_records['Date'] <= pd.to_datetime(end_date))]

    trend_navigator = st.tabs(["Daily Trends", "Weekly Trends", "Monthly Trends"])

    with trend_navigator[0]:
        st.subheader("Daily Visitor Trends")
        daily_visits = date_filtered_records.groupby("Date")["Number of Visitors"].sum().reset_index()
        fig_daily = px.line(daily_visits, x="Date", y="Number of Visitors", markers=True, hover_data={"Date": "|%b %d, %Y", "Number of Visitors": ":,.0f"})
        fig_daily.update_traces(line=dict(width=2),marker=dict(size=3, color='red'))
        fig_daily.update_xaxes(dtick="M1",tickformat="%b %Y")
        st.plotly_chart(fig_daily, use_container_width=True)

    with trend_navigator[1]:
        st.subheader("Weekly Visitor Trends")
        date_filtered_records["WeekStart"] = date_filtered_records["Date"] - pd.to_timedelta(date_filtered_records["Date"].dt.dayofweek, unit='d')
        date_filtered_records["WeekEnd"] = date_filtered_records["WeekStart"] + pd.to_timedelta(6, unit='d')
        date_filtered_records["VisitWeek"] = date_filtered_records["Date"].dt.strftime('%Y-W%W')
        weekly_visits = date_filtered_records.groupby("VisitWeek").agg({
            "Number of Visitors": "sum",
            "WeekStart": "first",
            "WeekEnd": "first"
        }).reset_index()
        weekly_visits["WeekRange"] = weekly_visits.apply(
            lambda row: f"{row['WeekStart'].strftime('%b %d')} to {row['WeekEnd'].strftime('%b %d')}", axis=1
        )
        fig_weekly = px.bar(weekly_visits, x="VisitWeek", y="Number of Visitors",
                            hover_data={"VisitWeek": True, "Number of Visitors": ":,.0f", "WeekRange": True},
                            labels={"VisitWeek": "Week", "Number of Visitors": "Number of Visitors", "WeekRange": "Week Range"})
        fig_weekly.update_traces(hovertemplate="<b>Week:</b> %{x}<br><b>Number of Visitors:</b> %{y:,.0f}<br><b>Week Range:</b> %{customdata[0]}")
        st.plotly_chart(fig_weekly, use_container_width=True)

    with trend_navigator[2]:
        st.subheader("Monthly Visitor Trends")
        monthly_visits = date_filtered_records.groupby("YearMonth")["Number of Visitors"].sum().reset_index()
        monthly_visits["YearMonth"] = pd.to_datetime(monthly_visits["YearMonth"])
        monthly_visits["MonthName"] = monthly_visits["YearMonth"].dt.strftime('%B')
        fig_monthly = px.bar(monthly_visits, x="MonthName", y="Number of Visitors", labels={"MonthName": "Month", "Number of Visitors": "Visitors"})
        fig_monthly.update_xaxes(categoryorder="array", categoryarray=[
            "January", "February", "March", "April", "May", "June", 
            "July", "August", "September", "October", "November", "December"
        ])

        st.plotly_chart(fig_monthly, use_container_width=True)

elif selected_section == "Visitor Type Analysis":
    st.title("Monthly Visitor Count by Type")
    visitor_traffic_monthly = filtered_records.groupby(["YearMonth", "Visitor Type"])['Number of Visitors'].sum().reset_index()

    fig_grouped_bar = px.bar(visitor_traffic_monthly, x="YearMonth", y="Number of Visitors", color="Visitor Type",
                             barmode="group", title="Visitor Count per Type Each Month")
    fig_grouped_bar.update_xaxes(dtick="M1",tickformat="%b %Y")
    st.plotly_chart(fig_grouped_bar, use_container_width=True)

elif selected_section == "Revenue Analysis":
    st.title("Revenue Insights")

    revenue_navigator = st.tabs(["Daily Revenue", "Monthly Revenue", "Revenue by Type"])
    
    with revenue_navigator[0]:
        st.subheader("Daily Revenue")
        daily_income = filtered_records.groupby("Date")["Revenue Generated ($)"].sum().reset_index()
        daily_revenue_chart = px.line(daily_income, x="Date", y="Revenue Generated ($)", markers=True,hover_data={"Date": "|%b %d, %Y", "Revenue Generated ($)": ":,.2f"})
        daily_revenue_chart.update_traces(line=dict(width=2), marker=dict(size=3, color='red'))
        daily_revenue_chart.update_xaxes(dtick="M1", tickformat="%b %Y")
        st.plotly_chart(daily_revenue_chart, use_container_width=True)    

    with revenue_navigator[1]:
        st.subheader("Monthly Revenue")
        monthly_income = filtered_records.groupby("YearMonth")["Revenue Generated ($)"].sum().reset_index()
        monthly_revenue_chart = px.line(monthly_income, x="YearMonth", y="Revenue Generated ($)",markers=True)
        monthly_revenue_chart.update_traces(line=dict(width=2),marker=dict(size=8, color='red'))   
        monthly_revenue_chart.update_xaxes(dtick="M1",tickformat="%b %Y")
        st.plotly_chart(monthly_revenue_chart, use_container_width=True)

    with revenue_navigator[2]:
        st.subheader("Revenue by Visitor Type")
        income_by_type = filtered_records.groupby("Visitor Type")["Revenue Generated ($)"].sum().reset_index()
        revenue_type_chart = px.bar(income_by_type, x="Visitor Type", y="Revenue Generated ($)", color="Visitor Type")
        st.plotly_chart(revenue_type_chart, use_container_width=True)

elif selected_section == "Trend Prediction":
    st.title("Future Visitor Trend Prediction")

    weather_options = filtered_records["Weather Condition"].unique()
    selected_weather = st.selectbox("Select Weather Condition:", weather_options)
    prediction_horizon = 30
    days_to_forecast = st.slider("Select Number of Days to Predict:", min_value=7, max_value=prediction_horizon, step=7, value=7)
    weather_specific_data = filtered_records[filtered_records["Weather Condition"] == selected_weather]
    last_available_date = weather_specific_data["Date"].max()
    if pd.isnull(last_available_date):
        st.error("No valid dates found in the dataset. Please check your data.")
        st.stop()
    
    forecast_start_date = max(last_available_date + pd.Timedelta(days=1), pd.Timestamp("2025-01-01"))
    future_dates = pd.date_range(start=forecast_start_date, periods=days_to_forecast, freq='D')
    future_data = pd.DataFrame({"Date": future_dates})
    weather_specific_data["TemporalIndex"] = (weather_specific_data["Date"] - weather_specific_data["Date"].min()).dt.days
    weather_specific_data["DayOfYear"] = weather_specific_data["Date"].dt.dayofyear
    weather_specific_data["DayOfWeek"] = weather_specific_data["Date"].dt.weekday
    future_data["TemporalIndex"] = (future_data["Date"] - weather_specific_data["Date"].min()).dt.days
    future_data["DayOfYear"] = future_data["Date"].dt.dayofyear
    future_data["DayOfWeek"] = future_data["Date"].dt.weekday
    X = weather_specific_data[["TemporalIndex", "DayOfYear", "DayOfWeek"]]
    y = weather_specific_data["Number of Visitors"]
    
    model = RandomForestRegressor(n_estimators=500, max_depth=10, random_state=42)
    model.fit(X, y)
    
    future_data["Prediction"] = model.predict(future_data[["TemporalIndex", "DayOfYear", "DayOfWeek"]]).round().astype(int)
    future_data = future_data[future_data["Date"] >= pd.Timestamp("2025-01-01")]
    
    fig_future = px.line(
        future_data, x="Date", y="Prediction", markers=True,
        title="Future Visitor Trend Prediction",
        labels={"Prediction": "Predicted Visitors", "Date": "Date"},
        line_shape="linear"
    )
    fig_future.update_layout(
        xaxis=dict(range=[pd.Timestamp("2025-01-01"), future_data["Date"].max()]),
        yaxis=dict(range=[0, future_data["Prediction"].max()])
    )
    fig_future.update_traces(hovertemplate="<b>Date:</b> %{x}<br><b>Predicted Visitors:</b> %{y}")
    fig_future.update_traces(line=dict(color="blue", dash="solid"), marker=dict(color="blue", size=6))
    st.plotly_chart(fig_future, use_container_width=True)