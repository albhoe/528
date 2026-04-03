print("Hello, World!")

import logging
from google.cloud import storage
import os
import sys
from google.cloud.sql.connector import Connector, IPTypes
import pymysql
import socket, struct
import sqlalchemy
import pandas
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.neural_network import MLPRegressor
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score, classification_report

PROJECT_ID = os.getenv("PROJECT_ID", "bucsece528")
INSTANCE_CONNECTION_NAME = os.getenv("INSTANCE_CONNECTION_NAME", "bucsece528:us-central1:alhoe-hw5-mysqlinstance")
DB_USER = os.getenv("DB_USER", "albert")
DB_PASS = os.getenv("DB_PASS", "pres1789")
DB_NAME = os.getenv("DB_NAME", "528hwdatabase")

connector = Connector()

def getconn():
    conn = connector.connect(
      INSTANCE_CONNECTION_NAME,
      "pymysql",
      user=DB_USER,
      password=DB_PASS,
      db=DB_NAME
    )
    print(f"Database connection established successfully: {conn}")
    return conn

pool = sqlalchemy.create_engine(
    "mysql+pymysql://",
    creator=getconn,
)

with pool.connect() as db_conn:
    #Country Prediction
    country_data = db_conn.execute(sqlalchemy.text(
        "SELECT DISTINCT `country`, " \
        "SUBSTRING_INDEX(`client_ip`, '.',1) AS `client_ip_1`, " \
        "SUBSTRING_INDEX(`client_ip`, '.',2) AS `client_ip_2`, " \
        "`client_ip` " \
        "FROM request_logs " \
        "WHERE `country` IS NOT NULL " \
        "AND `country` !='' " \
        "AND `client_ip` IS NOT NULL " \
        "ORDER BY `client_ip` "
    )).fetchall()
    country_dataframe = pandas.DataFrame(country_data)

    #Income Prediction
    income_data = db_conn.execute(sqlalchemy.text("SELECT DISTINCT `income`,`country`,`gender`,`is_banned`,`time_of_day` " \
    "FROM request_logs")).fetchall()


connector.close()

print("Data Aquired. Database connection closed successfully.")

X = country_dataframe.drop(columns=["country"])
y = country_dataframe["country"]

X_train, X_test, y_train, y_test = train_test_split(
X, y, test_size=0.1, random_state=42)

def predict_country(client_ip):
    client_ip_first = client_ip.split('.')[0]
    client_ip_prefix = '.'.join(client_ip.split('.')[:2])
    if client_ip_prefix in X_train['client_ip_2'].values:
        country = y_train[X_train['client_ip_2'] == client_ip_prefix].values[0]
    elif client_ip_first in X_train['client_ip_1'].values:
        country = y_train[X_train['client_ip_1'] == client_ip_first].values[0]
    return country

X_test.drop(columns=['client_ip_1', 'client_ip_2'], inplace=True)
predictions = X_test['client_ip'].apply(predict_country)
accuracy = (predictions == y_test).mean()
print(f"Country Prediction Accuracy: {accuracy:.2%}")
X_test['predicted_country'] = predictions
X_test['country'] = y_test
test_data = X_test[['client_ip','country','predicted_country']]
print(test_data)
test_data.to_csv(f'country_prediction_{accuracy}.csv', index=False)

try:
    storage.Client(project=PROJECT_ID).bucket('alhoe528hw2').blob(f'/hw6/country_prediction_{accuracy}.csv').upload_from_filename(f'country_prediction_{accuracy}.csv')
except Exception as e:
    logging.error(f"Error uploading country prediction results to Cloud Storage: {e}")

def income_2_scalar(income):
    match income:
        case "0-10k":
            return 0
        case "10k-20k":
            return 1
        case "20k-40k":
            return 2
        case "40k-60k":
            return 3
        case "60k-100k":
            return 4
        case "100k-150k":
            return 5
        case "150k-250k":
            return 6
        case _:
            return 7

def scalar_2_income(scalar):
    match scalar:
        case 0:
            return "0-10k"
        case 1:
            return "10k-20k"
        case 2:
            return "20k-40k"
        case 3:
            return "40k-60k"
        case 4:
            return "60k-100k"
        case 5:
            return "100k-150k"
        case 6:
            return "150k-250k"
        case _:
            return "250k+"
        
def time_to_int(time_str):
    h, m, s = map(int, time_str.split(":"))
    return h * 3600 + m * 60 + s

def predict_income():
    test_data = pandas.DataFrame(income_data).dropna()
    le = LabelEncoder()
    test_data["time_of_day"] = test_data["time_of_day"].apply(time_to_int)
    test_data["minute"] = test_data["time_of_day"] // 60
    test_data["hour"] = test_data["time_of_day"] // 3600
    test_data["is_banned"] = test_data["is_banned"].astype(int)
    test_data["gender"] = le.fit_transform(test_data["gender"])
    test_data["income"] = test_data["income"].apply(income_2_scalar)
    test_data = pandas.get_dummies(test_data, columns=["country"])

    X = test_data.drop(columns=["income"])
    y = test_data["income"]

    X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.1, random_state=42
    )

    models = {
    #"Naive Bayes":       GaussianNB(),
    "Random Forest":     RandomForestClassifier(random_state=42)
    }

    max_acc = 0

    test_data = X_test.copy()

    for name, model in models.items():
        model.fit(X_train, y_train)
        test_data[f'{name}_predicted_income'] = model.predict(X_test).round()
        acc = accuracy_score(y_test, test_data[f'{name}_predicted_income'])
        if acc > max_acc:
            max_acc = acc
        test_data[f'{name}_predicted_income'] = test_data[f'{name}_predicted_income'].apply(scalar_2_income)
        print(f"{name:25s} accuracy: {acc:.2f}")

    y_train = y_train.copy().apply(income_2_scalar)

    models = {#"MLP Regression" : MLPRegressor(hidden_layer_sizes=(64, 32), random_state=42)
              }
    
    for name, model in models.items():
        try:
            model.fit(X_train, y_train)
            test_data[f'{name}_predicted_income'] = model.predict(X_test).round()
            acc = accuracy_score(y_test, test_data[f'{name}_predicted_income'])
            if acc > max_acc:
                max_acc = acc
            test_data[f'{name}_predicted_income'] = test_data[f'{name}_predicted_income'].apply(scalar_2_income)
            print(f"{name:25s} accuracy: {acc:.2f}")
        except Exception as e:
            logging.error(f"Error training {name} model: {e}")

    test_data['income'] = y_test.apply(scalar_2_income)
    test_data = test_data[['income','Random Forest_predicted_income']]
    print(test_data)
    try:
        test_data.to_csv(f'income_prediction_{max_acc}.csv', index=False)
    except Exception as e:
        logging.error(f"Error saving income prediction results: {e}")
    return max_acc

max_acc = predict_income()

try:
    storage.Client(project=PROJECT_ID).bucket('alhoe528hw2').blob(f'/hw6/income_prediction_{max_acc}.csv').upload_from_filename(f'income_prediction_{max_acc}.csv')
except Exception as e:
    logging.error(f"Error uploading income prediction results to Cloud Storage: {e}")

sys.exit(0)
