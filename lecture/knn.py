import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

st.set_page_config(layout="wide")

# X is an n x 2 matrix. 
def build_range(X, mesh_size=.5, margin=.25):
    x_min = X[:, 0].min() - margin
    x_max = X[:, 0].max() + margin
    y_min = X[:, 1].min() - margin
    y_max = X[:, 1].max() + margin

    xrange = np.arange(x_min, x_max, mesh_size)
    yrange = np.arange(y_min, y_max, mesh_size)
    return xrange, yrange

def calculate_mse(X_train, X_test, y_train, y_test, k):
    clf = KNeighborsClassifier(k, weights='uniform')
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    return mean_squared_error(y_test, y_pred)

@st.cache
def load_and_parse_data():
    df = pd.read_csv('RawData.txt', header=None)
    df_truncated = df.loc[:, [1, 7, 8]]
    df_truncated.columns = ['pgc', 'age', 'response']
    df_truncated['color'] = df_truncated.response.astype(str)
    df_truncated['symbol'] = 1

    X = df.loc[:, [1, 7]].values
    y = df.loc[:, 8].values

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    mses = []
    for k in range(1, 350):
        mse = calculate_mse(X_train, X_test, y_train, y_test, k)
        mses.append(mse)

    mse_df = pd.DataFrame({'k': range(1, 350), 'mse': mses, 'color': [1]*len(mses)})
    return df, df_truncated, X, y, mse_df

df, df_truncated, X, y, mse_df = load_and_parse_data()

def get_probs(X, y, k):
    x_range, y_range = build_range(X)
    xx, yy = np.meshgrid(x_range, y_range)
    test_input = np.c_[xx.ravel(), yy.ravel()]

    clf = KNeighborsClassifier(k, weights='uniform')
    clf.fit(X, y)
    Z = clf.predict_proba(test_input)[:, 1]
    Z = Z.reshape(xx.shape)
    return Z

def build_figure(df, X, y, k):

    fig = px.scatter(df, x="pgc", y="age", color="color", 
    color_discrete_sequence=px.colors.qualitative.Vivid,  
    symbol='symbol', 
    symbol_sequence=['circle-open'],
    title='Decision boundary vs. k')
    fig.update(layout_coloraxis_showscale=False, layout_showlegend=False)
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)

    x_range, y_range = build_range(X)
    Z = get_probs(X, y, k)
    Z = np.where(Z > 0.5, 1, 0)

    fig.add_trace(
        go.Contour(
            x=x_range, y=y_range, 
            z=Z,contours_coloring='heatmap', 
            name='probs', hoverinfo='skip',
            colorscale=px.colors.sequential.Oryel,
            showscale=False
        )
    )

    return fig

st.title("Exploring the effect of $k$ on KNN decision boundary")

st.write("You can use the slider below to select the value of $k$ that the KNN model will use. The larger the $k$, the smoother the decision boundary. \
    The data that we're using is from the Pima Women Diabetes Database. The objective is to predict whether somebody has diabetes or not. \
    We're only using two of the features: Plasma glucose concentration (plotted on the x-axis) \
    and age (plotted on the y-axis).")

k = st.slider(
    'Select a value of $k$',
    1, 350, step=1)

col1, col2 = st.columns(2)

with col1:
    fig = build_figure(df_truncated, X, y, k)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    line_plot = px.line(mse_df, x="k", y="mse", color='color', color_discrete_sequence=['white'], title='Test MSE vs. k')
    line_plot.add_vline(x=k, line_color='#F63366')
    line_plot.update(layout_showlegend=False)

    st.plotly_chart(line_plot, use_container_width=True)