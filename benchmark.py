#!/usr/bin/env python3
"""
Performance Benchmarking Module for Navigation Routing Algorithms
Compares Dijkstra, A*, and Bellman-Ford algorithms across various metrics
"""

import time
import random
import statistics
from typing import List, Dict, Tuple, Any
from main import Graph, Node, Edge, DijkstraAlgorithm, AStarAlgorithm, BellmanFordAlgorithm

class PerformanceBenchmark:
    """Benchmarking suite for routing algorithms"""
    
    def __init__(self):
        self.results = {}
    
    def generate_random_city_graph(self, num_nodes: int, edge_density: float = 0.3) -> Graph:
        """Generate a random city graph for testing"""
        graph = Graph()
        
        # Generate nodes with random coordinates (simulating city layout)
        for i in range(num_nodes):
            node_id = f"N{i}"
            # Simulate city coordinates within a reasonable range
            x = random.uniform(-10, 10)  # Longitude range
            y = random.uniform(-10, 10)  # Latitude range
            graph.add_node(Node(node_id, x, y, f"Intersection {i}"))
        
        # Generate edges based on density
        node_ids = list(graph.nodes.keys())
        max_edges = num_nodes * (num_nodes - 1)  # Directed graph
        
        for i in range(int(max_edges * edge_density)):
            from_node = random.choice(node_ids)
            to_node = random.choice(node_ids)
            
            if from_node != to_node:
                # Calculate distance-based weight (simulating travel time)
                n1 = graph.get_node(from_node)
                n2 = graph.get_node(to_node)
                distance = ((n2.x - n1.x) ** 2 + (n2.y - n1.y) ** 2) ** 0.5
                weight = distance * random.uniform(0.5, 2.0)  # Add traffic variation
                
                graph.add_edge(Edge(from_node, to_node, weight, f"Road {i}"))
        
        return graph
    
    def benchmark_single_query(self, algorithm, start: str, end: str) -> Dict[str, Any]:
        """Benchmark a single routing query"""
        start_time = time.perf_counter()
        
        try:
            path, distance = algorithm.find_shortest_path(start, end)
            end_time = time.perf_counter()
            
            return {
                'success': True,
                'path_length': len(path),
                'distance': distance,
                'execution_time_ms': (end_time - start_time) * 1000,
                'path': path
            }
        except Exception as e:
            end_time = time.perf_counter()
            return {
                'success': False,
                'error': str(e),
                'execution_time_ms': (end_time - start_time) * 1000,
                'path_length': 0,
                'distance': float('inf')
            }
    
    def run_comprehensive_benchmark(self, graph_sizes: List[int], trials_per_size: int = 10) -> Dict[str, Any]:
        """Run comprehensive benchmark across different graph sizes"""
        algorithms = {
            'Dijkstra': DijkstraAlgorithm,
            'A*': AStarAlgorithm,
            'Bellman-Ford': BellmanFordAlgorithm
        }
        
        results = {
            'graph_sizes': graph_sizes,
            'trials_per_size': trials_per_size,
            'algorithm_results': {size: {name: [] for name in algorithms.keys()} for size in graph_sizes}
        }
        
        for size in graph_sizes:
            print(f"\nBenchmarking graph size: {size} nodes")
            print("-" * 40)
            
            for trial in range(trials_per_size):
                # Generate random graph
                graph = self.generate_random_city_graph(size, edge_density=0.2)
                
                # Select random start and end nodes
                nodes = list(graph.nodes.keys())
                start_node = random.choice(nodes)
                end_node = random.choice([n for n in nodes if n != start_node])
                
                # Test each algorithm
                for algo_name, algo_class in algorithms.items():
                    algorithm = algo_class(graph)
                    result = self.benchmark_single_query(algorithm, start_node, end_node)
                    
                    results['algorithm_results'][size][algo_name].append(result)
                
                if trial % 5 == 0:
                    print(f"  Completed trial {trial + 1}/{trials_per_size}")
        
        return results
    
    def analyze_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze benchmark results and compute statistics"""
        analysis = {
            'summary': {},
            'detailed_stats': {}
        }
        
        for size in results['graph_sizes']:
            size_analysis = {}
            
            for algo_name in results['algorithm_results'][size]:
                algo_results = results['algorithm_results'][size][algo_name]
                
                # Filter successful results
                successful = [r for r in algo_results if r['success']]
                
                if successful:
                    execution_times = [r['execution_time_ms'] for r in successful]
                    path_lengths = [r['path_length'] for r in successful]
                    distances = [r['distance'] for r in successful]
                    
                    size_analysis[algo_name] = {
                        'success_rate': len(successful) / len(algo_results),
                        'avg_execution_time_ms': statistics.mean(execution_times),
                        'median_execution_time_ms': statistics.median(execution_times),
                        'std_execution_time_ms': statistics.stdev(execution_times) if len(execution_times) > 1 else 0,
                        'min_execution_time_ms': min(execution_times),
                        'max_execution_time_ms': max(execution_times),
                        'avg_path_length': statistics.mean(path_lengths),
                        'avg_distance': statistics.mean(distances)
                    }
                else:
                    size_analysis[algo_name] = {
                        'success_rate': 0,
                        'error': 'No successful executions'
                    }
            
            analysis['detailed_stats'][size] = size_analysis
        
        # Create summary comparing algorithms
        analysis['summary'] = self._create_algorithm_comparison(analysis['detailed_stats'])
        
        return analysis
    
    def _create_algorithm_comparison(self, detailed_stats: Dict) -> Dict[str, Any]:
        """Create comparison summary between algorithms"""
        comparison = {
            'speed_ranking': {},
            'scalability_analysis': {},
            'recommendations': []
        }
        
        # Analyze speed across different graph sizes
        for size in detailed_stats:
            speed_comparison = {}
            
            for algo_name in detailed_stats[size]:
                if 'avg_execution_time_ms' in detailed_stats[size][algo_name]:
                    speed_comparison[algo_name] = detailed_stats[size][algo_name]['avg_execution_time_ms']
            
            if speed_comparison:
                # Sort by execution time (fastest first)
                sorted_algos = sorted(speed_comparison.items(), key=lambda x: x[1])
                comparison['speed_ranking'][size] = [algo[0] for algo in sorted_algos]
        
        # Analyze scalability (how performance changes with graph size)
        algorithms = set()
        for size_stats in detailed_stats.values():
            algorithms.update(size_stats.keys())
        
        for algo in algorithms:
            times = []
            sizes = []
            
            for size in sorted(detailed_stats.keys()):
                if algo in detailed_stats[size] and 'avg_execution_time_ms' in detailed_stats[size][algo]:
                    times.append(detailed_stats[size][algo]['avg_execution_time_ms'])
                    sizes.append(size)
            
            if len(times) > 1:
                # Simple scalability metric: time growth rate
                growth_rate = (times[-1] / times[0]) if times[0] > 0 else float('inf')
                comparison['scalability_analysis'][algo] = {
                    'growth_rate': growth_rate,
                    'small_graph_time': times[0],
                    'large_graph_time': times[-1]
                }
        
        # Generate recommendations based on analysis
        comparison['recommendations'] = self._generate_recommendations(comparison)
        
        return comparison
    
    def _generate_recommendations(self, comparison: Dict) -> List[str]:
        """Generate recommendations based on benchmark results"""
        recommendations = []
        
        # Speed recommendations
        if 'speed_ranking' in comparison and comparison['speed_ranking']:
            latest_ranking = list(comparison['speed_ranking'].values())[-1]
            if latest_ranking:
                fastest = latest_ranking[0]
                recommendations.append(f"Fastest algorithm: {fastest}")
        
        # Scalability recommendations
        if 'scalability_analysis' in comparison:
            best_scalability = min(comparison['scalability_analysis'].items(), 
                                 key=lambda x: x[1]['growth_rate'])
            recommendations.append(f"Best scalability: {best_scalability[0]} (growth rate: {best_scalability[1]['growth_rate']:.2f}x)")
        
        # General recommendations based on the report findings
        recommendations.extend([
            "A* is recommended for real-time navigation due to heuristic optimization",
            "Dijkstra is recommended as a reliable baseline and fallback",
            "Bellman-Ford is not recommended for routing due to O(V*E) complexity"
        ])
        
        return recommendations
    
    def print_benchmark_report(self, results: Dict[str, Any], analysis: Dict[str, Any]):
        """Print a comprehensive benchmark report"""
        print("\n" + "=" * 60)
        print("NAVIGATION ROUTING ALGORITHM BENCHMARK REPORT")
        print("=" * 60)
        
        print(f"\nTest Configuration:")
        print(f"  Graph sizes tested: {results['graph_sizes']}")
        print(f"  Trials per size: {results['trials_per_size']}")
        
        print("\nPerformance Summary by Graph Size:")
        print("-" * 50)
        
        for size in sorted(analysis['detailed_stats'].keys()):
            print(f"\nGraph Size: {size} nodes")
            print("  " + "-" * 40)
            
            for algo_name in sorted(analysis['detailed_stats'][size].keys()):
                stats = analysis['detailed_stats'][size][algo_name]
                
                if 'avg_execution_time_ms' in stats:
                    print(f"  {algo_name}:")
                    print(f"    Success Rate: {stats['success_rate']:.1%}")
                    print(f"    Avg Time: {stats['avg_execution_time_ms']:.3f} ms")
                    print(f"    Median Time: {stats['median_execution_time_ms']:.3f} ms")
                    print(f"    Std Dev: {stats['std_execution_time_ms']:.3f} ms")
                    print(f"    Avg Path Length: {stats['avg_path_length']:.1f} nodes")
                else:
                    print(f"  {algo_name}: {stats.get('error', 'No data')}")
        
        print("\nAlgorithm Rankings by Speed:")
        print("-" * 50)
        for size in sorted(analysis['summary']['speed_ranking'].keys()):
            ranking = analysis['summary']['speed_ranking'][size]
            print(f"  Size {size}: {' > '.join(ranking)}")
        
        print("\nScalability Analysis:")
        print("-" * 50)
        for algo, data in analysis['summary']['scalability_analysis'].items():
            print(f"  {algo}:")
            print(f"    Growth Rate: {data['growth_rate']:.2f}x")
            print(f"    Small Graph: {data['small_graph_time']:.3f} ms")
            print(f"    Large Graph: {data['large_graph_time']:.3f} ms")
        
        print("\nRecommendations:")
        print("-" * 50)
        for i, rec in enumerate(analysis['summary']['recommendations'], 1):
            print(f"  {i}. {rec}")

def main():
    """Main benchmarking function"""
    print("Navigation Routing Algorithm Performance Benchmark")
    print("Based on Algorithm Analysis Report Findings")
    print("=" * 50)
    
    benchmark = PerformanceBenchmark()
    
    # Define test parameters (smaller sizes for demo, can be increased)
    graph_sizes = [10, 25, 50, 100]
    trials_per_size = 5
    
    print(f"Starting benchmark with graph sizes: {graph_sizes}")
    print(f"Running {trials_per_size} trials per size")
    
    # Run benchmark
    results = benchmark.run_comprehensive_benchmark(graph_sizes, trials_per_size)
    
    # Analyze results
    analysis = benchmark.analyze_results(results)
    
    # Print report
    benchmark.print_benchmark_report(results, analysis)
    
    return results, analysis

if __name__ == "__main__":
    main()
