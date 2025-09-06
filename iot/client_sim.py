from model_utils import load_and_preprocess, train_local_model, evaluate_model

def simulate_client(csv_path, seed):
    X_train, X_test, y_train, y_test = load_and_preprocess(csv_path, seed)
    model = train_local_model(X_train, y_train)
    acc, f1 = evaluate_model(model, X_test, y_test)
    return model, acc, f1
