import numba
import numpy as np
from epyt import epanet


@numba.jit(nopython=True)
def triple_loop(dist: np.ndarray, n: int) -> np.ndarray:
    for k in range(n):
        for i in range(n):
            for j in range(n):
                dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])
    return dist


def floyd_warshall(adj_matrix: np.ndarray, undirected: bool = True) -> np.ndarray:
    n = adj_matrix.shape[0]
    if undirected:
        adj_matrix = np.maximum(adj_matrix, adj_matrix.T)
        
    dist = np.full_like(adj_matrix, float(n + 1))
    dist[adj_matrix > 0] = 1.0
    np.fill_diagonal(dist, 0.0)

    dist = triple_loop(dist, n)
    return dist


def matrix_to_adj_list(matrix: np.ndarray, undirected: bool = True) -> list[set[int]]:
    n = matrix.shape[0]
    if undirected:
        matrix = np.maximum(matrix, matrix.T)

    adj_list = [set() for _ in range(n)]
    for i, row in enumerate(matrix):
        for neighbor, connected in enumerate(row):
            if connected > 0:
                adj_list[i].add(neighbor)
                adj_list[neighbor].add(i)

    return adj_list


class Network:
    def __init__(self, G: epanet):
        self.G = G

        self.adj_matrix = G.getAdjacencyMatrix()
        self.adj_list = matrix_to_adj_list(self.adj_matrix, undirected=True)
        self.distances = floyd_warshall(self.adj_matrix, undirected=True)

        self.node_ids = G.NodeNameID
        self.node_indexes = list(map(lambda x: x - 1, G.NodeIndex))
        self.node_id_to_position_mapping = dict(zip(G.NodeNameID, self.node_indexes))
        self.position_to_node_id = dict(map(reversed, self.node_id_to_position_mapping.items()))

    def plot_with_ids(self):
        self.G.plot(nodesID=self.node_ids, fontsize=3)

    def plot_with_indexes(self):
        self.G.plot(nodesindex=list(map(lambda x: x + 1, self.node_indexes)), fontsize=3)

    def neighbor_array(self, vertex: int) -> np.ndarray:
        return np.array(list(self.adj_list[vertex]))

    def map_node_ids(self, ids: np.ndarray) -> np.ndarray:
        ids = list(map(str, ids))
        return np.array(list(map(self.node_id_to_position_mapping.get, ids)))
    
    def map_node_indexes(self, indexes: np.ndarray):
        return np.array(list(map(self.position_to_node_id.get, indexes)))
    
