from sklearn.linear_model import LogisticRegression

def get_model(random_seed: int = 42):
    return LogisticRegression(random_state=random_seed, max_iter=1000)
