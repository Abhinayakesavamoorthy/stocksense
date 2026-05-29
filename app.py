import streamlit as st
import plotly.graph_objects as go
import yfinance as yf
from data.stock_data import get_stock_data
from models.predictor import predict_price
from pages.sentiment import get_sentiment

st.set_page_config(page_title="StockSense 📈", layout="wide")
st.title("📈 StockSense — AI Stock Predictor")

TICKERS = {
    "🍎 Apple (AAPL)": "AAPL",
    "🚗 Tesla (TSLA)": "TSLA",
    "🔍 Google (GOOGL)": "GOOGL",
    "💻 Microsoft (MSFT)": "MSFT",
    "📦 Amazon (AMZN)": "AMZN",
    "👥 Meta (META)": "META",
    "🎮 NVIDIA (NVDA)": "NVDA",
    "🎵 Netflix (NFLX)": "NFLX",
    "💳 Visa (V)": "V",
    "🏦 JPMorgan (JPM)": "JPM",
    "🛒 Walmart (WMT)": "WMT",
    "🍔 McDonald's (MCD)": "MCD",
    "☕ Starbucks (SBUX)": "SBUX",
    "✈️ Boeing (BA)": "BA",
    "💊 Pfizer (PFE)": "PFE",
    "🪙 Coinbase (COIN)": "COIN",
    "🛢️ ExxonMobil (XOM)": "XOM",
    "📱 Qualcomm (QCOM)": "QCOM",
    "🏠 Airbnb (ABNB)": "ABNB",
    "🛍️ Shopify (SHOP)": "SHOP",
}

def show_headlines(headlines):
    st.write("**📋 Latest Headlines:**")
    for i, article in enumerate(headlines[:5]):
        title = article.get('title', '')
        description = article.get('description', 'No details available.')
        url = article.get('url', '')
        with st.expander(f"📌 {i+1}. {title}"):
            st.markdown("**📝 What this means:**")
            st.write(description)
            if url:
                st.markdown(f"[🔗 Read Full Article]({url})")

# ── Mode Selection ────────────────────────────────────
st.markdown("### 👋 What would you like to do today?")
mode = st.radio(
    "Choose an option:",
    ["📊 Check Single Stock Status", "⚖️ Compare Two Stocks"],
    horizontal=True
)

st.markdown("---")
period = st.selectbox("🗓️ Select Time Period", ["3mo", "6mo", "1y", "2y"])
st.markdown("---")

# ════════════════════════════════════════════════════
# OPTION 1 — SINGLE STOCK
# ════════════════════════════════════════════════════
if mode == "📊 Check Single Stock Status":

    st.subheader("📌 Select a Stock to Analyze")
    selected_label = st.selectbox("Choose a company:", list(TICKERS.keys()))
    ticker = TICKERS[selected_label]

    if st.button("🔍 Analyze Stock"):

        info = {}
        predicted = 0
        sentiment = "🟡 Neutral"
        headlines = []

        # Stock Info
        try:
            st.subheader(f"📌 {ticker} Stock Info")
            info = yf.Ticker(ticker).info
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("💰 Current Price", f"${info.get('currentPrice', 'N/A')}")
            col2.metric("📈 52W High", f"${info.get('fiftyTwoWeekHigh', 'N/A')}")
            col3.metric("📉 52W Low", f"${info.get('fiftyTwoWeekLow', 'N/A')}")
            col4.metric("🏦 Market Cap", f"${info.get('marketCap', 0):,}")
        except Exception as e:
            st.warning(f"Stock info error: {e}")

        # Candlestick Chart
        try:
            st.subheader(f"🕯️ {ticker} Candlestick Chart")
            df = yf.Ticker(ticker).history(period=period)
            fig = go.Figure(data=[go.Candlestick(
                x=df.index, open=df['Open'], high=df['High'],
                low=df['Low'], close=df['Close'], name=ticker
            )])
            df['MA20'] = df['Close'].rolling(window=20).mean()
            df['MA50'] = df['Close'].rolling(window=50).mean()
            fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], mode='lines',
                name='MA20', line=dict(color='orange', width=1.5)))
            fig.add_trace(go.Scatter(x=df.index, y=df['MA50'], mode='lines',
                name='MA50', line=dict(color='blue', width=1.5)))
            fig.update_layout(xaxis_rangeslider_visible=False, height=500, template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning(f"Chart error: {e}")

        # ML Prediction
        try:
            st.subheader("🤖 ML Price Prediction")
            df_ml = get_stock_data(ticker, period=period)
            predicted = predict_price(df_ml)
            current = info.get('currentPrice', 0)
            change = round(predicted - current, 2)
            direction = "📈 Up" if change > 0 else "📉 Down"
            col1, col2, col3 = st.columns(3)
            col1.metric("Current Price", f"${current}")
            col2.metric("Predicted Price", f"${predicted}")
            col3.metric("Expected Change", f"${change}", delta=direction)
        except Exception as e:
            st.warning(f"Prediction error: {e}")

        # News Sentiment
        try:
            st.subheader("📰 News Sentiment Analysis")
            sentiment, score, headlines = get_sentiment(ticker)
            col1, col2 = st.columns(2)
            col1.info(f"Overall Sentiment: {sentiment}")
            col2.info(f"Sentiment Score: {round(score, 2)}")
            show_headlines(headlines)
        except Exception as e:
            st.warning(f"Sentiment error: {e}")

# ════════════════════════════════════════════════════
# OPTION 2 — COMPARE TWO STOCKS
# ════════════════════════════════════════════════════
elif mode == "⚖️ Compare Two Stocks":

    st.subheader("📊 Select Two Stocks to Compare")
    col1, col2 = st.columns(2)

    with col1:
        label1 = st.selectbox("📌 Select First Stock", list(TICKERS.keys()), index=0)
        ticker1 = TICKERS[label1]

    with col2:
        label2 = st.selectbox("📌 Select Second Stock", list(TICKERS.keys()), index=1)
        ticker2 = TICKERS[label2]

    if st.button("⚖️ Compare Stocks"):

        if ticker1 == ticker2:
            st.error("⚠️ Please select two different stocks to compare!")
        else:
            # Side by Side Info
            st.subheader("📌 Stock Info Comparison")
            col1, col2 = st.columns(2)
            info1 = {}
            info2 = {}

            try:
                info1 = yf.Ticker(ticker1).info
                with col1:
                    st.markdown(f"### {ticker1}")
                    st.metric("💰 Current Price", f"${info1.get('currentPrice', 'N/A')}")
                    st.metric("📈 52W High", f"${info1.get('fiftyTwoWeekHigh', 'N/A')}")
                    st.metric("📉 52W Low", f"${info1.get('fiftyTwoWeekLow', 'N/A')}")
                    st.metric("🏦 Market Cap", f"${info1.get('marketCap', 0):,}")
            except Exception as e:
                st.warning(f"{ticker1} info error: {e}")

            try:
                info2 = yf.Ticker(ticker2).info
                with col2:
                    st.markdown(f"### {ticker2}")
                    st.metric("💰 Current Price", f"${info2.get('currentPrice', 'N/A')}")
                    st.metric("📈 52W High", f"${info2.get('fiftyTwoWeekHigh', 'N/A')}")
                    st.metric("📉 52W Low", f"${info2.get('fiftyTwoWeekLow', 'N/A')}")
                    st.metric("🏦 Market Cap", f"${info2.get('marketCap', 0):,}")
            except Exception as e:
                st.warning(f"{ticker2} info error: {e}")

            # Price Comparison Chart
            try:
                st.subheader(f"📈 {ticker1} vs {ticker2} Price Comparison")
                df1 = yf.Ticker(ticker1).history(period=period)['Close']
                df2 = yf.Ticker(ticker2).history(period=period)['Close']
                if df1.empty or df2.empty:
                    st.warning("⚠️ Could not fetch data for one or both stocks.")
                else:
                    df1_norm = (df1 / df1.iloc[0]) * 100
                    df2_norm = (df2 / df2.iloc[0]) * 100
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=df1_norm.index, y=df1_norm,
                        name=ticker1, line=dict(color='green', width=2)))
                    fig.add_trace(go.Scatter(x=df2_norm.index, y=df2_norm,
                        name=ticker2, line=dict(color='red', width=2)))
                    fig.update_layout(height=450, template="plotly_dark",
                        yaxis_title="Normalized Price (Base 100)",
                        title=f"{ticker1} vs {ticker2} Performance")
                    st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.warning(f"Comparison chart error: {e}")

            # Candlestick Side by Side
            st.subheader("🕯️ Candlestick Charts")
            col1, col2 = st.columns(2)
            for ticker, col in [(ticker1, col1), (ticker2, col2)]:
                try:
                    df = yf.Ticker(ticker).history(period=period)
                    fig = go.Figure(data=[go.Candlestick(
                        x=df.index, open=df['Open'], high=df['High'],
                        low=df['Low'], close=df['Close'], name=ticker
                    )])
                    fig.update_layout(xaxis_rangeslider_visible=False,
                        height=400, template="plotly_dark", title=ticker)
                    with col:
                        st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.warning(f"{ticker} chart error: {e}")

            # ML Prediction Comparison
            st.subheader("🤖 ML Prediction Comparison")
            col1, col2 = st.columns(2)
            for ticker, info, col in [(ticker1, info1, col1), (ticker2, info2, col2)]:
                try:
                    df_ml = get_stock_data(ticker, period=period)
                    predicted = predict_price(df_ml)
                    current = info.get('currentPrice', 0)
                    change = round(predicted - current, 2)
                    direction = "📈 Up" if change > 0 else "📉 Down"
                    with col:
                        st.markdown(f"### {ticker}")
                        st.metric("Current Price", f"${current}")
                        st.metric("Predicted Price", f"${predicted}")
                        st.metric("Expected Change", f"${change}", delta=direction)
                except Exception as e:
                    st.warning(f"{ticker} prediction error: {e}")

            # Sentiment Comparison
            st.subheader("📰 News Sentiment Comparison")
            col1, col2 = st.columns(2)
            for ticker, col in [(ticker1, col1), (ticker2, col2)]:
                try:
                    sentiment, score, headlines = get_sentiment(ticker)
                    with col:
                        st.markdown(f"### {ticker}")
                        st.info(f"Sentiment: {sentiment}")
                        st.info(f"Score: {round(score, 2)}")
                        show_headlines(headlines)
                except Exception as e:
                    st.warning(f"{ticker} sentiment error: {e}")