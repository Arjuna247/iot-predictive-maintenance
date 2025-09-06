#using dummy data
'''
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score


def load_and_preprocess(csv_path, seed=42):
    df = pd.read_csv(csv_path)

    # ✅ Use the actual dataset columns
    features = ["Temperature", "Humidity", "Vibration", "Current"]

    X = df[features]
    y = df["Anomaly"]   # target column

    # Split into train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=seed, stratify=y
    )
    return X_train, X_test, y_train, y_test


def train_local_model(X_train, y_train):
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    return model

def evaluate_model(model, X_test, y_test):
    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)
    f1 = f1_score(y_test, preds, average="weighted")
    return acc, f1
'''


import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score

# -----------------------------
# Preprocess function (optional)
# -----------------------------
def preprocess_data(df, features=None, target="Anomaly", test_size=0.2, seed=42):
    """
    Prepares train/test data from a DataFrame.
    
    df: pandas DataFrame containing sensor data
    features: list of feature column names
    target: target column name
    test_size: fraction of data for test set
    seed: random seed for reproducibility
    """
    if features is None:
        features = ["Temperature", "Humidity", "Vibration", "Current"]
    
    X = df[features]
    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=seed, stratify=y
    )
    return X_train, X_test, y_train, y_test

# -----------------------------
# Train local model
# -----------------------------
def train_local_model(X_train, y_train):
    """
    Trains a RandomForestClassifier on the given training data.
    """
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    return model

# -----------------------------
# Evaluate model
# -----------------------------
def evaluate_model(model, X_test, y_test):
    """
    Evaluates the model on test data and returns accuracy and weighted F1 score.
    """
    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)
    f1 = f1_score(y_test, preds, average="weighted")
    return acc, f1
