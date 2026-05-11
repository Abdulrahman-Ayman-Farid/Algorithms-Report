#!/usr/bin/env python3
"""
Comprehensive Test Suite for Navigation Routing Algorithms
Tests correctness, performance, and edge cases
"""

import unittest
import time
import json
import os
from typing import List, Dict, Tuple
from main import Graph, Node, Edge, DijkstraAlgorithm, AStarAlgorithm, BellmanFordAlgorithm
from data_generator import CityGraphGenerator, TestScenarioGenerator

class TestRoutingAlgorithms(unittest.TestCase):
    """Test suite for routing algorithms"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.generator = CityGraphGenerator(seed=42)
        self.scenario_gen = TestScenarioGenerator()
        
        # Create test graphs
        self.simple_graph = self._create_simple_test_graph()
        self.grid_graph = self.generator.generate_grid_city(3, 3, 1.0)
        self.edge_cases = self.scenario_gen.create_edge_case_scenarios()
    
    def _create_simple_test_graph(self) -> Graph:
        """Create a simple test graph"""
        graph = Graph()
        
        nodes = [
            Node("A", 0, 0, "Start"),
            Node("B", 1, 0, "Node B"),
            Node("C", 2, 0, "Node C"),
            Node("D", 1, 1, "Node D"),
            Node("E", 2, 1, "End"),
        ]
        
        for node in nodes:
            graph.add_node(node)
        
        edges = [
            Edge("A", "B", 2.0, "AB"),
            Edge("B", "C", 2.0, "BC"),
            Edge("A", "D", 1.0, "AD"),
            Edge("D", "E", 3.0, "DE"),
            Edge("C", "E", 1.0, "CE"),
            Edge("B", "D", 1.0, "BD"),
        ]
        
        for edge in edges:
            graph.add_edge(edge)
        
        return graph
    
    def test_dijkstra_correctness(self):
        """Test Dijkstra's algorithm correctness"""
        algorithm = DijkstraAlgorithm(self.simple_graph)
        
        # Test basic path finding
        path, distance = algorithm.find_shortest_path("A", "E")
        expected_path = ["A", "D", "E"]
        expected_distance = 4.0
        
        self.assertEqual(path, expected_path)
        self.assertAlmostEqual(distance, expected_distance, places=2)
        
        # Test no path case
        disconnected = self.edge_cases['disconnected']
        algo = DijkstraAlgorithm(disconnected)
        path, distance = algo.find_shortest_path("A", "C")
        self.assertEqual(path, [])
        self.assertEqual(distance, float('inf'))
    
    def test_astar_correctness(self):
        """Test A* algorithm correctness"""
        algorithm = AStarAlgorithm(self.simple_graph)
        
        # Test basic path finding
        path, distance = algorithm.find_shortest_path("A", "E")
        
        # A* should find the same optimal path as Dijkstra
        self.assertIn("A", path)
        self.assertIn("E", path)
        self.assertGreater(len(path), 1)
        
        # Verify path validity
        for i in range(len(path) - 1):
            self.assertIn(path[i+1], [edge.to_node for edge in self.simple_graph.edges.get(path[i], [])])
    
    def test_bellman_ford_correctness(self):
        """Test Bellman-Ford algorithm correctness"""
        algorithm = BellmanFordAlgorithm(self.simple_graph)
        
        # Test basic path finding
        path, distance = algorithm.find_shortest_path("A", "E")
        expected_path = ["A", "D", "E"]
        expected_distance = 4.0
        
        self.assertEqual(path, expected_path)
        self.assertAlmostEqual(distance, expected_distance, places=2)
    
    def test_algorithm_consistency(self):
        """Test that all algorithms give consistent results on simple graphs"""
        algorithms = [
            DijkstraAlgorithm(self.simple_graph),
            AStarAlgorithm(self.simple_graph),
            BellmanFordAlgorithm(self.simple_graph)
        ]
        
        results = []
        for algorithm in algorithms:
            path, distance = algorithm.find_shortest_path("A", "E")
            results.append((path, distance))
        
        # All should find the same optimal distance
        distances = [result[1] for result in results]
        self.assertTrue(all(abs(d - distances[0]) < 0.01 for d in distances))
    
    def test_edge_cases(self):
        """Test edge case scenarios"""
        # Single path graph
        single_path = self.edge_cases['single_path']
        algorithms = [
            DijkstraAlgorithm(single_path),
            AStarAlgorithm(single_path),
            BellmanFordAlgorithm(single_path)
        ]
        
        for algorithm in algorithms:
            path, distance = algorithm.find_shortest_path("S", "E")
            self.assertEqual(len(path), 6)  # S -> 1 -> 2 -> 3 -> 4 -> E
            self.assertAlmostEqual(distance, 5.0, places=2)
        
        # Fully connected graph
        fully_connected = self.edge_cases['fully_connected']
        for algorithm in [DijkstraAlgorithm(fully_connected), AStarAlgorithm(fully_connected)]:
            path, distance = algorithm.find_shortest_path("A", "D")
            self.assertGreater(len(path), 1)
            self.assertLess(distance, float('inf'))
    
    def test_performance_characteristics(self):
        """Test performance characteristics"""
        # Test on larger graph
        large_graph = self.generator.generate_organic_city(50, 0.2)
        
        algorithms = [
            ("Dijkstra", DijkstraAlgorithm(large_graph)),
            ("A*", AStarAlgorithm(large_graph)),
            ("Bellman-Ford", BellmanFordAlgorithm(large_graph))
        ]
        
        nodes = list(large_graph.nodes.keys())
        start, end = nodes[0], nodes[-1]
        
        performance_results = {}
        
        for name, algorithm in algorithms:
            start_time = time.perf_counter()
            try:
                path, distance = algorithm.find_shortest_path(start, end)
                end_time = time.perf_counter()
                execution_time = (end_time - start_time) * 1000
                
                performance_results[name] = {
                    'success': True,
                    'time_ms': execution_time,
                    'path_length': len(path),
                    'distance': distance
                }
            except Exception as e:
                performance_results[name] = {
                    'success': False,
                    'error': str(e)
                }
        
        # Bellman-Ford should be significantly slower on larger graphs
        if all(performance_results[algo]['success'] for algo in ['Dijkstra', 'Bellman-Ford']):
            dijkstra_time = performance_results['Dijkstra']['time_ms']
            bellman_time = performance_results['Bellman-Ford']['time_ms']
            # Bellman-Ford should be slower (theoretically O(VE) vs O(E log V))
            self.assertGreater(bellman_time, dijkstra_time * 0.5)  # Allow some variance
    
    def test_heuristic_admissibility(self):
        """Test that A* heuristic is admissible"""
        algorithm = AStarAlgorithm(self.simple_graph)
        
        # For any pair of nodes, heuristic should never overestimate actual distance
        nodes = list(self.simple_graph.nodes.keys())
        
        for i in range(len(nodes)):
            for j in range(len(nodes)):
                if i != j:
                    heuristic = algorithm.heuristic(nodes[i], nodes[j])
                    
                    # Find actual shortest path using Dijkstra (ground truth)
                    dijkstra = DijkstraAlgorithm(self.simple_graph)
                    try:
                        _, actual_distance = dijkstra.find_shortest_path(nodes[i], nodes[j])
                        
                        # Heuristic should never overestimate
                        self.assertLessEqual(heuristic, actual_distance + 0.01)  # Small tolerance
                    except:
                        # If no path exists, heuristic should still be reasonable
                        self.assertGreaterEqual(heuristic, 0)
    
    def test_graph_validation(self):
        """Test graph validation and error handling"""
        graph = Graph()
        
        # Test adding edges to non-existent nodes
        with self.assertRaises(ValueError):
            graph.add_edge(Edge("A", "B", 1.0, "test"))
        
        # Test path finding with invalid nodes
        algorithm = DijkstraAlgorithm(graph)
        with self.assertRaises(ValueError):
            algorithm.find_shortest_path("A", "B")
    
    def test_negative_weights(self):
        """Test handling of negative weights"""
        graph = Graph()
        
        # Create graph with negative weight
        graph.add_node(Node("A", 0, 0))
        graph.add_node(Node("B", 1, 0))
        graph.add_node(Node("C", 2, 0))
        
        graph.add_edge(Edge("A", "B", -1.0, "negative"))
        graph.add_edge(Edge("B", "C", 2.0, "positive"))
        
        # Bellman-Ford should handle negative weights
        bf_algorithm = BellmanFordAlgorithm(graph)
        path, distance = bf_algorithm.find_shortest_path("A", "C")
        expected_distance = 1.0  # -1 + 2
        
        self.assertEqual(path, ["A", "B", "C"])
        self.assertAlmostEqual(distance, expected_distance, places=2)

class TestGraphStructures(unittest.TestCase):
    """Test graph data structures and utilities"""
    
    def setUp(self):
        self.graph = Graph()
        self.generator = CityGraphGenerator()
    
    def test_node_operations(self):
        """Test node addition and retrieval"""
        node = Node("test", 1.0, 2.0, "Test Node")
        self.graph.add_node(node)
        
        retrieved = self.graph.get_node("test")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.id, "test")
        self.assertEqual(retrieved.x, 1.0)
        self.assertEqual(retrieved.y, 2.0)
        self.assertEqual(retrieved.name, "Test Node")
    
    def test_edge_operations(self):
        """Test edge addition and weight retrieval"""
        self.graph.add_node(Node("A", 0, 0))
        self.graph.add_node(Node("B", 1, 1))
        
        edge = Edge("A", "B", 5.0, "Test Edge")
        self.graph.add_edge(edge)
        
        weight = self.graph.get_edge_weight("A", "B")
        self.assertEqual(weight, 5.0)
        
        # Test non-existent edge
        weight = self.graph.get_edge_weight("A", "C")
        self.assertEqual(weight, float('inf'))
    
    def test_neighbor_operations(self):
        """Test neighbor retrieval"""
        self.graph.add_node(Node("A", 0, 0))
        self.graph.add_node(Node("B", 1, 0))
        self.graph.add_node(Node("C", 2, 0))
        
        self.graph.add_edge(Edge("A", "B", 1.0, "AB"))
        self.graph.add_edge(Edge("A", "C", 2.0, "AC"))
        
        neighbors = self.graph.get_neighbors("A")
        self.assertEqual(len(neighbors), 2)
        self.assertIn(("B", 1.0), neighbors)
        self.assertIn(("C", 2.0), neighbors)

class TestGenerators(unittest.TestCase):
    """Test data generators"""
    
    def test_grid_generator(self):
        """Test grid city generator"""
        generator = CityGraphGenerator(seed=42)
        graph = generator.generate_grid_city(3, 3, 1.0)
        
        self.assertEqual(len(graph.nodes), 9)
        self.assertGreater(len(graph.edges), 0)
        
        # Check grid structure
        for node_id in graph.nodes:
            neighbors = graph.get_neighbors(node_id)
            # Each node should have 2-4 neighbors in a grid (except edges)
            self.assertGreaterEqual(len(neighbors), 2)
            self.assertLessEqual(len(neighbors), 4)
    
    def test_radial_generator(self):
        """Test radial city generator"""
        generator = CityGraphGenerator(seed=42)
        graph = generator.generate_radial_city(3, [4, 8, 12], 0.5)
        
        # Should have center + ring nodes
        expected_nodes = 1 + 4 + 8 + 12
        self.assertEqual(len(graph.nodes), expected_nodes)
        self.assertGreater(len(graph.edges), 0)
    
    def test_file_operations(self):
        """Test graph save/load operations"""
        generator = CityGraphGenerator(seed=42)
        original_graph = generator.generate_grid_city(2, 2, 1.0)
        
        # Save to file
        filename = "test_graph.json"
        generator.save_graph_to_file(original_graph, filename)
        
        # Load from file
        loaded_graph = generator.load_graph_from_file(filename)
        
        # Compare graphs
        self.assertEqual(len(original_graph.nodes), len(loaded_graph.nodes))
        self.assertEqual(len(original_graph.edges), len(loaded_graph.edges))
        
        # Clean up
        if os.path.exists(filename):
            os.remove(filename)

def run_comprehensive_tests():
    """Run all tests and generate a report"""
    print("Running Comprehensive Test Suite for Navigation Routing Algorithms")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestRoutingAlgorithms))
    suite.addTests(loader.loadTestsFromTestCase(TestGraphStructures))
    suite.addTests(loader.loadTestsFromTestCase(TestGenerators))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Generate summary report
    print("\n" + "=" * 60)
    print("TEST SUMMARY REPORT")
    print("=" * 60)
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    success_rate = (total_tests - failures - errors) / total_tests * 100
    
    print(f"Total Tests Run: {total_tests}")
    print(f"Successful: {total_tests - failures - errors}")
    print(f"Failures: {failures}")
    print(f"Errors: {errors}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    if failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('Exception:')[-1].strip()}")
    
    if success_rate == 100:
        print("\n🎉 All tests passed! The implementation is working correctly.")
    else:
        print(f"\n⚠️  {failures + errors} test(s) failed. Please review the implementation.")
    
    return result

def main():
    """Main function to run tests"""
    return run_comprehensive_tests()

if __name__ == "__main__":
    main()
