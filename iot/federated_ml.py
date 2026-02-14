import json
import os
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from ledger import Blockchain
from model_utils import (
    preprocess_data,
    train_local_model,
    evaluate_model,
    save_model
)

# --------------------------------------------------
# Utility: Load JSONL sensor data
# --------------------------------------------------
def load_sensor_data_from_file(file_path):
    records = []
    with open(file_path, "r") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return pd.DataFrame(records)


def federated_average(models):
    if not models:
        raise ValueError("No models provided for aggregation")

    return np.mean(
        [model.feature_importances_ for model in models],
        axis=0
    )


def split_data_for_clients(df, num_clients=3, seed=42):
    df = df.sample(frac=1, random_state=seed).reset_index(drop=True)
    return np.array_split(df, num_clients)


def train_federated_round(client_datasets, features, round_num):
    local_models = []
    local_accs = []
    local_f1s = []

    print(f"\n{'='*60}")
    print(f"🚀 Federated Learning – Round {round_num}")
    print(f"{'='*60}")

    for idx, client_df in enumerate(client_datasets, start=1):
        print(f"\n🔹 Training Client {idx}")

        X_train, X_test, y_train, y_test = preprocess_data(
            client_df,
            features=features,
            test_size=0.2,
            seed=round_num + idx
        )

        model = train_local_model(
            X_train,
            y_train,
            random_state=round_num + idx
        )

        acc, f1 = evaluate_model(model, X_test, y_test, verbose=False)

        print(f"   ✔ Accuracy: {acc:.4f}")
        print(f"   ✔ F1 Score: {f1:.4f}")

        local_models.append(model)
        local_accs.append(acc)
        local_f1s.append(f1)

    return local_models, local_accs, local_f1s


# --------------------------------------------------
# Main Federated Learning Pipeline
# --------------------------------------------------
def run_federated_learning(
    data_file="sensor_data.jsonl",
    num_rounds=5,
    num_clients=3,
    save_blockchain=True,
    plot_results=True
):
    FEATURES = ["Temperature", "Humidity", "Vibration", "Current"]

    print("\n" + "=" * 60)
    print("🧠 Federated Learning for IoT Predictive Maintenance")
    print("=" * 60)

    if not os.path.exists(data_file):
        print(f"❌ Data file not found: {data_file}")
        print("   Ensure ESP32 server is running and collecting data.")
        return None

    # Load data
    df = load_sensor_data_from_file(data_file)
    if len(df) < 50:
        print("❌ Not enough data for training")
        return None
    print(f"✔ Loaded {len(df)} sensor records")

    # Sanity check
    required_cols = FEATURES + ["Anomaly"]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    # Split data
    client_datasets = split_data_for_clients(df, num_clients=num_clients)
    print(f"✔ Data split into {num_clients} clients")

    # Initialize blockchain
    ledger = Blockchain()
    print("✔ Blockchain initialized")

    global_accuracies = []
    global_f1s = []
    feature_importances = []
    best_overall_acc=0
    best_overall_model=None

    # Federated rounds
    for round_num in range(1, num_rounds + 1):
        local_models, local_accs, local_f1s = train_federated_round(
            client_datasets,
            FEATURES,
            round_num
        )

        global_acc = np.mean(local_accs)
        global_f1 = np.mean(local_f1s)
        global_importance = federated_average(local_models)

        print("\n🌍 Global Model Performance")
        print(f"   Accuracy: {global_acc:.4f}")
        print(f"   F1 Score: {global_f1:.4f}")

        global_accuracies.append(global_acc)
        global_f1s.append(global_f1)
        feature_importances.append(global_importance)

        ledger.add_block({
            "round": round_num,
            "clients": num_clients,
            "accuracy": float(global_acc),
            "f1_score": float(global_f1),
            "feature_importance": global_importance.tolist(),
            "timestamp": time.time()
        })
        if global_acc>best_overall_acc:
            best_overall_acc=global_acc
            best_overall_model=local_models[np.argmax(local_accs)]

        print(f"⛓️  Block #{len(ledger.chain)} added to blockchain")

    # Save blockchain
    if save_blockchain:
        ledger.save_chain("ledger.json")
        print("\n✔ Blockchain saved to ledger.json")

    ledger.is_chain_valid()
    if best_overall_model:
        # Save best model
        save_model(best_overall_model, "models/federated_model.pkl")
        print("✔ Best model saved")

    # Plot results
    if plot_results:
        plot_federated_results(
            global_accuracies,
            global_f1s,
            feature_importances,
            FEATURES
        )

    print("\n" + "=" * 60)
    print("✅ Federated Learning Completed Successfully")
    print("=" * 60)

    return {
        "accuracies": global_accuracies,
        "f1_scores": global_f1s,
        "feature_importance": feature_importances
    }


# --------------------------------------------------
# Visualization
# --------------------------------------------------
def plot_federated_results(accuracies, f1s, importances, features):
    rounds = range(1, len(accuracies) + 1)
    importances = np.array(importances)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    ax1.plot(rounds, accuracies, marker="o", label="Accuracy")
    ax1.plot(rounds, f1s, marker="s", label="F1 Score")
    ax1.set_title("Federated Learning Performance")
    ax1.set_xlabel("Round")
    ax1.set_ylabel("Score")
    ax1.legend()
    ax1.grid(True)

    for i, feature in enumerate(features):
        ax2.plot(rounds, importances[:, i], marker="o", label=feature)

    ax2.set_title("Feature Importance Across Rounds")
    ax2.set_xlabel("Round")
    ax2.set_ylabel("Importance")
    ax2.legend()
    ax2.grid(True)

    plt.tight_layout()
    plt.savefig("federated_learning_results.png", dpi=300)
    print("📊 Results plot saved: federated_learning_results.png")
    plt.show()


# --------------------------------------------------
# Entry Point
# --------------------------------------------------
if __name__ == "__main__":
    import sys

    data_file = sys.argv[1] if len(sys.argv) > 1 else "sensor_data.jsonl"
    rounds = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    clients = int(sys.argv[3]) if len(sys.argv) > 3 else 3

    results = run_federated_learning(
        data_file=data_file,
        num_rounds=rounds,
        num_clients=clients,
        save_blockchain=True,
        plot_results=True
    )

    if results:
        print("\n✅ Federated learning completed successfully!")
        print(f"\n📊 Final Results:")
        print(f"   Best Global Accuracy: {max(results['accuracies']):.4f}")
        print(f"   Best Global F1 Score: {max(results['f1_scores']):.4f}")