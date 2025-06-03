import numpy as np
from .graph_utils import Network
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.ensemble import RandomForestClassifier
from sklearn.base import ClassifierMixin

from .AnnealingConfig import AnnealingConfig
from pydantic import BaseModel, Field
from typing import Any

from typing import List, Any
from tqdm import tqdm
import matplotlib.pyplot as plt




class ExperimentLogger(BaseModel):
    config: AnnealingConfig
    temperature: List[float] = Field(default_factory=list)
    energy: List[float] = Field(default_factory=list)
    best_energy: float = Field(default=float("inf"))
    best_solution: List[int] = Field(default_factory=list)

    def record_step(
            self, 
            temperature: float, 
            energy_value: float, 
            solution_state: np.ndarray
        ) -> None:

        self.temperature.append(temperature)
        self.energy.append(energy_value)

        if energy_value < self.best_energy:
            self.best_energy = energy_value
            self.best_solution = list(solution_state)

    def plot(self):
        fig, ax1 = plt.subplots(figsize=(8, 5))  # Set default figure size

        # Plot temperature (left y-axis)
        ax1.plot(self.temperature, label='Temperature', color='tab:red')
        ax1.set_ylabel('Temperature', color='tab:red')
        ax1.tick_params(axis='y', labelcolor='tab:red')
        ax1.grid(True, which='both', linestyle='--', linewidth=0.5)  # Add grid

        # Plot energy (right y-axis)
        ax2 = ax1.twinx()
        ax2.plot(self.energy, label='Energy', color='tab:blue')
        ax2.set_ylabel('Energy', color='tab:blue')
        ax2.tick_params(axis='y', labelcolor='tab:blue')

        # Title and x-axis limits
        ax1.set_title("Energy and Temperature During Simulated Annealing")
        ax1.set_xlim(0, self.config.epochs * self.config.steps_per_epoch)

        # Combine legends
        lines_1, labels_1 = ax1.get_legend_handles_labels()
        lines_2, labels_2 = ax2.get_legend_handles_labels()
        ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper right')

        plt.tight_layout()
        plt.show()


def random_solution(vertices: np.ndarray, m: int) -> np.ndarray:
    return np.random.permutation(vertices)[:m]

def generate_neighbor(vertex_subset: np.ndarray, network: Network) -> np.ndarray:
    count = 0
    while count < 100:
        vertex_to_swap = np.random.choice(vertex_subset)
        neighboring_vertex = np.random.choice(network.neighbor_array(vertex_to_swap))
        if neighboring_vertex not in vertex_subset:
            break
        count += 1

    new_vertices = vertex_subset.copy()
    new_vertices[new_vertices == vertex_to_swap] = neighboring_vertex

    return new_vertices

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
    # valid_subset = pressures_valid[:, vertices_subset]

    predictor = create_predictor(algorithm, algorithm_params)
    predictor.fit(train_subset, labels_train)
    return predictor

def evaluate_solution(
        vertices_subset: np.ndarray, 
        network: Network,
        pressures_train: np.ndarray,
        labels_train: np.ndarray,
        pressures_valid: np.ndarray,
        labels_valid: np.ndarray,
        algorithm: str,
        algorithm_params: dict[str, Any],
        d_max: float = 5
    ) -> float:

    predictor = train_predictor(
        vertices_subset, 
        pressures_train, 
        labels_train, 
        algorithm, 
        algorithm_params
    )

    valid_subset = pressures_valid[:, vertices_subset]
    pred_label = predictor.predict(valid_subset)

    dists = network.distances[pred_label, labels_valid] / d_max
    dists[dists >= 1.0] = 1.0 
    loss = dists.sum() / pred_label.shape[0]
    return loss


def probability_fun(delta, T):
    return np.exp(-delta/T)

def annealing(
    vertices: np.ndarray,
    network: Network,
    train_pressures: np.ndarray,
    train_labels: np.ndarray,
    test_pressures: np.ndarray,
    test_labels: np.ndarray,
    config: AnnealingConfig
) -> ExperimentLogger:
    
    logger = ExperimentLogger(config=config)
    solution = random_solution(vertices, config.solution_size)
    cur_energy = evaluate_solution(
        solution, network, 
        train_pressures, train_labels,
        test_pressures, test_labels,
        config.algorithm,
        config.algorithm_params,
        config.d_max
    )

    T = config.initial_temperature
    logger.record_step(T, cur_energy, solution)

    for i in tqdm(list(range(config.epochs))):

        for _ in range(config.steps_per_epoch):
            new_solution = generate_neighbor(solution, network)
            next_energy = evaluate_solution(
                new_solution, network,
                train_pressures, train_labels,
                test_pressures, test_labels,
                config.algorithm,
                config.algorithm_params,
                config.d_max
            )

            if next_energy < cur_energy:
                solution = new_solution
                cur_energy = next_energy
            else:
                probability = probability_fun(next_energy - cur_energy, T)
                if probability > np.random.uniform(0, 1):
                    solution = new_solution
                    cur_energy = next_energy

            logger.record_step(T, cur_energy, solution)

        # if (i + 1)  % 100 == 0:
            # logger.plot()
        T *= config.temperature_decay
        
    return logger

