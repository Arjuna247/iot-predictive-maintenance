"""
Federated Machine Learning
Implements federated learning for distributed anomaly detection across IoT devices
"""

from ledger import Blockchain
from model_utils import (
    load_sensor_data_from_file,
    preprocess_data,
    train_local_model,
    evaluate_model,
    get_feature_importance,
    save_model
)
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
import os


def federated_average(models):
    """
    Federated averaging of model parameters

    Args:
        models: List of trained RandomForestClassifier models

    Returns:
        Averaged feature importances
    """
    if not models:
        raise ValueError("No models provided for aggregation")

    # Average feature importances from all local models
    importances = np.mean([m.feature_importances_ for m in models], axis=0)
    return importances


def split_data_for_clients(df, num_clients=3, seed=42):
    """
    Split data among multiple clients for federated learning

    Args:
        df: DataFrame with all data
        num_clients: Number of clients to split data into
        seed: Random seed for reproducibility

    Returns:
        List of DataFrames, one for each client
    """
    # Shuffle data
    df_shuffled = df.sample(frac=1, random_state=seed).reset_index(drop=True)

    # Split into roughly equal parts
    client_data = np.array_split(df_shuffled, num_clients)

    return client_data


def train_federated_round(client_datasets, features, round_num, verbose=True):
    """
    Train one round of federated learning

    Args:
        client_datasets: List of DataFrames for each client
        features: List of feature names
        round_num: Current round number
        verbose: Print progress messages

    Returns:
        Tuple of (local_models, local_accuracies, local_f1s)
    """
    local_models = []
    local_accs = []
    local_f1s = []

    if verbose:
        print(f"\n{'='*60}")
        print(f"= Federated Learning Round {round_num}")
        print(f"{'='*60}")

    for client_id, client_df in enumerate(client_datasets, start=1):
        if verbose:
            print(f"\n=ñ Training Client {client_id}...")

        # Prepare data for this client
        X_train, X_test, y_train, y_test = preprocess_data(
            client_df,
            features=features,
            test_size=0.2,
            seed=round_num + client_id
        )

        # Train local model
        model = train_local_model(X_train, y_train, random_state=round_num + client_id)

        # Evaluate on local test set
        acc, f1 = evaluate_model(model, X_test, y_test, verbose=False)

        local_models.append(model)
        local_accs.append(acc)
        local_f1s.append(f1)

        if verbose:
            print(f"    Accuracy: {acc:.4f}, F1: {f1:.4f}")

    return local_models, local_accs, local_f1s


def run_federated_learning(
    data_file="sensor_data.jsonl",
    num_rounds=5,
    num_clients=3,
    features=None,
    save_blockchain=True,
    plot_results=True
):
    """
    Run complete federated learning simulation

    Args:
        data_file: Path to sensor data file
        num_rounds: Number of federated learning rounds
        num_clients: Number of simulated clients
        features: List of feature names
        save_blockchain: Save blockchain ledger to file
        plot_results: Generate performance plots

    Returns:
        Dictionary with results
    """
    if features is None:
        features = ["Temperature", "Humidity", "Vibration", "Current"]

    print("\n" + "="*60)
    print("< Federated Learning for IoT Predictive Maintenance")
    print("="*60)

    # Initialize blockchain
    ledger = Blockchain()
    print(" Blockchain initialized")

    # Load sensor data
    print(f"\n=Â Loading data from {data_file}...")
    if not os.path.exists(data_file):
        print(f"L Error: Data file '{data_file}' not found!")
        print("   Please run the ESP32 simulator first to generate data.")
        return None

    df = load_sensor_data_from_file(data_file)
    print(f" Loaded {len(df)} sensor readings")

    # Split data among clients
    client_datasets = split_data_for_clients(df, num_clients=num_clients)
    print(f" Data split among {num_clients} clients")

    # Create global test set
    _, X_test_global, _, y_test_global = preprocess_data(df, features=features, test_size=0.2, seed=999)

    # Storage for results
    global_accuracies = []
    global_f1s = []
    feature_importances_over_rounds = []

    # Run federated learning rounds
    for round_num in range(1, num_rounds + 1):
        # Train local models
        local_models, local_accs, local_f1s = train_federated_round(
            client_datasets,
            features,
            round_num
        )

        # Aggregate models (FedAvg on feature importances)
        global_importances = federated_average(local_models)
        global_acc = np.mean(local_accs)
        global_f1 = np.mean(local_f1s)

        print(f"\n< Global Model Performance:")
        print(f"   Accuracy: {global_acc:.4f}")
        print(f"   F1 Score: {global_f1:.4f}")

        # Store results
        global_accuracies.append(global_acc)
        global_f1s.append(global_f1)
        feature_importances_over_rounds.append(global_importances)

        # Add to blockchain
        ledger.add_block({
            "round": round_num,
            "num_clients": num_clients,
            "global_accuracy": float(global_acc),
            "global_f1": float(global_f1),
            "local_accuracies": [float(acc) for acc in local_accs],
            "local_f1s": [float(f1) for f1 in local_f1s],
            "feature_importances": global_importances.tolist(),
            "timestamp": time.time()
        })

        print(f"   Ó  Block #{len(ledger.chain)} added to blockchain")

    # Display blockchain
    print("\n" + "="*60)
    print("Ó  Blockchain Ledger")
    print("="*60)
    ledger.print_chain()

    # Save blockchain
    if save_blockchain:
        ledger.save_chain("ledger.json")
        print("\n Blockchain saved to ledger.json")

    # Verify blockchain
    ledger.is_chain_valid()

    # Save the best model (from last round)
    best_model = local_models[np.argmax(local_accs)]
    save_model(best_model, "models/federated_model.pkl")

    # Plot results
    if plot_results:
        plot_federated_results(
            global_accuracies,
            global_f1s,
            feature_importances_over_rounds,
            features
        )

    results = {
        "global_accuracies": global_accuracies,
        "global_f1s": global_f1s,
        "feature_importances": feature_importances_over_rounds,
        "blockchain": ledger,
        "best_model": best_model
    }

    print("\n" + "="*60)
    print(" Federated Learning Completed Successfully!")
    print("="*60 + "\n")

    return results


def plot_federated_results(accuracies, f1s, importances, feature_names):
    """
    Plot federated learning results

    Args:
        accuracies: List of global accuracies per round
        f1s: List of global F1 scores per round
        importances: List of feature importances per round
        feature_names: List of feature names
    """
    rounds = list(range(1, len(accuracies) + 1))

    # Create figure with subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Plot 1: Accuracy and F1 Score
    ax1.plot(rounds, accuracies, marker="o", linewidth=2, label="Accuracy", color="#4ecdc4")
    ax1.plot(rounds, f1s, marker="s", linewidth=2, label="F1 Score", color="#ff6b6b")
    ax1.set_title("Federated Learning Performance Across Rounds", fontsize=14, fontweight="bold")
    ax1.set_xlabel("Round", fontsize=12)
    ax1.set_ylabel("Score", fontsize=12)
    ax1.set_ylim(0, 1.05)
    ax1.grid(True, linestyle="--", alpha=0.3)
    ax1.legend(fontsize=11)

    # Plot 2: Feature Importances
    importances_array = np.array(importances)
    colors = ["#4ecdc4", "#ff6b6b", "#ffa726", "#66bb6a"]

    for i, (feature, color) in enumerate(zip(feature_names, colors)):
        ax2.plot(rounds, importances_array[:, i], marker="o", linewidth=2,
                label=feature, color=color)

    ax2.set_title("Feature Importances Across Rounds", fontsize=14, fontweight="bold")
    ax2.set_xlabel("Round", fontsize=12)
    ax2.set_ylabel("Importance", fontsize=12)
    ax2.grid(True, linestyle="--", alpha=0.3)
    ax2.legend(fontsize=11)

    plt.tight_layout()
    plt.savefig("federated_learning_results.png", dpi=300, bbox_inches="tight")
    print("\n=Ê Results plot saved to: federated_learning_results.png")
    plt.show()


if __name__ == "__main__":
    import sys

    # Check for command line arguments
    data_file = sys.argv[1] if len(sys.argv) > 1 else "sensor_data.jsonl"
    num_rounds = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    num_clients = int(sys.argv[3]) if len(sys.argv) > 3 else 3

    print(f"\n=Ë Configuration:")
    print(f"   Data file: {data_file}")
    print(f"   Rounds: {num_rounds}")
    print(f"   Clients: {num_clients}")

    # Run federated learning
    results = run_federated_learning(
        data_file=data_file,
        num_rounds=num_rounds,
        num_clients=num_clients,
        save_blockchain=True,
        plot_results=True
    )

    if results:
        print("\n<‰ Federated learning completed successfully!")
        print(f"\n=È Final Results:")
        print(f"   Best Global Accuracy: {max(results['global_accuracies']):.4f}")
        print(f"   Best Global F1 Score: {max(results['global_f1s']):.4f}")
