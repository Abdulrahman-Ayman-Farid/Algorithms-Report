#!/usr/bin/env python3
"""
Data Generator for Navigation Routing Algorithms
Creates realistic city road network graphs for testing and benchmarking
"""

import random
import math
import json
from typing import List, Dict, Tuple, Set
from main import Graph, Node, Edge

class CityGraphGenerator:
    """Generates realistic city road network graphs"""
    
    def __init__(self, seed: int = None):
        if seed:
            random.seed(seed)
    
    def generate_grid_city(self, width: int, height: int, block_size: float = 1.0) -> Graph:
        """Generate a grid-based city layout (like Manhattan)"""
        graph = Graph()
        
        # Create nodes in a grid pattern
        for i in range(width):
            for j in range(height):
                node_id = f"G{i}_{j}"
                x = i * block_size
                y = j * block_size
                name = f"Grid {i},{j}"
                graph.add_node(Node(node_id, x, y, name))
        
        # Create edges (horizontal and vertical streets)
        for i in range(width):
            for j in range(height):
                current = f"G{i}_{j}"
                
                # Horizontal connection (east)
                if i < width - 1:
                    east = f"G{i+1}_{j}"
                    weight = block_size * random.uniform(0.8, 1.2)  # Traffic variation
                    graph.add_edge(Edge(current, east, weight, f"Street {i+1}"))
                    graph.add_edge(Edge(east, current, weight, f"Street {i+1}"))
                
                # Vertical connection (north)
                if j < height - 1:
                    north = f"G{i}_{j+1}"
                    weight = block_size * random.uniform(0.8, 1.2)
                    graph.add_edge(Edge(current, north, weight, f"Avenue {j+1}"))
                    graph.add_edge(Edge(north, current, weight, f"Avenue {j+1}"))
        
        return graph
    
    def generate_radial_city(self, num_rings: int, points_per_ring: List[int], 
                           center_radius: float = 0.5) -> Graph:
        """Generate a radial city layout (like Paris)"""
        graph = Graph()
        
        # Create center node
        center_id = "CENTER"
        graph.add_node(Node(center_id, 0, 0, "City Center"))
        
        # Create rings
        ring_nodes = []
        for ring in range(num_rings):
            ring_nodes.append([])
            num_points = points_per_ring[ring] if ring < len(points_per_ring) else 8
            radius = center_radius + ring * 1.0
            
            for i in range(num_points):
                angle = 2 * math.pi * i / num_points
                x = radius * math.cos(angle)
                y = radius * math.sin(angle)
                node_id = f"R{ring}_P{i}"
                name = f"Ring {ring}, Point {i}"
                graph.add_node(Node(node_id, x, y, name))
                ring_nodes[ring].append(node_id)
        
        # Connect center to inner ring
        for node_id in ring_nodes[0]:
            center_node = graph.get_node(center_id)
            ring_node = graph.get_node(node_id)
            distance = math.sqrt((ring_node.x - center_node.x)**2 + (ring_node.y - center_node.y)**2)
            weight = distance * random.uniform(0.8, 1.2)
            graph.add_edge(Edge(center_id, node_id, weight, "Radial Avenue"))
            graph.add_edge(Edge(node_id, center_id, weight, "Radial Avenue"))
        
        # Connect rings
        for ring in range(len(ring_nodes)):
            # Ring connections (circular)
            nodes_in_ring = ring_nodes[ring]
            for i in range(len(nodes_in_ring)):
                current = nodes_in_ring[i]
                next_node = nodes_in_ring[(i + 1) % len(nodes_in_ring)]
                
                curr_node = graph.get_node(current)
                next_node_obj = graph.get_node(next_node)
                distance = math.sqrt((next_node_obj.x - curr_node.x)**2 + (next_node_obj.y - curr_node.y)**2)
                weight = distance * random.uniform(0.8, 1.2)
                graph.add_edge(Edge(current, next_node, weight, f"Ring {ring}"))
                graph.add_edge(Edge(next_node, current, weight, f"Ring {ring}"))
            
            # Radial connections to next ring
            if ring < len(ring_nodes) - 1:
                for i, node_id in enumerate(ring_nodes[ring]):
                    # Connect to corresponding node in next ring
                    next_ring_nodes = ring_nodes[ring + 1]
                    target_idx = int(i * len(next_ring_nodes) / len(ring_nodes[ring]))
                    target = next_ring_nodes[target_idx]
                    
                    curr_node = graph.get_node(node_id)
                    target_node = graph.get_node(target)
                    distance = math.sqrt((target_node.x - curr_node.x)**2 + (target_node.y - curr_node.y)**2)
                    weight = distance * random.uniform(0.8, 1.2)
                    graph.add_edge(Edge(node_id, target, weight, f"Radial {ring+1}"))
                    graph.add_edge(Edge(target, node_id, weight, f"Radial {ring+1}"))
        
        return graph
    
    def generate_organic_city(self, num_nodes: int, connectivity: float = 0.15) -> Graph:
        """Generate an organic city layout (like old European cities)"""
        graph = Graph()
        
        # Generate nodes with clustering tendency
        nodes = []
        num_clusters = max(3, num_nodes // 20)
        
        for cluster in range(num_clusters):
            cluster_center_x = random.uniform(-10, 10)
            cluster_center_y = random.uniform(-10, 10)
            cluster_size = num_nodes // num_clusters + random.randint(-5, 5)
            
            for i in range(cluster_size):
                # Normal distribution around cluster center
                x = cluster_center_x + random.gauss(0, 2)
                y = cluster_center_y + random.gauss(0, 2)
                node_id = f"C{cluster}_N{i}"
                name = f"Cluster {cluster}, Node {i}"
                graph.add_node(Node(node_id, x, y, name))
                nodes.append((node_id, cluster_center_x, cluster_center_y))
        
        # Create edges based on proximity and cluster connectivity
        node_list = list(graph.nodes.keys())
        
        for i, node1_id in enumerate(node_list):
            node1 = graph.get_node(node1_id)
            
            # Connect to nearby nodes
            for j, node2_id in enumerate(node_list):
                if i >= j:  # Avoid duplicates
                    continue
                
                node2 = graph.get_node(node2_id)
                distance = math.sqrt((node2.x - node1.x)**2 + (node2.y - node1.y)**2)
                
                # Probability of connection decreases with distance
                connection_prob = math.exp(-distance / 3.0) * connectivity
                
                if random.random() < connection_prob:
                    weight = distance * random.uniform(0.7, 1.3)
                    graph.add_edge(Edge(node1_id, node2_id, weight, f"Road {i}-{j}"))
                    
                    # Make some roads bidirectional
                    if random.random() < 0.7:
                        graph.add_edge(Edge(node2_id, node1_id, weight, f"Road {j}-{i}"))
        
        return graph
    
    def generate_highway_network(self, num_cities: int, highway_density: float = 0.3) -> Graph:
        """Generate a highway network connecting multiple cities"""
        graph = Graph()
        
        # Generate city centers
        cities = []
        for i in range(num_cities):
            x = random.uniform(-20, 20)
            y = random.uniform(-20, 20)
            city_id = f"CITY_{i}"
            name = f"City {i}"
            graph.add_node(Node(city_id, x, y, name))
            cities.append((city_id, x, y))
        
        # Create highway connections between cities
        for i, (city1_id, x1, y1) in enumerate(cities):
            for j, (city2_id, x2, y2) in enumerate(cities):
                if i >= j:
                    continue
                
                distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                
                # Higher probability for connections between closer cities
                connection_prob = math.exp(-distance / 10.0) * highway_density
                
                if random.random() < connection_prob:
                    weight = distance * 0.8  # Highways are faster
                    highway_name = f"Highway {city1_id}-{city2_id}"
                    graph.add_edge(Edge(city1_id, city2_id, weight, highway_name))
                    graph.add_edge(Edge(city2_id, city1_id, weight, highway_name))
        
        # Add local roads within cities
        for city_id, x, y in cities:
            # Add suburban nodes around each city
            num_suburbs = random.randint(3, 8)
            for i in range(num_suburbs):
                angle = 2 * math.pi * i / num_suburbs
                suburb_x = x + random.uniform(1, 3) * math.cos(angle)
                suburb_y = y + random.uniform(1, 3) * math.sin(angle)
                suburb_id = f"{city_id}_SUB{i}"
                suburb_name = f"Suburb {i} of {city_id}"
                graph.add_node(Node(suburb_id, suburb_x, suburb_y, suburb_name))
                
                # Connect suburb to city
                distance = math.sqrt((suburb_x - x)**2 + (suburb_y - y)**2)
                weight = distance * 1.2  # Local roads are slower
                graph.add_edge(Edge(suburb_id, city_id, weight, f"Local Road {i}"))
                graph.add_edge(Edge(city_id, suburb_id, weight, f"Local Road {i}"))
        
        return graph
    
    def add_traffic_patterns(self, graph: Graph, peak_hours_factor: float = 1.5) -> Graph:
        """Add realistic traffic patterns to the graph"""
        # Identify major roads (higher connectivity)
        edge_usage = {}
        for from_node in graph.edges:
            for edge in graph.edges[from_node]:
                edge_key = (edge.from_node, edge.to_node)
                edge_usage[edge_key] = 0
        
        # Count connections to identify major roads
        for node_id in graph.nodes:
            for edge in graph.edges.get(node_id, []):
                edge_key = (edge.from_node, edge.to_node)
                edge_usage[edge_key] += 1
        
        # Apply traffic multipliers
        for from_node in graph.edges:
            new_edges = []
            for edge in graph.edges[from_node]:
                edge_key = (edge.from_node, edge.to_node)
                usage = edge_usage.get(edge_key, 0)
                
                # Major roads get less traffic impact
                if usage > 3:
                    traffic_factor = random.uniform(0.9, 1.1)
                else:
                    traffic_factor = random.uniform(1.0, peak_hours_factor)
                
                new_weight = edge.weight * traffic_factor
                new_edges.append(Edge(edge.from_node, edge.to_node, new_weight, edge.name))
            
            graph.edges[from_node] = new_edges
            # Update adjacency list
            graph.adjacency_list[from_node] = {edge.to_node: edge.weight for edge in new_edges}
        
        return graph
    
    def save_graph_to_file(self, graph: Graph, filename: str):
        """Save graph structure to JSON file"""
        data = {
            'nodes': [],
            'edges': []
        }
        
        for node_id, node in graph.nodes.items():
            data['nodes'].append({
                'id': node.id,
                'x': node.x,
                'y': node.y,
                'name': node.name
            })
        
        for from_node in graph.edges:
            for edge in graph.edges[from_node]:
                data['edges'].append({
                    'from': edge.from_node,
                    'to': edge.to_node,
                    'weight': edge.weight,
                    'name': edge.name
                })
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_graph_from_file(self, filename: str) -> Graph:
        """Load graph structure from JSON file"""
        with open(filename, 'r') as f:
            data = json.load(f)
        
        graph = Graph()
        
        # Load nodes
        for node_data in data['nodes']:
            node = Node(
                node_data['id'],
                node_data['x'],
                node_data['y'],
                node_data['name']
            )
            graph.add_node(node)
        
        # Load edges
        for edge_data in data['edges']:
            edge = Edge(
                edge_data['from'],
                edge_data['to'],
                edge_data['weight'],
                edge_data['name']
            )
            graph.add_edge(edge)
        
        return graph

class TestScenarioGenerator:
    """Generates specific test scenarios for algorithm evaluation"""
    
    def __init__(self):
        self.city_generator = CityGraphGenerator()
    
    def create_small_city_test(self) -> Graph:
        """Create a small city for basic testing"""
        return self.city_generator.generate_grid_city(5, 5, 1.0)
    
    def create_medium_city_test(self) -> Graph:
        """Create a medium-sized city for performance testing"""
        return self.city_generator.generate_organic_city(50, 0.2)
    
    def create_large_city_test(self) -> Graph:
        """Create a large city for scalability testing"""
        return self.city_generator.generate_radial_city(5, [6, 12, 18, 24, 30], 0.5)
    
    def create_highway_network_test(self) -> Graph:
        """Create a highway network for long-distance routing"""
        return self.city_generator.generate_highway_network(10, 0.4)
    
    def create_edge_case_scenarios(self) -> Dict[str, Graph]:
        """Create edge case scenarios for testing"""
        scenarios = {}
        
        # Disconnected graph
        disconnected = Graph()
        disconnected.add_node(Node("A", 0, 0, "Isolated A"))
        disconnected.add_node(Node("B", 1, 1, "Isolated B"))
        disconnected.add_node(Node("C", 2, 2, "Connected C"))
        disconnected.add_node(Node("D", 3, 3, "Connected D"))
        disconnected.add_edge(Edge("C", "D", 1.0, "Connection"))
        scenarios['disconnected'] = disconnected
        
        # Single path graph
        single_path = Graph()
        nodes = ["S", "1", "2", "3", "4", "E"]
        for i, node_id in enumerate(nodes):
            single_path.add_node(Node(node_id, i, 0, f"Node {node_id}"))
        
        for i in range(len(nodes) - 1):
            single_path.add_edge(Edge(nodes[i], nodes[i+1], 1.0, f"Path {i}"))
        scenarios['single_path'] = single_path
        
        # Fully connected graph
        fully_connected = Graph()
        for i in range(4):
            fully_connected.add_node(Node(chr(65+i), i, i, f"Node {chr(65+i)}"))
        
        for i in range(4):
            for j in range(4):
                if i != j:
                    weight = abs(i - j) + random.uniform(0.5, 1.5)
                    fully_connected.add_edge(Edge(chr(65+i), chr(65+j), weight, f"Edge {i}-{j}"))
        scenarios['fully_connected'] = fully_connected
        
        return scenarios
    
    def get_benchmark_test_pairs(self, graph: Graph) -> List[Tuple[str, str]]:
        """Generate test pairs for benchmarking"""
        nodes = list(graph.nodes.keys())
        pairs = []
        
        # Random pairs
        for _ in range(min(10, len(nodes) * 2)):
            start = random.choice(nodes)
            end = random.choice([n for n in nodes if n != start])
            pairs.append((start, end))
        
        # Distance-based pairs
        if len(nodes) >= 4:
            # Short distance
            pairs.append((nodes[0], nodes[1]))
            # Medium distance  
            pairs.append((nodes[0], nodes[len(nodes)//2]))
            # Long distance
            pairs.append((nodes[0], nodes[-1]))
        
        return pairs

def main():
    """Main function to demonstrate data generation"""
    print("Navigation Routing Data Generator")
    print("=" * 40)
    
    generator = CityGraphGenerator(seed=42)
    scenario_gen = TestScenarioGenerator()
    
    # Generate different city types
    print("Generating sample city graphs...")
    
    # Small grid city
    small_city = generator.generate_grid_city(4, 4, 1.0)
    print(f"Small grid city: {len(small_city.nodes)} nodes, {sum(len(edges) for edges in small_city.edges.values())} edges")
    generator.save_graph_to_file(small_city, "small_grid_city.json")
    
    # Medium organic city
    medium_city = generator.generate_organic_city(30, 0.2)
    print(f"Medium organic city: {len(medium_city.nodes)} nodes, {sum(len(edges) for edges in medium_city.edges.values())} edges")
    generator.save_graph_to_file(medium_city, "medium_organic_city.json")
    
    # Large radial city
    large_city = generator.generate_radial_city(4, [8, 16, 24, 32], 0.5)
    print(f"Large radial city: {len(large_city.nodes)} nodes, {sum(len(edges) for edges in large_city.edges.values())} edges")
    generator.save_graph_to_file(large_city, "large_radial_city.json")
    
    # Highway network
    highway_network = generator.generate_highway_network(8, 0.3)
    print(f"Highway network: {len(highway_network.nodes)} nodes, {sum(len(edges) for edges in highway_network.edges.values())} edges")
    generator.save_graph_to_file(highway_network, "highway_network.json")
    
    # Generate edge cases
    edge_cases = scenario_gen.create_edge_case_scenarios()
    for name, graph in edge_cases.items():
        print(f"Edge case '{name}': {len(graph.nodes)} nodes, {sum(len(edges) for edges in graph.edges.values())} edges")
        generator.save_graph_to_file(graph, f"edge_case_{name}.json")
    
    print("\nAll sample graphs saved to JSON files!")
    print("You can use these files for testing and benchmarking.")

if __name__ == "__main__":
    main()
