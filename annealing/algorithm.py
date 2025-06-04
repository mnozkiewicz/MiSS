import numpy as np
from .graph_utils import Network
from .classification import train_predictor
from .AnnealingConfig import AnnealingConfig
from .ExperimentLogger import ExperimentLogger
from typing import Any

from typing import Any
from tqdm import tqdm


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

        T *= config.temperature_decay
        
    return logger
