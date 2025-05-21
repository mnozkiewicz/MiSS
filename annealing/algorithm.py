import numpy as np
from .graph_utils import Network
from sklearn.neighbors import KNeighborsClassifier
from pydantic import BaseModel, Field
from typing import List
from tqdm import tqdm
import matplotlib.pyplot as plt

class AnnealingConfig(BaseModel):
    solution_size: int
    knn_neighbors: int
    knn_d_max: int
    epochs: int
    steps_per_epoch: int
    initial_temperature: float
    temperature_decay: float


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
        fig, ax1 = plt.subplots(figsize=(10, 6))  # Set default figure size

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

def evaluate_solution(
        vertices_subset: np.ndarray, 
        network: Network,
        train_pressures: np.ndarray,
        train_labels: np.ndarray,
        test_pressures: np.ndarray,
        test_labels: np.ndarray,
        n_neighbors: int = 5,
        d_max: float = 5
    ) -> float:

    train_subset = train_pressures[:, vertices_subset]
    test_subset = test_pressures[:, vertices_subset]

    knn = KNeighborsClassifier(n_neighbors=n_neighbors)
    knn.fit(train_subset, train_labels)

    pred_label = knn.predict(test_subset)

    dists = network.distances[pred_label, test_labels] / d_max
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
        test_pressures, test_labels
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
                config.knn_neighbors,
                config.knn_d_max
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

        if (i + 1)  % 100 == 0:
            logger.plot()
        T *= config.temperature_decay
        
    return logger

