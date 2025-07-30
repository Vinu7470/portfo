# pip install streamlit fbprophet yfinance plotly
import streamlit as st
from datetime import date
import yfinance as yf
from prophet import Prophet
from prophet.plot import plot_plotly
from plotly import graph_objs as go
import pandas as pd

# Set page title
st.title('Stock Forecast App')

# Define constants
START = "2015-01-01"
TODAY = date.today().strftime("%Y-%m-%d")

# Stock selection
stocks = ('GOOG', 'AAPL', 'MSFT', 'GME')
selected_stock = st.selectbox('Select dataset for prediction', stocks)

# Prediction period slider
n_years = st.slider('Years of prediction:', 1, 4)
period = n_years * 365

# Cache data loading to improve performance
@st.cache_data
def load_data(ticker):
    try:
        data = yf.download(ticker, START, TODAY)
        if data.empty:
            st.error(f"No data found for ticker {ticker}")
            return None
        data.reset_index(inplace=True)
        return data
    except Exception as e:
        st.error(f"Error loading data for {ticker}: {str(e)}")
        return None

# Load data
data_load_state = st.text('Loading data...')
data = load_data(selected_stock)

# Check if data was loaded successfully
if data is None:
    data_load_state.text('Failed to load data!')
    st.stop()

data_load_state.text('Loading data... done!')

# Display raw data
st.subheader('Raw data')
st.write(data.tail())

# Plot raw data
def plot_raw_data():
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Open'], name="stock_open"))
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name="stock_close"))
    fig.update_layout(
        title_text='Time Series Data with Rangeslider',
        xaxis_rangeslider_visible=True,
        xaxis_title="Date",
        yaxis_title="Price",
        legend_title="Legend"
    )
    st.plotly_chart(fig)

plot_raw_data()

# Prepare data for Prophet
df_train = data[['Date', 'Close']].copy()
df_train = df_train.rename(columns={"Date": "ds", "Close": "y"})

# Ensure correct data types
df_train['ds'] = pd.to_datetime(df_train['ds'], errors='coerce')
df_train['y'] = pd.to_numeric(df_train['y'], errors='coerce')

# Drop rows with NaN values
