from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.ensemble import RandomForestClassifier
from sklearn.base import ClassifierMixin

from typing import Any
import numpy as np

def create_predictor(algorithm_name: str, algorithm_params: dict[str, Any]) -> ClassifierMixin:
    match algorithm_name:
        case "knn":
            return KNeighborsClassifier(**algorithm_params)
        case "logistic_regression":
            return LogisticRegression(**algorithm_params)
        case "gaussian_nb":
            return GaussianNB(**algorithm_params)
        case "decision_tree":
            return DecisionTreeClassifier(**algorithm_params)
        case "random_forest":
            return RandomForestClassifier(**algorithm_params)
        case "lda":
            return LinearDiscriminantAnalysis(**algorithm_params)
        case _:
            raise ValueError(f"Unknow algorithm {algorithm_name}")
        

def train_predictor(
        vertices_subset: np.ndarray, 
        pressures_train: np.ndarray,
        labels_train: np.ndarray,
        algorithm: str,
        algorithm_params: dict[str, Any],
    ) -> ClassifierMixin:

    train_subset = pressures_train[:, vertices_subset]
    predictor = create_predictor(algorithm, algorithm_params)
    predictor.fit(train_subset, labels_train)
    return predictor