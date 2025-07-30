import streamlit as st
from datetime import datetime, timedelta
import yfinance as yf
from prophet import Prophet
from prophet.plot import plot_plotly
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import pytz
import ta

def fetch_stock_data(ticker, period, interval):
    end_date = datetime.now()
    if period == '1wk':
        start_date = end_date - timedelta(days=7)
        data = yf.download(ticker, start=start_date, end=end_date, interval=interval)
    else:
        data = yf.download(ticker, period=period, interval=interval)
    return data

def process_data(data):
    if data.index.tzinfo is None:
        data.index = data.index.tz_localize('UTC')
    data.index = data.index.tz_convert('US/Eastern')
    data.reset_index(inplace=True)
    data.rename(columns={'Date' : 'Datetime'}, inplace=True)
    return data

def calculate_metrics(data):
    last_close = data['Close'].iloc[-1]
    prev_close = data['Close'].iloc[0]
    change = last_close - prev_close
    pct_change = (change / prev_close) * 100
    high = data['High'].max()
    low = data['Low'].min()
    volume = data['Volume'].sum()
    return last_close, change, pct_change, high, low, volume

def add_technical_indicators(data):
    data['SMA_20'] = ta.trend.sma_indicator(data['Close'], window=20)
    data['EMA_20'] = ta.trend.ema_indicator(data['Close'], window=20)
    return data

def plot_chart(data, chart_type, indicators, ticker):
    if data.empty:
        return None
    fig = go.Figure()
    if chart_type == 'Candlestick':
        fig.add_trace(go.Candlestick(
            x=data['Datetime'],
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name='Candlestick'
        ))
    else:
        fig.add_trace(go.Scatter(
            x=data['Datetime'],
            y=data['Close'],
            mode='lines',
            name='Close Price'
        ))

    if 'SMA 20' in indicators and 'SMA_20' in data.columns:
        fig.add_trace(go.Scatter(
            x=data['Datetime'],
            y=data['SMA_20'],
            mode='lines',
            name='SMA 20',
            line=dict(color='orange')
        ))
 if 'EMA 20' in indicators and 'EMA_20' in data.columns:
        fig.add_trace(go.Scatter(
            x=data['Datetime'],
            y=data['EMA_20'],
            mode='lines',
            name='EMA 20',
            line=dict(color='purple')
        ))

    fig.update_layout(
        title=f'{ticker} Stock Price',
        xaxis_title='Date',
        yaxis_title='Price (USD)',
        template='plotly_dark'
    )
    return fig

st.set_page_config(layout="wide")
st.title('Real Time Stock Dashboard')

st.sidebar.header('Chart Parameters')
ticker =  st.sidebar.text_input('Ticker', 'ADBE')
time_period = st.sidebar.selectbox('Time Period', ['1d', '1wk', '1mo', '1y', 'max'])
chart_type = st.sidebar.selectbox('Chart Type', ['Candlestick', 'Line'])
indicators =  st.sidebar.multiselect('Technical Indicators', ['SMA 20', 'EMA 20'])

interval_mapping = {
    '1d': '1m',
    '1wk': '30m',
    '1mo': '1d',
    '1y': '1wk',
    'max': '1wk'
}

if st.sidebar.button('Update'):
    data = fetch_stock_data(ticker, time_period, interval_mapping[time_period])
    data = process_data(data)
    data = add_technical_indicators(data)
    last_close, change, pct_change, high, low, volume =  calculate_metrics(data)

last_close, change, pct_change, high, low, volume = 0, 0, 0, 0, 0, 0
data = pd.DataFrame()

if st.sidebar.button('Update'):
    try:
        data = fetch_stock_data(ticker, time_period, interval_mapping[time_period])
        if not data.empty:
            data = process_data(data)
            data = add_technical_indicators(data)
            last_close, change, pct_change, high, low, volume = calculate_metrics(data)
            # Display chart
            fig = plot_chart(data, chart_type, indicators, ticker)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("No data available for the selected ticker and period.")
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")

st.metric(label=f"{ticker} Last Price", value=f"{last_close:.2f} USD", delta=f"{change:.2f} ({pct_change:.2f}%)")

col1, col2, col3 = st.columns(3)
col1.metric("High", f"{high:.2f} USD")
col2.metric("Low", f"{low:.2f} USD")
col3.metric("Volume", f"{volume:.2f} USD")

for indicator in indicators:
    if indicator == 'SMA 20':
        fig.add_trace(go.Scatter(x=data['Date time'], y= data ['SMA_20'], name='SMA 20'))
    elif indicator == 'EMA 20':
        fig.add_trace(go.Scatter(x=data['Date time'], y= data ['SMA_20'], name='SMA 20'))

fig.update_layout(title=f'{ticker} {time_period.upper()} Chart',
                  xaxis_title='Time',
yaxis_title='Price (USD)',
height=600)
st.plotly_chart(fig, use_container_width=True)

