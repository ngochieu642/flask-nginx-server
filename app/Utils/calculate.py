from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def getAB_fromDevice(y_device_mac, x_device_mac, dataframe, showReport=True):
    calculate_df = dataframe[[y_device_mac, x_device_mac, "date"]].dropna()
    calculate_df = calculate_df.loc[
        (calculate_df[y_device_mac] != 0) & (calculate_df[x_device_mac] != 0)
    ]

    if not calculate_df.shape[0]:
        return

    # Get Data
    y = calculate_df[y_device_mac]
    X = calculate_df[[x_device_mac]]

    # Split Data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=68
    )

    # Linear Regression
    lm = LinearRegression()
    lm.fit(X_train, y_train)

    y_test_predict = lm.predict(X_test)
    y_train_predict = lm.predict(X_train)

    if showReport:
        # Pearson
        pearson_coef = calculate_df[y_device_mac].corr(
            calculate_df[x_device_mac], method="pearson"
        )

        # Error
        train_error = np.sqrt(np.mean(np.square(y_train_predict - y_train)))
        test_error = np.sqrt(np.mean(np.square(y_test_predict - y_test)))

        print("Pearson correlation coeeficient: ", pearson_coef)
        print("Train Error: ", train_error)
        print("Test Error: ", test_error)

        # plt.figure(figsize=(20, 10))

        # plt.scatter(x=X_train, y=y_train, label="training", s=200)
        # plt.scatter(x=X_test, y=y_test, label="testing", s=200)
        # plt.legend()

        # x_linear = np.linspace(X[x_device_mac].min(), X[x_device_mac].max(), 1000)
        # y_linear = lm.coef_[0] * x_linear + lm.intercept_

        # plt.plot(x_linear, y_linear, c="green")
        # plt.xlabel("X")
        # plt.ylabel("Y")

    return lm.coef_[0], lm.intercept_

def calAB_from2Phase(setPoint, phase0_a, phase0_b, phase1_a, phase1_b):
    coef_A = - phase0_a / phase1_a
    coef_B = (setPoint - phase0_b - phase1_b)/phase1_a + 25
    
    return coef_A, coef_B

def calDownDim_exp(setPoint, upValue, phase0_a, phase0_b, phase1_a, phase1_b):
    return (setPoint - phase0_a*upValue - phase0_b - phase1_b) / phase1_a + 25