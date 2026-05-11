#!/usr/bin/env python3
"""
Visualization Module for Navigation Routing Algorithms
Provides visual representations of graphs, paths, and performance comparisons
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import seaborn as sns
from typing import List, Dict, Tuple, Any, Optional
import pandas as pd
from main import Graph, Node, Edge, RoutingAlgorithm

class RoutingVisualizer:
    """Visualizer for routing algorithms and results"""
    
    def __init__(self):
        # Set up plotting style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
    
    def plot_graph_with_path(self, graph: Graph, algorithm: RoutingAlgorithm, 
                           start_node: str, end_node: str, title: str = "Routing Visualization"):
        """Plot the graph with the shortest path highlighted"""
        try:
            path, distance = algorithm.find_shortest_path(start_node, end_node)
        except Exception as e:
            print(f"Error finding path: {e}")
            return
        
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Plot all edges
        for from_node_id, edges in graph.edges.items():
            from_node = graph.get_node(from_node_id)
            for edge in edges:
                to_node = graph.get_node(edge.to_node)
                ax.plot([from_node.x, to_node.x], [from_node.y, to_node.y], 
                       'gray', alpha=0.3, linewidth=1, zorder=1)
        
        # Highlight the shortest path
        if len(path) > 1:
            for i in range(len(path) - 1):
                from_node = graph.get_node(path[i])
                to_node = graph.get_node(path[i + 1])
                ax.plot([from_node.x, to_node.x], [from_node.y, to_node.y], 
                       'red', linewidth=3, alpha=0.8, zorder=3)
        
        # Plot all nodes
        for node_id, node in graph.nodes.items():
            color = 'green' if node_id == start_node else 'blue' if node_id == end_node else 'lightblue'
            size = 200 if node_id in [start_node, end_node] else 100
            
            ax.scatter(node.x, node.y, c=color, s=size, alpha=0.8, zorder=2)
            ax.annotate(node_id, (node.x, node.y), xytext=(5, 5), 
                       textcoords='offset points', fontsize=8, fontweight='bold')
        
        # Add legend
        legend_elements = [
            patches.Patch(color='green', label='Start Node'),
            patches.Patch(color='blue', label='End Node'),
            patches.Patch(color='lightblue', label='Regular Node'),
            patches.Patch(color='red', label='Shortest Path')
        ]
        ax.legend(handles=legend_elements, loc='upper right')
        
        ax.set_title(f"{title}\n{algorithm.get_algorithm_name()}: {start_node} → {end_node}\n"
                    f"Path: {' → '.join(path)} | Distance: {distance:.2f}", 
                    fontsize=14, fontweight='bold')
        ax.set_xlabel("Longitude", fontsize=12)
        ax.set_ylabel("Latitude", fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')
        
        plt.tight_layout()
        plt.show()
    
    def compare_algorithm_paths(self, graph: Graph, algorithms: List[RoutingAlgorithm], 
                              start_node: str, end_node: str):
        """Compare paths found by different algorithms side by side"""
        fig, axes = plt.subplots(1, len(algorithms), figsize=(6*len(algorithms), 6))
        
        if len(algorithms) == 1:
            axes = [axes]
        
        for idx, algorithm in enumerate(algorithms):
            ax = axes[idx]
            
            try:
                path, distance = algorithm.find_shortest_path(start_node, end_node)
                path_str = f"Path: {' → '.join(path)}" if path else "No path found"
                distance_str = f"Distance: {distance:.2f}" if distance != float('inf') else "Distance: ∞"
            except Exception as e:
                path_str = f"Error: {e}"
                distance_str = ""
                path = []
            
            # Plot edges
            for from_node_id, edges in graph.edges.items():
                from_node = graph.get_node(from_node_id)
                for edge in edges:
                    to_node = graph.get_node(edge.to_node)
                    ax.plot([from_node.x, to_node.x], [from_node.y, to_node.y], 
                           'gray', alpha=0.3, linewidth=1)
            
            # Highlight path if found
            if len(path) > 1:
                for i in range(len(path) - 1):
                    from_node = graph.get_node(path[i])
                    to_node = graph.get_node(path[i + 1])
                    ax.plot([from_node.x, to_node.x], [from_node.y, to_node.y], 
                           'red', linewidth=3, alpha=0.8)
            
            # Plot nodes
            for node_id, node in graph.nodes.items():
                color = 'green' if node_id == start_node else 'blue' if node_id == end_node else 'lightblue'
                size = 150 if node_id in [start_node, end_node] else 80
                ax.scatter(node.x, node.y, c=color, s=size, alpha=0.8)
                ax.annotate(node_id, (node.x, node.y), xytext=(3, 3), 
                           textcoords='offset points', fontsize=7)
            
            ax.set_title(f"{algorithm.get_algorithm_name()}\n{path_str}\n{distance_str}", 
                        fontsize=10, fontweight='bold')
            ax.set_xlabel("Longitude")
            ax.set_ylabel("Latitude")
            ax.grid(True, alpha=0.3)
            ax.set_aspect('equal')
        
        plt.suptitle(f"Algorithm Comparison: {start_node} → {end_node}", 
                    fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.show()
    
    def plot_performance_comparison(self, benchmark_results: Dict[str, Any], 
                                  analysis: Dict[str, Any]):
        """Create performance comparison charts from benchmark results"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Prepare data
        graph_sizes = []
        algorithms = []
        execution_times = []
        success_rates = []
        
        for size in analysis['detailed_stats'].keys():
            for algo in analysis['detailed_stats'][size].keys():
                stats = analysis['detailed_stats'][size][algo]
                if 'avg_execution_time_ms' in stats:
                    graph_sizes.append(size)
                    algorithms.append(algo)
                    execution_times.append(stats['avg_execution_time_ms'])
                    success_rates.append(stats['success_rate'])
        
        df = pd.DataFrame({
            'Graph Size': graph_sizes,
            'Algorithm': algorithms,
            'Execution Time (ms)': execution_times,
            'Success Rate': success_rates
        })
        
        # 1. Execution Time vs Graph Size
        ax1 = axes[0, 0]
        for algo in df['Algorithm'].unique():
            algo_data = df[df['Algorithm'] == algo]
            ax1.plot(algo_data['Graph Size'], algo_data['Execution Time (ms)'], 
                    marker='o', label=algo, linewidth=2, markersize=6)
        
        ax1.set_xlabel('Graph Size (nodes)')
        ax1.set_ylabel('Execution Time (ms)')
        ax1.set_title('Execution Time vs Graph Size')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_yscale('log')
        
        # 2. Success Rate Comparison
        ax2 = axes[0, 1]
        success_pivot = df.pivot(index='Graph Size', columns='Algorithm', values='Success Rate')
        success_pivot.plot(kind='bar', ax=ax2, width=0.8)
        ax2.set_xlabel('Graph Size (nodes)')
        ax2.set_ylabel('Success Rate')
        ax2.set_title('Success Rate by Algorithm and Graph Size')
        ax2.legend(title='Algorithm')
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim(0, 1.1)
        
        # 3. Performance Ranking Heatmap
        ax3 = axes[1, 0]
        if 'speed_ranking' in analysis['summary']:
            ranking_data = []
            for size, ranking in analysis['summary']['speed_ranking'].items():
                for rank, algo in enumerate(ranking):
                    ranking_data.append({'Graph Size': size, 'Algorithm': algo, 'Rank': rank + 1})
            
            ranking_df = pd.DataFrame(ranking_data)
            ranking_pivot = ranking_df.pivot(index='Graph Size', columns='Algorithm', values='Rank')
            
            sns.heatmap(ranking_pivot, annot=True, fmt='d', cmap='RdYlGn_r', 
                       ax=ax3, cbar_kws={'label': 'Rank (1=Fastest)'})
            ax3.set_title('Algorithm Speed Ranking by Graph Size')
        
        # 4. Scalability Analysis
        ax4 = axes[1, 1]
        if 'scalability_analysis' in analysis['summary']:
            algos = list(analysis['summary']['scalability_analysis'].keys())
            growth_rates = [analysis['summary']['scalability_analysis'][algo]['growth_rate'] 
                          for algo in algos]
            
            bars = ax4.bar(algos, growth_rates, alpha=0.7)
            ax4.set_ylabel('Growth Rate (x)')
            ax4.set_title('Algorithm Scalability (Lower is Better)')
            ax4.grid(True, alpha=0.3)
            
            # Add value labels on bars
            for bar, rate in zip(bars, growth_rates):
                height = bar.get_height()
                ax4.text(bar.get_x() + bar.get_width()/2., height,
                        f'{rate:.2f}x', ha='center', va='bottom')
        
        plt.suptitle('Navigation Routing Algorithm Performance Analysis', 
                    fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.show()
    
    def plot_complexity_analysis(self):
        """Plot theoretical complexity analysis of the algorithms"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Theoretical complexities
        algorithms = ['Dijkstra', 'A*', 'Bellman-Ford']
        time_complexities = ['O(E log V)', 'O(k log V)', 'O(V*E)']
        space_complexities = ['O(V)', 'O(V)', 'O(V)']
        
        # Create synthetic data for visualization
        v_values = np.logspace(1, 4, 100)  # 10 to 10,000 vertices
        e_values = v_values * 3  # Assume average degree of 3
        
        # Time complexity visualization
        ax1.set_xscale('log')
        ax1.set_yscale('log')
        
        # Dijkstra: O(E log V)
        dijkstra_time = e_values * np.log10(v_values)
        ax1.plot(v_values, dijkstra_time, 'b-', linewidth=2, label='Dijkstra: O(E log V)')
        
        # A*: O(k log V) where k << E (assume k = E/10 for typical case)
        astar_time = (e_values / 10) * np.log10(v_values)
        ax1.plot(v_values, astar_time, 'g-', linewidth=2, label='A*: O(k log V), k << E')
        
        # Bellman-Ford: O(V*E)
        bellman_time = v_values * e_values
        ax1.plot(v_values, bellman_time, 'r-', linewidth=2, label='Bellman-Ford: O(V*E)')
        
        ax1.set_xlabel('Number of Vertices (V)')
        ax1.set_ylabel('Operations (log scale)')
        ax1.set_title('Theoretical Time Complexity Comparison')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Space complexity comparison (bar chart)
        space_values = [1, 1, 1]  # All O(V) for space
        colors = ['blue', 'green', 'red']
        bars = ax2.bar(algorithms, space_values, color=colors, alpha=0.7)
        ax2.set_ylabel('Space Complexity (relative to V)')
        ax2.set_title('Space Complexity Comparison')
        ax2.set_ylim(0, 1.2)
        
        # Add complexity labels
        for bar, complexity in zip(bars, space_complexities):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                    complexity, ha='center', va='bottom', fontweight='bold')
        
        plt.suptitle('Algorithm Complexity Analysis', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.show()
    
    def create_interactive_map(self, graph: Graph, path: List[str], 
                             algorithm_name: str = "Routing Algorithm"):
        """Create an interactive map visualization (requires folium)"""
        try:
            import folium
        except ImportError:
            print("Folium not installed. Install with: pip install folium")
            return None
        
        # Calculate center of the map
        lats = [node.y for node in graph.nodes.values()]
        lons = [node.x for node in graph.nodes.values()]
        center_lat = sum(lats) / len(lats)
        center_lon = sum(lons) / len(lons)
        
        # Create map
        m = folium.Map(location=[center_lat, center_lon], zoom_start=12)
        
        # Add all nodes
        for node_id, node in graph.nodes.items():
            color = 'green' if node_id == path[0] else 'blue' if node_id == path[-1] else 'lightblue'
            folium.CircleMarker(
                location=[node.y, node.x],
                radius=8,
                popup=f"{node_id}: {node.name}",
                color='black',
                weight=2,
                fillColor=color,
                fillOpacity=0.8
            ).add_to(m)
        
        # Add all edges
        for from_node_id, edges in graph.edges.items():
            from_node = graph.get_node(from_node_id)
            for edge in edges:
                to_node = graph.get_node(edge.to_node)
                folium.PolyLine(
                    locations=[[from_node.y, from_node.x], [to_node.y, to_node.x]],
                    color='gray',
                    weight=2,
                    opacity=0.5
                ).add_to(m)
        
        # Highlight path
        if len(path) > 1:
            path_coords = []
            for node_id in path:
                node = graph.get_node(node_id)
                path_coords.append([node.y, node.x])
            
            folium.PolyLine(
                locations=path_coords,
                color='red',
                weight=4,
                opacity=0.8,
                popup=f"Path: {' → '.join(path)}"
            ).add_to(m)
        
        # Add title
        title_html = f'''
        <h3 align="center" style="font-size:16px"><b>{algorithm_name}</b></h3>
        <p align="center" style="font-size:12px">Path: {" → ".join(path)}</p>
        '''
        m.get_root().html.add_child(folium.Element(title_html))
        
        return m

def create_sample_city_graph() -> Graph:
    """Create a sample city graph for visualization"""
    graph = Graph()
    
    # Create a more realistic city layout
    nodes = [
        Node("A", -74.0060, 40.7128, "Downtown"),
        Node("B", -74.0040, 40.7148, "City Hall"),
        Node("C", -74.0020, 40.7168, "Financial District"),
        Node("D", -74.0080, 40.7148, "West Side"),
        Node("E", -74.0060, 40.7188, "Midtown"),
        Node("F", -74.0040, 40.7208, "Central Park"),
        Node("G", -74.0100, 40.7168, "Upper West"),
        Node("H", -74.0000, 40.7128, "East Village"),
        Node("I", -74.0020, 40.7108, "Lower East Side"),
        Node("J", -74.0080, 40.7188, "Theater District"),
    ]
    
    for node in nodes:
        graph.add_node(node)
    
    # Add edges with realistic weights
    edges = [
        Edge("A", "B", 2.0, "Broadway"),
        Edge("A", "D", 3.0, "West Street"),
        Edge("A", "H", 2.5, "Houston St"),
        Edge("B", "C", 1.5, "Wall St"),
        Edge("B", "E", 3.0, "Park Ave"),
        Edge("B", "D", 2.0, "Cross Street"),
        Edge("C", "F", 4.0, "Madison Ave"),
        Edge("C", "E", 2.5, "5th Ave"),
        Edge("D", "G", 3.5, "Riverside Dr"),
        Edge("D", "J", 4.0, "Times Square"),
        Edge("E", "F", 2.0, "Central Park South"),
        Edge("E", "J", 1.5, "Broadway"),
        Edge("F", "G", 3.0, "Central Park West"),
        Edge("G", "J", 2.5, "Columbus Circle"),
        Edge("H", "I", 1.0, "Essex St"),
        Edge("I", "A", 2.0, "Delancey St"),
        Edge("I", "B", 3.0, "Grand St"),
        # Add some reverse edges for bidirectional streets
        Edge("B", "A", 2.0, "Broadway"),
        Edge("D", "A", 3.0, "West Street"),
        Edge("H", "A", 2.5, "Houston St"),
        Edge("C", "B", 1.5, "Wall St"),
        Edge("E", "B", 3.0, "Park Ave"),
        Edge("D", "B", 2.0, "Cross Street"),
    ]
    
    for edge in edges:
        graph.add_edge(edge)
    
    return graph

def main():
    """Main visualization demonstration"""
    print("Navigation Routing Visualization Demo")
    print("=" * 40)
    
    visualizer = RoutingVisualizer()
    graph = create_sample_city_graph()
    
    # Import algorithms
    from main import DijkstraAlgorithm, AStarAlgorithm, BellmanFordAlgorithm
    
    algorithms = [
        DijkstraAlgorithm(graph),
        AStarAlgorithm(graph),
        BellmanFordAlgorithm(graph)
    ]
    
    start_node = "A"
    end_node = "F"
    
    print(f"Visualizing routes from {start_node} to {end_node}")
    
    # Show individual algorithm paths
    for algorithm in algorithms:
        visualizer.plot_graph_with_path(graph, algorithm, start_node, end_node)
    
    # Compare all algorithms side by side
    visualizer.compare_algorithm_paths(graph, algorithms, start_node, end_node)
    
    # Show theoretical complexity analysis
    visualizer.plot_complexity_analysis()
    
    print("Visualization complete!")

if __name__ == "__main__":
    main()
