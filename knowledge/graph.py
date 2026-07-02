#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TurboMind AI - Knowledge Graph
==============================
Represents and visualizes knowledge as a graph
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
import time
import json
import random
from pathlib import Path


@dataclass
class GraphNode:
    """Represents a node in the knowledge graph"""
    id: str
    label: str
    type: str = "concept"  # concept, entity, document, silo
    size: int = 10  # Visual size
    color: str = "#2196F3"
    x: float = 0.0  # Position for visualization
    y: float = 0.0
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'label': self.label,
            'type': self.type,
            'size': self.size,
            'color': self.color,
            'x': self.x,
            'y': self.y,
            'properties': self.properties
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GraphNode':
        """Create from dictionary"""
        return cls(
            id=data.get('id', ''),
            label=data.get('label', ''),
            type=data.get('type', 'concept'),
            size=data.get('size', 10),
            color=data.get('color', '#2196F3'),
            x=data.get('x', 0.0),
            y=data.get('y', 0.0),
            properties=data.get('properties', {})
        )


@dataclass
class GraphEdge:
    """Represents an edge between nodes in the knowledge graph"""
    id: str
    source: str  # Source node ID
    target: str  # Target node ID
    label: str = ""
    type: str = "related"  # related, part_of, depends_on, etc.
    weight: float = 1.0
    color: str = "#777777"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'source': self.source,
            'target': self.target,
            'label': self.label,
            'type': self.type,
            'weight': self.weight,
            'color': self.color
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GraphEdge':
        """Create from dictionary"""
        return cls(
            id=data.get('id', ''),
            source=data.get('source', ''),
            target=data.get('target', ''),
            label=data.get('label', ''),
            type=data.get('type', 'related'),
            weight=data.get('weight', 1.0),
            color=data.get('color', '#777777')
        )


@dataclass
class GraphLayout:
    """Represents the layout of the graph for visualization"""
    nodes: Dict[str, Tuple[float, float]]  # node_id -> (x, y)
    edges: List[Dict[str, Any]]  # List of edge positions
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'nodes': {k: {'x': v[0], 'y': v[1]} for k, v in self.nodes.items()},
            'edges': self.edges
        }


class KnowledgeGraph:
    """
    Represents knowledge as a graph structure.
    Nodes represent concepts, entities, documents, or silos.
    Edges represent relationships between nodes.
    """
    
    def __init__(self, storage_path: str = "knowledge_graph"):
        """
        Initialize the knowledge graph.
        
        Args:
            storage_path: Path to store graph data
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Nodes and edges
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: Dict[str, GraphEdge] = {}
        
        # Layout
        self.layout: Optional[GraphLayout] = None
        
        # Stats
        self.stats = {
            'total_nodes': 0,
            'total_edges': 0,
            'last_updated': 0
        }
        
        # Load existing data
        self._load_data()
        
        print("🔗 Knowledge Graph initialized")
    
    def _load_data(self):
        """Load graph data from storage"""
        nodes_file = self.storage_path / "nodes.json"
        edges_file = self.storage_path / "edges.json"
        layout_file = self.storage_path / "layout.json"
        
        if nodes_file.exists():
            with open(nodes_file, 'r', encoding='utf-8') as f:
                nodes_data = json.load(f)
            
            for node_data in nodes_data:
                node = GraphNode.from_dict(node_data)
                self.nodes[node.id] = node
            
            self.stats['total_nodes'] = len(self.nodes)
        
        if edges_file.exists():
            with open(edges_file, 'r', encoding='utf-8') as f:
                edges_data = json.load(f)
            
            for edge_data in edges_data:
                edge = GraphEdge.from_dict(edge_data)
                self.edges[edge.id] = edge
            
            self.stats['total_edges'] = len(self.edges)
        
        if layout_file.exists():
            with open(layout_file, 'r', encoding='utf-8') as f:
                layout_data = json.load(f)
            
            self.layout = GraphLayout(
                nodes={k: (v['x'], v['y']) for k, v in layout_data.get('nodes', {}).items()},
                edges=layout_data.get('edges', [])
            )
        
        print(f"📂 Loaded {self.stats['total_nodes']} nodes, {self.stats['total_edges']} edges")
    
    def save(self):
        """Save graph data to storage"""
        # Save nodes
        nodes_file = self.storage_path / "nodes.json"
        with open(nodes_file, 'w', encoding='utf-8') as f:
            json.dump([node.to_dict() for node in self.nodes.values()], f, indent=2)
        
        # Save edges
        edges_file = self.storage_path / "edges.json"
        with open(edges_file, 'w', encoding='utf-8') as f:
            json.dump([edge.to_dict() for edge in self.edges.values()], f, indent=2)
        
        # Save layout
        if self.layout:
            layout_file = self.storage_path / "layout.json"
            with open(layout_file, 'w', encoding='utf-8') as f:
                json.dump(self.layout.to_dict(), f, indent=2)
        
        print("💾 Knowledge graph saved")
    
    def _generate_id(self) -> str:
        """Generate a unique ID"""
        return f"node_{int(time.time() * 1000)}_{random.randint(0, 10000)}"
    
    # ==================== NODES ====================
    
    def add_node(
        self,
        label: str,
        node_type: str = "concept",
        size: int = 10,
        color: str = "#2196F3",
        x: Optional[float] = None,
        y: Optional[float] = None,
        properties: Optional[Dict[str, Any]] = None
    ) -> GraphNode:
        """
        Add a node to the graph.
        
        Args:
            label: Node label
            node_type: Type of node
            size: Visual size
            color: Node color
            x: X position (optional)
            y: Y position (optional)
            properties: Additional properties
            
        Returns:
            The created GraphNode
        """
        node_id = self._generate_id()
        
        node = GraphNode(
            id=node_id,
            label=label,
            type=node_type,
            size=size,
            color=color,
            x=x or random.uniform(0, 1),
            y=y or random.uniform(0, 1),
            properties=properties or {}
        )
        
        self.nodes[node_id] = node
        self.stats['total_nodes'] += 1
        self.stats['last_updated'] = time.time()
        
        print(f"🆕 Added node: {label}")
        return node
    
    def delete_node(self, node_id: str) -> bool:
        """Delete a node from the graph"""
        if node_id not in self.nodes:
            return False
        
        # Delete all edges connected to this node
        edges_to_delete = [
            edge_id for edge_id, edge in self.edges.items()
            if edge.source == node_id or edge.target == node_id
        ]
        
        for edge_id in edges_to_delete:
            del self.edges[edge_id]
            self.stats['total_edges'] -= 1
        
        # Delete the node
        del self.nodes[node_id]
        self.stats['total_nodes'] -= 1
        self.stats['last_updated'] = time.time()
        
        print(f"🗑️  Deleted node: {node_id}")
        return True
    
    def update_node(self, node_id: str, **kwargs) -> Optional[GraphNode]:
        """Update a node"""
        if node_id not in self.nodes:
            return None
        
        node = self.nodes[node_id]
        
        for key, value in kwargs.items():
            if hasattr(node, key):
                setattr(node, key, value)
        
        self.stats['last_updated'] = time.time()
        
        print(f"🔄 Updated node: {node.label}")
        return node
    
    def get_node(self, node_id: str) -> Optional[GraphNode]:
        """Get a node by ID"""
        return self.nodes.get(node_id)
    
    # ==================== EDGES ====================
    
    def add_edge(
        self,
        source: str,
        target: str,
        edge_type: str = "related",
        label: str = "",
        weight: float = 1.0,
        color: str = "#777777"
    ) -> Optional[GraphEdge]:
        """
        Add an edge between two nodes.
        
        Args:
            source: Source node ID
            target: Target node ID
            edge_type: Type of relationship
            label: Edge label
            weight: Edge weight
            color: Edge color
            
        Returns:
            The created GraphEdge or None if nodes don't exist
        """
        if source not in self.nodes or target not in self.nodes:
            print(f"❌ Edge nodes not found: {source}, {target}")
            return None
        
        edge_id = self._generate_id()
        
        edge = GraphEdge(
            id=edge_id,
            source=source,
            target=target,
            label=label,
            type=edge_type,
            weight=weight,
            color=color
        )
        
        self.edges[edge_id] = edge
        self.stats['total_edges'] += 1
        self.stats['last_updated'] = time.time()
        
        print(f"🔗 Added edge: {source} -> {target}")
        return edge
    
    def delete_edge(self, edge_id: str) -> bool:
        """Delete an edge from the graph"""
        if edge_id not in self.edges:
            return False
        
        del self.edges[edge_id]
        self.stats['total_edges'] -= 1
        self.stats['last_updated'] = time.time()
        
        print(f"🗑️  Deleted edge: {edge_id}")
        return True
    
    def get_edge(self, edge_id: str) -> Optional[GraphEdge]:
        """Get an edge by ID"""
        return self.edges.get(edge_id)
    
    # ==================== GRAPH OPERATIONS ====================
    
    def get_neighbors(self, node_id: str) -> Dict[str, List[GraphEdge]]:
        """
        Get all neighbors of a node.
        
        Args:
            node_id: Node ID
            
        Returns:
            Dictionary with 'incoming' and 'outgoing' edges
        """
        if node_id not in self.nodes:
            return {'incoming': [], 'outgoing': []}
        
        incoming = [
            edge for edge in self.edges.values()
            if edge.target == node_id
        ]
        
        outgoing = [
            edge for edge in self.edges.values()
            if edge.source == node_id
        ]
        
        return {'incoming': incoming, 'outgoing': outgoing}
    
    def find_path(self, start: str, end: str, max_depth: int = 5) -> Optional[List[str]]:
        """
        Find a path between two nodes using BFS.
        
        Args:
            start: Start node ID
            end: End node ID
            max_depth: Maximum search depth
            
        Returns:
            List of node IDs in the path or None
        """
        if start not in self.nodes or end not in self.nodes:
            return None
        
        if start == end:
            return [start]
        
        # BFS
        queue = [[start]]
        visited = {start}
        
        while queue:
            path = queue.pop(0)
            current = path[-1]
            
            if len(path) > max_depth:
                continue
            
            # Get neighbors
            neighbors = self.get_neighbors(current)
            all_neighbors = [
                edge.source for edge in neighbors['incoming']
            ] + [
                edge.target for edge in neighbors['outgoing']
            ]
            
            for neighbor in all_neighbors:
                if neighbor == end:
                    return path + [neighbor]
                
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(path + [neighbor])
        
        return None
    
    def get_connected_components(self) -> List[List[str]]:
        """
        Get all connected components in the graph.
        
        Returns:
            List of lists of node IDs
        """
        components = []
        visited = set()
        
        for node_id in self.nodes.keys():
            if node_id not in visited:
                # BFS to find connected component
                component = []
                queue = [node_id]
                
                while queue:
                    current = queue.pop(0)
                    if current in visited:
                        continue
                    
                    visited.add(current)
                    component.append(current)
                    
                    # Add neighbors
                    neighbors = self.get_neighbors(current)
                    all_neighbors = [
                        edge.source for edge in neighbors['incoming']
                    ] + [
                        edge.target for edge in neighbors['outgoing']
                    ]
                    
                    for neighbor in all_neighbors:
                        if neighbor not in visited:
                            queue.append(neighbor)
                
                components.append(component)
        
        return components
    
    # ==================== LAYOUT ====================
    
    def generate_layout(self, algorithm: str = "force_directed") -> GraphLayout:
        """
        Generate a layout for the graph.
        
        Args:
            algorithm: Layout algorithm ('force_directed', 'circular', 'random')
            
        Returns:
            GraphLayout object
        """
        if algorithm == "force_directed":
            return self._force_directed_layout()
        elif algorithm == "circular":
            return self._circular_layout()
        else:  # random
            return self._random_layout()
    
    def _force_directed_layout(self, iterations: int = 100) -> GraphLayout:
        """Force-directed layout (simplified)"""
        # Initialize positions randomly
        positions = {node_id: (random.uniform(0, 1), random.uniform(0, 1))
                    for node_id in self.nodes.keys()}
        
        # Simple force-directed algorithm
        for _ in range(iterations):
            for node_id in self.nodes.keys():
                x, y = positions[node_id]
                
                # Repulsive forces from all nodes
                fx, fy = 0, 0
                for other_id in self.nodes.keys():
                    if node_id == other_id:
                        continue
                    
                    ox, oy = positions[other_id]
                    dx = x - ox
                    dy = y - oy
                    distance = max(0.01, (dx**2 + dy**2)**0.5)
                    
                    # Repulsion
                    fx += dx / distance
                    fy += dy / distance
                
                # Attractive forces from connected nodes
                neighbors = self.get_neighbors(node_id)
                all_neighbors = [
                    edge.source for edge in neighbors['incoming']
                ] + [
                    edge.target for edge in neighbors['outgoing']
                ]
                
                for neighbor_id in all_neighbors:
                    if neighbor_id not in positions:
                        continue
                    
                    nx, ny = positions[neighbor_id]
                    dx = x - nx
                    dy = y - ny
                    distance = max(0.01, (dx**2 + dy**2)**0.5)
                    
                    # Attraction
                    fx -= dx * distance
                    fy -= dy * distance
                
                # Update position
                x += fx * 0.1
                y += fy * 0.1
                
                # Keep within bounds
                x = max(0, min(1, x))
                y = max(0, min(1, y))
                
                positions[node_id] = (x, y)
        
        # Create layout
        self.layout = GraphLayout(
            nodes=positions,
            edges=[]
        )
        
        return self.layout
    
    def _circular_layout(self) -> GraphLayout:
        """Circular layout"""
        n = len(self.nodes)
        positions = {}
        
        for i, node_id in enumerate(self.nodes.keys()):
            angle = (i / n) * 2 * 3.14159
            positions[node_id] = (
                0.5 + 0.4 * (1 + 0.1 * i) * (1 + 0.1 * (i % 3)) * (0.5 + 0.5 * (i % 2)) * (0.9 + 0.2 * random.random()) * 0.8 * (0.5 + 0.5 * (i % 2)) * 
                (0.8 + 0.4 * (i % 2)) * math.cos(angle) if 'math' in dir() else 0.5 + 0.4 * math.cos(angle),
                0.5 + 0.4 * (1 + 0.1 * i) * (1 + 0.1 * (i % 3)) * (0.5 + 0.5 * (i % 2)) * (0.9 + 0.2 * random.random()) * 0.8 * (0.5 + 0.5 * (i % 2)) * 
                (0.8 + 0.4 * (i % 2)) * math.sin(angle) if 'math' in dir() else 0.5 + 0.4 * math.sin(angle)
            )
        
        # Simplified circular layout
        import math
        for i, node_id in enumerate(self.nodes.keys()):
            angle = (i / n) * 2 * math.pi
            radius = 0.4
            positions[node_id] = (
                0.5 + radius * math.cos(angle),
                0.5 + radius * math.sin(angle)
            )
        
        self.layout = GraphLayout(
            nodes=positions,
            edges=[]
        )
        
        return self.layout
    
    def _random_layout(self) -> GraphLayout:
        """Random layout"""
        positions = {node_id: (random.uniform(0, 1), random.uniform(0, 1))
                    for node_id in self.nodes.keys()}
        
        self.layout = GraphLayout(
            nodes=positions,
            edges=[]
        )
        
        return self.layout
    
    # ==================== VISUALIZATION ====================
    
    def to_visjs_format(self) -> Dict[str, Any]:
        """
        Convert graph to Vis.js format for visualization.
        
        Returns:
            Dictionary with nodes and edges in Vis.js format
        """
        nodes = []
        for node in self.nodes.values():
            nodes.append({
                'id': node.id,
                'label': node.label,
                'title': f"{node.type}\nSize: {node.size}",
                'value': node.size,
                'color': node.color,
                'x': node.x,
                'y': node.y
            })
        
        edges = []
        for edge in self.edges.values():
            edges.append({
                'from': edge.source,
                'to': edge.target,
                'label': edge.label,
                'title': edge.type,
                'width': edge.weight,
                'color': edge.color
            })
        
        return {'nodes': nodes, 'edges': edges}
    
    def to_d3_format(self) -> Dict[str, Any]:
        """
        Convert graph to D3.js format for visualization.
        
        Returns:
            Dictionary with nodes and edges in D3.js format
        """
        nodes = []
        for node in self.nodes.values():
            nodes.append({
                'id': node.id,
                'name': node.label,
                'group': 1,
                'size': node.size
            })
        
        links = []
        for edge in self.edges.values():
            links.append({
                'source': edge.source,
                'target': edge.target,
                'value': edge.weight
            })
        
        return {'nodes': nodes, 'links': links}
    
    def to_cytoscape_format(self) -> Dict[str, Any]:
        """
        Convert graph to Cytoscape.js format for visualization.
        
        Returns:
            Dictionary with nodes and edges in Cytoscape.js format
        """
        elements = []
        
        for node in self.nodes.values():
            elements.append({
                'data': {
                    'id': node.id,
                    'label': node.label,
                    'type': node.type,
                    'size': node.size,
                    'color': node.color
                },
                'position': {
                    'x': node.x * 1000,
                    'y': node.y * 1000
                }
            })
        
        for edge in self.edges.values():
            elements.append({
                'data': {
                    'id': edge.id,
                    'source': edge.source,
                    'target': edge.target,
                    'label': edge.label,
                    'type': edge.type,
                    'weight': edge.weight
                }
            })
        
        return {'elements': elements}
    
    # ==================== STATS & INFO ====================
    
    def get_stats(self) -> Dict[str, Any]:
        """Get graph statistics"""
        # Count by type
        type_counts = {}
        for node in self.nodes.values():
            type_counts[node.type] = type_counts.get(node.type, 0) + 1
        
        # Count by edge type
        edge_type_counts = {}
        for edge in self.edges.values():
            edge_type_counts[edge.type] = edge_type_counts.get(edge.type, 0) + 1
        
        return {
            **self.stats,
            'node_types': type_counts,
            'edge_types': edge_type_counts,
            'average_degree': self._calculate_average_degree()
        }
    
    def _calculate_average_degree(self) -> float:
        """Calculate average degree of the graph"""
        if not self.nodes:
            return 0.0
        
        total_degree = 0
        for node_id in self.nodes.keys():
            neighbors = self.get_neighbors(node_id)
            degree = len(neighbors['incoming']) + len(neighbors['outgoing'])
            total_degree += degree
        
        return total_degree / len(self.nodes)
    
    def get_all_nodes(self) -> List[GraphNode]:
        """Get all nodes"""
        return list(self.nodes.values())
    
    def get_all_edges(self) -> List[GraphEdge]:
        """Get all edges"""
        return list(self.edges.values())
    
    def clear(self):
        """Clear the entire graph"""
        self.nodes.clear()
        self.edges.clear()
        self.layout = None
        self.stats = {
            'total_nodes': 0,
            'total_edges': 0,
            'last_updated': 0
        }
        
        print("🧹 Knowledge graph cleared")
    
    def export_graph(self, output_path: str, format: str = "json") -> bool:
        """Export graph to a file"""
        try:
            if format == "json":
                data = {
                    'nodes': [node.to_dict() for node in self.nodes.values()],
                    'edges': [edge.to_dict() for edge in self.edges.values()]
                }
                output_file = Path(output_path)
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
            elif format == "visjs":
                data = self.to_visjs_format()
                output_file = Path(output_path)
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
            elif format == "d3":
                data = self.to_d3_format()
                output_file = Path(output_path)
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
            else:
                return False
            
            print(f"📤 Graph exported to {output_path}")
            return True
        except Exception as e:
            print(f"❌ Export failed: {e}")
            return False
    
    def import_graph(self, input_path: str, format: str = "json") -> bool:
        """Import graph from a file"""
        try:
            input_file = Path(input_path)
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if format == "json":
                for node_data in data.get('nodes', []):
                    node = GraphNode.from_dict(node_data)
                    self.nodes[node.id] = node
                
                for edge_data in data.get('edges', []):
                    edge = GraphEdge.from_dict(edge_data)
                    self.edges[edge.id] = edge
            
            self.stats['total_nodes'] = len(self.nodes)
            self.stats['total_edges'] = len(self.edges)
            self.stats['last_updated'] = time.time()
            
            print(f"📥 Graph imported from {input_path}")
            return True
        except Exception as e:
            print(f"❌ Import failed: {e}")
            return False
