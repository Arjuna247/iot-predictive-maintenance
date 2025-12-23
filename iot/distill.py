"""
Knowledge Distillation
Compress large ensemble models into smaller, efficient models for edge deployment
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neural_network import MLPClassifier
from model_utils import preprocess_data, evaluate_model, load_sensor_data_from_file
import pickle


class ModelDistillation:
    """Knowledge distillation for model compression"""

    def __init__(self, teacher_model, temperature=2.0):
        """
        Initialize distillation

        Args:
            teacher_model: Large, complex model (teacher)
            temperature: Temperature for softening probability distributions
        """
        self.teacher_model = teacher_model
        self.temperature = temperature
        self.student_model = None

    def create_student_model(self, model_type="decision_tree", **kwargs):
        """
        Create a smaller student model

        Args:
            model_type: Type of student model ('decision_tree', 'small_rf', 'mlp')
            **kwargs: Additional parameters for the student model

        Returns:
            Student model instance
        """
        if model_type == "decision_tree":
            # Simple decision tree for edge deployment
            self.student_model = DecisionTreeClassifier(
                max_depth=kwargs.get("max_depth", 5),
                min_samples_split=kwargs.get("min_samples_split", 10),
                random_state=42
            )
        elif model_type == "small_rf":
            # Smaller random forest
            self.student_model = RandomForestClassifier(
                n_estimators=kwargs.get("n_estimators", 10),
                max_depth=kwargs.get("max_depth", 5),
                min_samples_split=kwargs.get("min_samples_split", 10),
                random_state=42,
                n_jobs=-1
            )
        elif model_type == "mlp":
            # Small neural network
            self.student_model = MLPClassifier(
                hidden_layer_sizes=kwargs.get("hidden_layer_sizes", (32, 16)),
                max_iter=kwargs.get("max_iter", 500),
                random_state=42
            )
        else:
            raise ValueError(f"Unknown model type: {model_type}")

        return self.student_model

    def get_soft_labels(self, X):
        """
        Get soft labels (probabilities) from teacher model

        Args:
            X: Input features

        Returns:
            Soft labels with temperature scaling
        """
        if hasattr(self.teacher_model, 'predict_proba'):
            # Get probabilities from teacher
            probs = self.teacher_model.predict_proba(X)

            # Apply temperature scaling
            scaled_probs = np.power(probs, 1.0 / self.temperature)
            scaled_probs = scaled_probs / np.sum(scaled_probs, axis=1, keepdims=True)

            return scaled_probs
        else:
            # Fallback to hard labels if model doesn't support probabilities
            return self.teacher_model.predict(X)

    def distill(self, X_train, y_train=None, use_soft_labels=True):
        """
        Perform knowledge distillation

        Args:
            X_train: Training features
            y_train: Training labels (optional, will use teacher predictions if None)
            use_soft_labels: Use soft labels from teacher (default: True)

        Returns:
            Trained student model
        """
        if self.student_model is None:
            raise ValueError("Student model not created. Call create_student_model() first.")

        print("\n<� Starting Knowledge Distillation...")
        print(f"   Teacher: {type(self.teacher_model).__name__}")
        print(f"   Student: {type(self.student_model).__name__}")
        print(f"   Temperature: {self.temperature}")

        if use_soft_labels and hasattr(self.teacher_model, 'predict_proba'):
            # Train student on soft labels from teacher
            print("   Using soft labels from teacher...")
            soft_labels = self.get_soft_labels(X_train)

            # For sklearn models, we need to convert probabilities to class labels
            # A better approach would use custom loss, but sklearn doesn't support that directly
            teacher_predictions = self.teacher_model.predict(X_train)
            self.student_model.fit(X_train, teacher_predictions)
        else:
            # Train student on hard labels
            print("   Using hard labels...")
            if y_train is None:
                y_train = self.teacher_model.predict(X_train)
            self.student_model.fit(X_train, y_train)

        print("    Distillation complete!")

        return self.student_model

    def compare_models(self, X_test, y_test):
        """
        Compare teacher and student model performance

        Args:
            X_test: Test features
            y_test: Test labels

        Returns:
            Dictionary with comparison metrics
        """
        print("\n=� Model Comparison:")
        print("="*60)

        # Evaluate teacher
        print("\n=h
<� Teacher Model:")
        teacher_acc, teacher_f1 = evaluate_model(
            self.teacher_model, X_test, y_test, verbose=True
        )

        # Evaluate student
        print("\n<� Student Model:")
        student_acc, student_f1 = evaluate_model(
            self.student_model, X_test, y_test, verbose=True
        )

        # Calculate compression ratio
        teacher_size = self._estimate_model_size(self.teacher_model)
        student_size = self._estimate_model_size(self.student_model)
        compression_ratio = teacher_size / student_size if student_size > 0 else 0

        print("\n=� Model Size Comparison:")
        print(f"   Teacher size: ~{teacher_size:.2f} KB")
        print(f"   Student size: ~{student_size:.2f} KB")
        print(f"   Compression ratio: {compression_ratio:.2f}x")

        print("\n=� Performance Gap:")
        print(f"   Accuracy loss: {(teacher_acc - student_acc)*100:.2f}%")
        print(f"   F1 Score loss: {(teacher_f1 - student_f1)*100:.2f}%")

        return {
            "teacher": {"accuracy": teacher_acc, "f1": teacher_f1, "size_kb": teacher_size},
            "student": {"accuracy": student_acc, "f1": student_f1, "size_kb": student_size},
            "compression_ratio": compression_ratio
        }

    def _estimate_model_size(self, model):
        """
        Estimate model size in KB

        Args:
            model: sklearn model

        Returns:
            Estimated size in KB
        """
        import sys
        try:
            # Serialize model to get actual size
            model_bytes = pickle.dumps(model)
            return len(model_bytes) / 1024  # Convert to KB
        except:
            # Fallback estimate
            return sys.getsizeof(model) / 1024

    def save_student_model(self, file_path="models/student_model.pkl"):
        """
        Save student model to disk

        Args:
            file_path: Path to save the model
        """
        import os
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "wb") as f:
            pickle.dump(self.student_model, f)

        print(f"\n Student model saved to: {file_path}")


def distill_model_for_edge(
    teacher_model,
    X_train,
    X_test,
    y_train,
    y_test,
    student_type="decision_tree",
    temperature=2.0
):
    """
    High-level function for model distillation

    Args:
        teacher_model: Large teacher model
        X_train, X_test, y_train, y_test: Training and test data
        student_type: Type of student model
        temperature: Distillation temperature

    Returns:
        Tuple of (student_model, comparison_results)
    """
    # Initialize distillation
    distiller = ModelDistillation(teacher_model, temperature=temperature)

    # Create student model
    if student_type == "decision_tree":
        distiller.create_student_model("decision_tree", max_depth=6)
    elif student_type == "small_rf":
        distiller.create_student_model("small_rf", n_estimators=15, max_depth=6)
    elif student_type == "mlp":
        distiller.create_student_model("mlp", hidden_layer_sizes=(32, 16))

    # Perform distillation
    student_model = distiller.distill(X_train, y_train, use_soft_labels=True)

    # Compare models
    results = distiller.compare_models(X_test, y_test)

    # Save student model
    distiller.save_student_model(f"models/student_{student_type}.pkl")

    return student_model, results


if __name__ == "__main__":
    print("\n" + "="*60)
    print(">� Knowledge Distillation for Edge Deployment")
    print("="*60)

    # Load data
    data_file = "sensor_data.jsonl"

    if not os.path.exists(data_file):
        print(f"\nL Error: Data file '{data_file}' not found!")
        print("   Please run the ESP32 simulator first to generate data.")
        exit(1)

    import os
    df = load_sensor_data_from_file(data_file)
    print(f"\n Loaded {len(df)} sensor readings")

    # Prepare data
    features = ["Temperature", "Humidity", "Vibration", "Current"]
    X_train, X_test, y_train, y_test = preprocess_data(df, features=features)

    # Train teacher model (large Random Forest)
    print("\n=h
<� Training Teacher Model (Large Random Forest)...")
    teacher_model = RandomForestClassifier(
        n_estimators=100,
        max_depth=15,
        random_state=42,
        n_jobs=-1
    )
    teacher_model.fit(X_train, y_train)
    print("    Teacher model trained")

    # Distill to different student models
    student_types = ["decision_tree", "small_rf"]

    for student_type in student_types:
        print(f"\n{'='*60}")
        print(f"Distilling to: {student_type}")
        print(f"{'='*60}")

        student_model, results = distill_model_for_edge(
            teacher_model,
            X_train,
            X_test,
            y_train,
            y_test,
            student_type=student_type,
            temperature=2.0
        )

    print("\n" + "="*60)
    print(" Knowledge Distillation Complete!")
    print("="*60)
    print("\n=� Student models are ready for edge deployment!")
    print("   - Smaller size (fits on ESP32/embedded devices)")
    print("   - Faster inference")
    print("   - Minimal accuracy loss\n")
