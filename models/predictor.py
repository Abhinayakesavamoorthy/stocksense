import numpy as np
from sklearn.linear_model import LinearRegression

def predict_price(df):
    df = df.copy()
    df['Day'] = np.arange(len(df))

    X = df[['Day']]
    y = df['Close']

    model = LinearRegression()
    model.fit(X, y)

    next_day = np.array([[len(df)]])
    predicted = model.predict(next_day)[0]
    return round(predicted, 2)
    