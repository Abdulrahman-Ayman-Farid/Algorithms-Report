#!/usr/bin/env python3
"""
Navigation Routing Algorithm Implementation
Based on the Navigation App Routing: Algorithm Analysis Report

This module implements and compares three shortest-path algorithms:
1. Dijkstra's Algorithm
2. A* Search Algorithm  
3. Bellman-Ford Algorithm

Author: Implementation based on CS Algorithms Assignment - Scenario 6
"""

import sys
import time
import heapq
import math
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass
class Node:
    """Represents a node (intersection) in the road network"""
    id: str
    x: float  # Longitude
    y: float  # Latitude
    name: str = ""

@dataclass
class Edge:
    """Represents an edge (road segment) in the road network"""
    from_node: str
    to_node: str
    weight: float  # Travel time or distance
    name: str = ""

class Graph:
    """Weighted directed graph representing the road network"""
    
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.edges: Dict[str, List[Edge]] = {}
        self.adjacency_list: Dict[str, Dict[str, float]] = {}
    
    def add_node(self, node: Node):
        """Add a node to the graph"""
        self.nodes[node.id] = node
        if node.id not in self.edges:
            self.edges[node.id] = []
        if node.id not in self.adjacency_list:
            self.adjacency_list[node.id] = {}
    
    def add_edge(self, edge: Edge):
        """Add a directed edge to the graph"""
        if edge.from_node not in self.nodes or edge.to_node not in self.nodes:
            raise ValueError("Both nodes must exist before adding edge")
        
        self.edges[edge.from_node].append(edge)
        self.adjacency_list[edge.from_node][edge.to_node] = edge.weight
    
    def get_neighbors(self, node_id: str) -> List[Tuple[str, float]]:
        """Get all neighbors of a node with their edge weights"""
        return list(self.adjacency_list.get(node_id, {}).items())
    
    def get_node(self, node_id: str) -> Optional[Node]:
        """Get node by ID"""
        return self.nodes.get(node_id)
    
    def get_edge_weight(self, from_node: str, to_node: str) -> float:
        """Get weight of edge between two nodes"""
        return self.adjacency_list.get(from_node, {}).get(to_node, float('inf'))

class RoutingAlgorithm(ABC):
    """Abstract base class for routing algorithms"""
    
    def __init__(self, graph: Graph):
        self.graph = graph
    
    @abstractmethod
    def find_shortest_path(self, start: str, end: str) -> Tuple[List[str], float]:
        """
        Find shortest path from start to end node
        Returns: (path as list of node IDs, total distance)
        """
        pass
    
    @abstractmethod
    def get_algorithm_name(self) -> str:
        """Get the name of the algorithm"""
        pass

class DijkstraAlgorithm(RoutingAlgorithm):
    """Dijkstra's shortest path algorithm implementation"""
    
    def find_shortest_path(self, start: str, end: str) -> Tuple[List[str], float]:
        if start not in self.graph.nodes or end not in self.graph.nodes:
            raise ValueError("Start or end node not found in graph")
        
        # Initialize distances and previous nodes
        distances = {node_id: float('inf') for node_id in self.graph.nodes}
        distances[start] = 0
        previous = {node_id: None for node_id in self.graph.nodes}
        
        # Priority queue: (distance, node_id)
        pq = [(0, start)]
        visited = set()
        
        while pq:
            current_dist, current_node = heapq.heappop(pq)
            
            if current_node in visited:
                continue
                
            visited.add(current_node)
            
            # Early termination if we reached the target
            if current_node == end:
                break
            
            # Explore neighbors
            for neighbor, weight in self.graph.get_neighbors(current_node):
                if neighbor in visited:
                    continue
                
                new_dist = current_dist + weight
                if new_dist < distances[neighbor]:
                    distances[neighbor] = new_dist
                    previous[neighbor] = current_node
                    heapq.heappush(pq, (new_dist, neighbor))
        
        # Reconstruct path
        if distances[end] == float('inf'):
            return [], float('inf')
        
        path = []
        current = end
        while current is not None:
            path.append(current)
            current = previous[current]
        path.reverse()
        
        return path, distances[end]
    
    def get_algorithm_name(self) -> str:
        return "Dijkstra's Algorithm"

class AStarAlgorithm(RoutingAlgorithm):
    """A* search algorithm with Euclidean distance heuristic"""
    
    def __init__(self, graph: Graph):
        super().__init__(graph)
        self.max_speed = 60.0  # km/h default max speed for heuristic
    
    def heuristic(self, node1: str, node2: str) -> float:
        """Euclidean distance heuristic (straight-line distance)"""
        n1 = self.graph.get_node(node1)
        n2 = self.graph.get_node(node2)
        
        if not n1 or not n2:
            return 0
        
        # Haversine formula for more accurate distance on Earth
        lat1, lon1 = math.radians(n1.y), math.radians(n1.x)
        lat2, lon2 = math.radians(n2.y), math.radians(n2.x)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Earth's radius in kilometers
        earth_radius = 6371
        distance = earth_radius * c
        
        # Convert to time using max speed
        return distance / self.max_speed
    
    def find_shortest_path(self, start: str, end: str) -> Tuple[List[str], float]:
        if start not in self.graph.nodes or end not in self.graph.nodes:
            raise ValueError("Start or end node not found in graph")
        
        # Initialize g-score (actual distance) and f-score (g + h)
        g_score = {node_id: float('inf') for node_id in self.graph.nodes}
        g_score[start] = 0
        
        f_score = {node_id: float('inf') for node_id in self.graph.nodes}
        f_score[start] = self.heuristic(start, end)
        
        previous = {node_id: None for node_id in self.graph.nodes}
        
        # Priority queue: (f_score, node_id)
        pq = [(f_score[start], start)]
        visited = set()
        
        while pq:
            current_f, current_node = heapq.heappop(pq)
            
            if current_node in visited:
                continue
                
            visited.add(current_node)
            
            # Early termination
            if current_node == end:
                break
            
            # Explore neighbors
            for neighbor, weight in self.graph.get_neighbors(current_node):
                if neighbor in visited:
                    continue
                
                tentative_g = g_score[current_node] + weight
                
                if tentative_g < g_score[neighbor]:
                    previous[neighbor] = current_node
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + self.heuristic(neighbor, end)
                    heapq.heappush(pq, (f_score[neighbor], neighbor))
        
        # Reconstruct path
        if g_score[end] == float('inf'):
            return [], float('inf')
        
        path = []
        current = end
        while current is not None:
            path.append(current)
            current = previous[current]
        path.reverse()
        
        return path, g_score[end]
    
    def get_algorithm_name(self) -> str:
        return "A* Search Algorithm"

class BellmanFordAlgorithm(RoutingAlgorithm):
    """Bellman-Ford algorithm implementation"""
    
    def find_shortest_path(self, start: str, end: str) -> Tuple[List[str], float]:
        if start not in self.graph.nodes or end not in self.graph.nodes:
            raise ValueError("Start or end node not found in graph")
        
        # Initialize distances and previous nodes
        distances = {node_id: float('inf') for node_id in self.graph.nodes}
        distances[start] = 0
        previous = {node_id: None for node_id in self.graph.nodes}
        
        # Relax edges |V| - 1 times
        num_nodes = len(self.graph.nodes)
        for i in range(num_nodes - 1):
            updated = False
            
            for from_node in self.graph.nodes:
                if distances[from_node] == float('inf'):
                    continue
                    
                for to_node, weight in self.graph.get_neighbors(from_node):
                    if distances[from_node] + weight < distances[to_node]:
                        distances[to_node] = distances[from_node] + weight
                        previous[to_node] = from_node
                        updated = True
            
            if not updated:
                break
        
        # Check for negative cycles (not applicable for road networks, but included for completeness)
        for from_node in self.graph.nodes:
            if distances[from_node] == float('inf'):
                continue
                
            for to_node, weight in self.graph.get_neighbors(from_node):
                if distances[from_node] + weight < distances[to_node]:
                    raise ValueError("Graph contains a negative weight cycle")
        
        # Reconstruct path
        if distances[end] == float('inf'):
            return [], float('inf')
        
        path = []
        current = end
        while current is not None:
            path.append(current)
            current = previous[current]
        path.reverse()
        
        return path, distances[end]
    
    def get_algorithm_name(self) -> str:
        return "Bellman-Ford Algorithm"

def main():
    """Main function to demonstrate the routing algorithms"""
    print("Navigation Routing Algorithm Implementation")
    print("Based on CS Algorithms Assignment - Scenario 6")
    print("=" * 50)
    
    # Create a simple test graph
    graph = create_sample_city_graph()
    
    # Test algorithms
    algorithms = [
        DijkstraAlgorithm(graph),
        AStarAlgorithm(graph),
        BellmanFordAlgorithm(graph)
    ]
    
    start_node = "A"
    end_node = "F"
    
    print(f"\nFinding shortest path from {start_node} to {end_node}:")
    print("-" * 50)
    
    for algorithm in algorithms:
        try:
            start_time = time.time()
            path, distance = algorithm.find_shortest_path(start_node, end_node)
            end_time = time.time()
            
            print(f"\n{algorithm.get_algorithm_name()}:")
            print(f"  Path: {' -> '.join(path) if path else 'No path found'}")
            print(f"  Distance: {distance:.2f}")
            print(f"  Time: {(end_time - start_time) * 1000:.4f} ms")
            print(f"  Nodes explored: {len(path)}")
            
        except Exception as e:
            print(f"\n{algorithm.get_algorithm_name()}: Error - {e}")

def create_sample_city_graph() -> Graph:
    """Create a sample city graph for testing"""
    graph = Graph()
    
    # Add nodes (intersections)
    nodes = [
        Node("A", 0.0, 0.0, "Downtown"),
        Node("B", 2.0, 1.0, "City Center"),
        Node("C", 4.0, 0.0, "East District"),
        Node("D", 1.0, 3.0, "North Park"),
        Node("E", 3.0, 3.0, "University"),
        Node("F", 5.0, 2.0, "Airport"),
    ]
    
    for node in nodes:
        graph.add_node(node)
    
    # Add edges (road segments) with weights (travel time in minutes)
    edges = [
        Edge("A", "B", 5.0, "Main Street"),
        Edge("A", "D", 8.0, "Park Avenue"),
        Edge("B", "C", 4.0, "Highway 1"),
        Edge("B", "D", 3.0, "Center Road"),
        Edge("B", "E", 6.0, "University Blvd"),
        Edge("C", "F", 7.0, "Airport Road"),
        Edge("D", "E", 2.0, "Park Connector"),
        Edge("E", "F", 3.0, "Airport Express"),
        Edge("C", "B", 4.0, "Highway 1 Reverse"),
        Edge("E", "B", 6.0, "University Blvd Reverse"),
    ]
    
    for edge in edges:
        graph.add_edge(edge)
    
    return graph

if __name__ == "__main__":
    main()
