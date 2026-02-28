import pandas as pd
import numpy as np
import pytest
from scipy.spatial import KDTree
import heapq
import os

class AStarRouter:
    """
    A class that implements the A* search algorithm for navigating between star systems
    in a 3D coordinate space using pre-calculated star system data.
    
    Attributes:
        df (pd.DataFrame): The dataframe containing star system data (id64 and coords).
        points (np.ndarray): A Nx3 numpy array of (x, y, z) coordinates for all systems.
        tree (scipy.spatial.KDTree): A spatial index used for efficient neighbor lookups.
        max_jump_range (float): The maximum distance allowed between two systems in a single jump.
        id_to_idx (dict): A mapping from id64 identifiers to their corresponding index in the dataframe.
    """

    def __init__(self, parquet_path: str, max_jump_range: float = 50.0):
        """
        Initializes the AStarRouter by loading star system data and building a spatial index.
        
        Args:
            parquet_path (str): The file path to the systems_coords.parquet file.
            max_jump_range (float): The maximum distance (in light years) for a single jump.
                                   Defaults to 50.0.
        
        Raises:
            FileNotFoundError: If the provided parquet_path does not exist.
        """
        if not os.path.exists(parquet_path):
            raise FileNotFoundError(f"Parquet file not found: {parquet_path}")
            
        self.df = pd.read_parquet(parquet_path)
        # Extract coordinates as a numpy array for KDTree
        # The 'coords' column is stored as dictionaries
        self.points = np.array([[c['x'], c['y'], c['z']] for c in self.df['coords']])
        self.tree = KDTree(self.points)
        self.max_jump_range = max_jump_range
        # Pre-cache id64 to index mapping for faster lookup
        self.id_to_idx = {id64: idx for idx, id64 in enumerate(self.df['id64'])}
        
    def find_path(self, start_id64: int, end_id64: int):
        """
        Calculates the shortest path between two star systems using the A* algorithm.
        
        The algorithm uses the Euclidean distance between coordinates as both the 
        edge weight (g_score) and the heuristic (h_score).
        
        Args:
            start_id64 (int): The 64-bit integer identifier of the starting system.
            end_id64 (int): The 64-bit integer identifier of the destination system.
            
        Returns:
            list[int] | None: 
                - A list of id64 identifiers representing the sequence of jumps from 
                  start to finish if a path is found.
                - None if no path exists within the max_jump_range.
                - A single-item list [start_id64] if the start and end systems are identical.
        """
        start_node = self.id_to_idx.get(start_id64)
        end_node = self.id_to_idx.get(end_id64)
        
        if start_node is None or end_node is None:
            return None
            
        if start_node == end_node:
            return [start_id64]
            
        # Priority queue: (f_score, node_idx)
        open_set = []
        heapq.heappush(open_set, (0, start_node))
        
        came_from = {}
        g_score = {start_node: 0.0}
        
        # Track nodes in open_set for efficiency
        open_set_hash = {start_node}
        
        while open_set:
            _, current = heapq.heappop(open_set)
            open_set_hash.remove(current)
            
            if current == end_node:
                return self.reconstruct_path(came_from, current)
                
            # Find neighbors within jump range using the KDTree spatial index
            neighbors = self.tree.query_ball_point(self.points[current], self.max_jump_range)
            
            for neighbor in neighbors:
                if neighbor == current:
                    continue
                    
                dist = np.linalg.norm(self.points[current] - self.points[neighbor])
                tentative_g_score = g_score[current] + dist
                
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    h_score = np.linalg.norm(self.points[neighbor] - self.points[end_node])
                    f_val = tentative_g_score + h_score
                    
                    if neighbor not in open_set_hash:
                        heapq.heappush(open_set, (f_val, neighbor))
                        open_set_hash.add(neighbor)
                        
        return None

    def reconstruct_path(self, came_from: dict, current: int):
        """
        Traces back the path from the destination node to the starting node.
        
        Args:
            came_from (dict): A mapping of each node to the node it was reached from.
            current (int): The index of the destination node.
            
        Returns:
            list[int]: The ordered list of id64 identifiers from start to end.
        """
        path = [int(self.df.iloc[current]['id64'])]
        while current in came_from:
            current = came_from[current]
            path.append(int(self.df.iloc[current]['id64']))
        return path[::-1]

@pytest.fixture(scope="module")
def router():
    # Large jump range to ensure we find a path easily in this prototype
    return AStarRouter('tests/data/proto/samples/systems_coords.parquet', max_jump_range=1000)

def test_astar_route_exists(router):
    # Use two systems from the dataset.
    start_id = int(router.df.iloc[0]['id64'])
    # Find something within 1000 units
    dist = np.linalg.norm(router.points - router.points[0], axis=1)
    # Get index of a system that is within range but not the same system
    candidates = np.where((dist > 0) & (dist < 1000))[0]
    
    if len(candidates) > 0:
        end_id = int(router.df.iloc[candidates[0]]['id64'])
        path = router.find_path(start_id, end_id)
        assert path is not None
        assert path[0] == start_id
        assert path[-1] == end_id
        print(f"\nPath found: {path}")
    else:
        pytest.skip("No neighbor found within range for test system.")

def test_astar_no_path(router):
    # Test with a very small jump range that likely makes navigation impossible
    small_router = AStarRouter('tests/data/proto/samples/systems_coords.parquet', max_jump_range=1)
    start_id = int(small_router.df.iloc[0]['id64'])
    # Pick a system very far away
    end_id = int(small_router.df.iloc[-1]['id64'])
    
    path = small_router.find_path(start_id, end_id)
    if path:
        assert path[0] == start_id
        assert path[-1] == end_id
    else:
        assert path is None
