'''from ledger import Blockchain
from client_sim import simulate_client
from model_utils import load_and_preprocess, evaluate_model
import numpy as np

# -----------------------------
# Federated Averaging (simple version)
# -----------------------------
def federated_average(models):
    coefs = np.mean([tree.feature_importances_ for tree in models], axis=0)
    return coefs

# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    csv_path = "data/dummy_sensor_data_5000_with_anomaly.csv"

    # Initialize blockchain
    ledger = Blockchain()

    # Global test dataset
    X_train, X_test, y_train, y_test = load_and_preprocess(csv_path, seed=999)

    for round_num in range(1, 4):  # simulate 3 federated rounds
        print(f"\n--- Federated Learning Round {round_num} ---")

        local_models = []
        local_accs, local_f1s = [], []

        for seed in [1, 2, 3]:  # simulate 3 clients
            model, acc, f1 = simulate_client(csv_path, seed)
            local_models.append(model)
            local_accs.append(acc)
            local_f1s.append(f1)
            print(f"Client(seed={seed}) → Acc: {acc:.2f}, F1: {f1:.2f}")

        # Aggregate (here just averaging feature importances)
        global_importances = federated_average(local_models)
        global_acc = np.mean(local_accs)
        global_f1 = np.mean(local_f1s)

        print(f"🌍 Global Model → Acc: {global_acc:.2f}, F1: {global_f1:.2f}")

        # Add results to blockchain
        ledger.add_block({
            "round": round_num,
            "global_accuracy": global_acc,
            "global_f1": global_f1,
            "feature_importances": global_importances.tolist()
        })

    print("\n--- Blockchain Ledger ---")
    ledger.print_chain()
    ledger.save_chain()
    print("✅ Blockchain saved to ledger.json")

    # Verify blockchain
    ledger.is_chain_valid()
'''
#using dummy data
'''
from ledger import Blockchain
from client_sim import simulate_client
from model_utils import load_and_preprocess, evaluate_model
import numpy as np
import matplotlib.pyplot as plt

# -----------------------------
# Federated Averaging (simple version)
# -----------------------------
def federated_average(models):
    # Average feature importances from all local models
    coefs = np.mean([m.feature_importances_ for m in models], axis=0)
    return coefs

# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    csv_path = "data/dummy_sensor_data_5000_with_anomaly.csv"

    # Initialize blockchain
    ledger = Blockchain()

    # Global test dataset
    X_train, X_test, y_train, y_test = load_and_preprocess(csv_path, seed=999)

    # Store metrics for plotting later
    global_accuracies = []
    global_f1s = []
    feature_importances_over_rounds = []

    for round_num in range(1, 4):  # simulate 3 federated rounds
        print(f"\n--- Federated Learning Round {round_num} ---")

        local_models = []
        local_accs, local_f1s = [], []

        for seed in [1, 2, 3]:  # simulate 3 clients
            model, acc, f1 = simulate_client(csv_path, seed)
            local_models.append(model)
            local_accs.append(acc)
            local_f1s.append(f1)
            print(f"Client(seed={seed}) → Acc: {acc:.2f}, F1: {f1:.2f}")

        # Aggregate (FedAvg on feature importances)
        global_importances = federated_average(local_models)
        global_acc = np.mean(local_accs)
        global_f1 = np.mean(local_f1s)

        print(f"🌍 Global Model → Acc: {global_acc:.2f}, F1: {global_f1:.2f}")

        # Save metrics
        global_accuracies.append(global_acc)
        global_f1s.append(global_f1)
        feature_importances_over_rounds.append(global_importances)

        # Add results to blockchain
        ledger.add_block({
            "round": round_num,
            "global_accuracy": float(global_acc),
            "global_f1": float(global_f1),
            "feature_importances": global_importances.tolist()
        })

    print("\n--- Blockchain Ledger ---")
    ledger.print_chain()
    ledger.save_chain()
    print("✅ Blockchain saved to ledger.json")

    # Verify blockchain
    ledger.is_chain_valid()

    # -----------------------------
    # Plot Global Accuracy & F1 trends
    # -----------------------------
    rounds = list(range(1, len(global_accuracies) + 1))
    plt.figure(figsize=(10, 6))
    plt.plot(rounds, global_accuracies, marker="o", label="Accuracy")
    plt.plot(rounds, global_f1s, marker="s", label="F1 Score")
    plt.title("Federated Learning Performance Across Rounds")
    plt.xlabel("Round")
    plt.ylabel("Score")
    plt.ylim(0, 1.05)
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend()
    plt.tight_layout()
    plt.show()

    # -----------------------------
    # Plot Feature Importances per Round
    # -----------------------------
    feature_names = ["Temperature", "Humidity", "Vibration", "Current"]
    feature_importances_over_rounds = np.array(feature_importances_over_rounds)

    plt.figure(figsize=(10, 6))
    for i, feature in enumerate(feature_names):
        plt.plot(rounds, feature_importances_over_rounds[:, i], marker="o", label=feature)

    plt.title("Feature Importances Across Rounds")
    plt.xlabel("Round")
    plt.ylabel("Importance")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend()
    plt.tight_layout()
    plt.show()
'''

from ledger import Blockchain
from client_sim import simulate_client
from model_utils import evaluate_model
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import json
import time
import os

# -----------------------------
# Federated Averaging (simple version)
# -----------------------------
def federated_average(models):
    # Average feature importances from all local models
    coefs = np.mean([m.feature_importances_ for m in models], axis=0)
    return coefs

# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":

    # Initialize blockchain
    ledger = Blockchain()

    DATA_FILE = "sensor_data.jsonl"

    # -----------------------------
    # Wait for some sensor data to arrive
    # -----------------------------
    print("Waiting for ESP32 data...")
    while not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:
        time.sleep(1)

    # Load sensor data from file
    with open(DATA_FILE, "r") as f:
        data = [json.loads(line) for line in f.readlines()]

    df = pd.DataFrame(data)

    # If labels for anomaly detection don't exist
    if "Anomaly" not in df.columns:
        df["Anomaly"] = 0  # placeholder or use unsupervised method

    # Features and target
    features = ["Temperature", "Humidity", "Vibration", "Current"]
    X = df[features]
    y = df["Anomaly"]

    # Split for test/train if needed
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=999, stratify=y
    )

    # Store metrics for plotting later
    global_accuracies = []
    global_f1s = []
    feature_importances_over_rounds = []

    # -----------------------------
    # Simulate federated learning rounds
    # -----------------------------
    num_clients = 3
    client_data_splits = np.array_split(df, num_clients)

    for round_num in range(1, 4):  # simulate 3 federated rounds
        print(f"\n--- Federated Learning Round {round_num} ---")

        local_models = []
        local_accs, local_f1s = [], []

        for i, client_df in enumerate(client_data_splits, start=1):
            # Train local model for each client
            model = RandomForestClassifier(n_estimators=100, random_state=i)
            model.fit(client_df[features], client_df["Anomaly"])
            local_models.append(model)

            # Evaluate on test set
            acc, f1 = evaluate_model(model, X_test, y_test)
            local_accs.append(acc)
            local_f1s.append(f1)

            print(f"Client(seed={i}) → Acc: {acc:.2f}, F1: {f1:.2f}")

        # Aggregate (FedAvg on feature importances)
        global_importances = federated_average(local_models)
        global_acc = np.mean(local_accs)
        global_f1 = np.mean(local_f1s)

        print(f"🌍 Global Model → Acc: {global_acc:.2f}, F1: {global_f1:.2f}")

        # Save metrics
        global_accuracies.append(global_acc)
        global_f1s.append(global_f1)
        feature_importances_over_rounds.append(global_importances)

        # Add results to blockchain
        ledger.add_block({
            "round": round_num,
            "global_accuracy": float(global_acc),
            "global_f1": float(global_f1),
            "feature_importances": global_importances.tolist()
        })

    # -----------------------------
    # Blockchain output
    # -----------------------------
    print("\n--- Blockchain Ledger ---")
    ledger.print_chain()
    ledger.save_chain()
    print("✅ Blockchain saved to ledger.json")

    # Verify blockchain
    ledger.is_chain_valid()

    # -----------------------------
    # Plot Global Accuracy & F1 trends
    # -----------------------------
    rounds = list(range(1, len(global_accuracies) + 1))
    plt.figure(figsize=(10, 6))
    plt.plot(rounds, global_accuracies, marker="o", label="Accuracy")
    plt.plot(rounds, global_f1s, marker="s", label="F1 Score")
    plt.title("Federated Learning Performance Across Rounds")
    plt.xlabel("Round")
    plt.ylabel("Score")
    plt.ylim(0, 1.05)
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend()
    plt.tight_layout()
    plt.show()

    # -----------------------------
    # Plot Feature Importances per Round
    # -----------------------------
    feature_importances_over_rounds = np.array(feature_importances_over_rounds)
    plt.figure(figsize=(10, 6))
    for i, feature in enumerate(features):
        plt.plot(rounds, feature_importances_over_rounds[:, i], marker="o", label=feature)

    plt.title("Feature Importances Across Rounds")
    plt.xlabel("Round")
    plt.ylabel("Importance")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend()
    plt.tight_layout()
    plt.show()
