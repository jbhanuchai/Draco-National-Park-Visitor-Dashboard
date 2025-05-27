# Draco National Park Dashboard


## Overview
The **Draco National Park Visitor Dashboard** is an interactive data visualization tool built using **Streamlit**. It helps park analysts track visitor trends, analyze revenue, and predict future attendance patterns based on historical data and weather conditions. The dashboard provides an intuitive and user-friendly interface for data-driven decision-making.

This is a Streamlit app deployed [here](https://draco-national-park-visitor-dashboard.streamlit.app/).

## Features
- **Data Upload**: Allows users to upload visitor datasets in CSV format.
- **Visitor Analysis**:
  - Daily, weekly, and monthly visitor trends using interactive visualizations.
- **Visitor Type Analysis**:
  - Breakdown of visitors into categories (One-day visit, Camping, RV Center).
- **Revenue Analysis**:
  - Daily and monthly revenue trends.
  - Revenue distribution by visitor type.
- **Trend Prediction**:
  - Predicts future visitor trends based on historical data and weather conditions using **Random Forest Regression**.
  - Allows users to select a weather condition and prediction range (7-30 days).

## Installation & Setup
### Prerequisites
Ensure you have **Python 3.8+** installed along with the following dependencies:

```sh
pip install streamlit pandas plotly scikit-learn
```

### Running the Dashboard
1. Clone the repository or download the project files.
```sh
   git clone https://github.com/jbhanuchai/Draco-National-Park-Visitor-Dashboard.git
   cd Draco-National-Park-Visitor-Dashboard
   ```
2. Navigate to the project directory and run the following command:

```sh
streamlit run case.py
```

3. Upload the visitor dataset (CSV format) when prompted.
4. Use the **sidebar navigation** to explore different analyses.

## Usage Instructions
- **Upload a CSV File**: Click on "Upload Visitor Data (CSV)" and select a properly formatted file.
- **Filter Visitor Types**: Use the multi-select dropdown to analyze specific visitor categories.
- **Select Date Range**: Adjust start and end dates to filter visitor data.
- **View Predictions**: Select a weather condition and adjust the forecast duration.
