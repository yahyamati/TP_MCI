from enum import Enum
from typing import List, Dict, Optional, Tuple, Set
import tkinter as tk
from tkinter import ttk, messagebox



class NodeState(Enum):
    KNOWN = "known"
    UNKNOWN = "unknown"

class Direction(Enum):
    FORWARD = "->"
    BACKWARD = "<-"

class RelationType(Enum):
    CONVERGENTE = "convergente"  # X -> Z <- Y
    SERIES = "series"            # X -> Z -> Y
    DIVERGENTE = "divergente"    # Z -> X and Z -> Y

class Node:
    def __init__(self, name: str, state: NodeState = NodeState.UNKNOWN):
        self.name = name
        self.state = state

    def __str__(self):
        return f"{self.name} ({self.state.value})"

class Relation:
    def __init__(self, source: Node, target: Node, direction: Direction):
        self.source = source
        self.target = target
        self.direction = direction

    def __str__(self):
        return f"{self.source} {self.direction.value} {self.target}"

class BayesianNetwork:
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.relations: List[Relation] = []
        self.adjacency: Dict[str, List[Tuple[str, Direction]]] = {}

    def add_node(self, name: str, state: NodeState) -> Node:
        if name not in self.nodes:
            self.nodes[name] = Node(name, state)
            self.adjacency[name] = []
        return self.nodes[name]

    def add_relation(self, source: str, target: str, direction: Direction,
                    source_state: NodeState = NodeState.UNKNOWN, 
                    target_state: NodeState = NodeState.UNKNOWN):
        source_node = self.add_node(source, source_state)
        target_node = self.add_node(target, target_state)
        rel = Relation(source_node, target_node, direction)
        self.relations.append(rel)
        
        if direction == Direction.FORWARD:
            self.adjacency[source].append((target, direction))
        else:
            self.adjacency[target].append((source, direction))

    def get_all_paths(self, start: str, max_length: int = 100) -> List[List[str]]:
         
        paths = []
        
        def dfs(node: str, path: List[str], length: int):
            if length > max_length:
                return
                
            path.append(node)
            
            if len(path) > 1:
                paths.append(path.copy())
                
            for neighbor, _ in self.adjacency.get(node, []):
                if neighbor not in path:
                    dfs(neighbor, path, length + 1)
                elif neighbor == path[0] and len(path) >= 3:  # Detect cycles
                    cycle = path + [neighbor]
                    paths.append(cycle)
                    
            path.pop()
        
        dfs(start, [], 0)
        return paths

    def get_all_possible_triples(self) -> List[Tuple[str, str, str]]:
        """Generate all possible triples in the network"""
        triples = set()
        nodes = list(self.nodes.keys())
        
        # Check all possible combinations of 3 nodes
        for x in nodes:
            for z in nodes:
                if x == z:
                    continue
                for y in nodes:
                    if y == z or y == x:
                        continue
                    
                    # Check if x-z-y forms a valid triple
                    xz = any((r.source.name == x and r.target.name == z) or 
                            (r.source.name == z and r.target.name == x) 
                            for r in self.relations)
                    zy = any((r.source.name == z and r.target.name == y) or 
                            (r.source.name == y and r.target.name == z) 
                            for r in self.relations)
                    
                    if xz and zy:
                        triples.add((x, z, y))
        
        return list(triples)

    def determine_relation_type(self, x: str, z: str, y: str) -> Optional[RelationType]:
        """Determine the relationship pattern between three nodes"""
        x_to_z = any(r.source.name == x and r.target.name == z for r in self.relations)
        z_to_x = any(r.source.name == z and r.target.name == x for r in self.relations)
        z_to_y = any(r.source.name == z and r.target.name == y for r in self.relations)
        y_to_z = any(r.source.name == y and r.target.name == z for r in self.relations)

        if x_to_z and z_to_y:
            return RelationType.SERIES
        elif z_to_x and z_to_y:
            return RelationType.DIVERGENTE
        elif x_to_z and y_to_z:
            return RelationType.CONVERGENTE
        return None

    def check_triple_flow(self, x: str, z: str, y: str) -> Tuple[bool, str]:
        """Check if information can flow through a triple"""
        z_node = self.nodes[z]
        rel_type = self.determine_relation_type(x, z, y)

        if rel_type == RelationType.SERIES: 
            if z_node.state == NodeState.UNKNOWN:
                return True, f"Series: Flow allowed through {z} (unknown)"
            return False, f"Series: Blocked at {z} (known)"

        elif rel_type == RelationType.DIVERGENTE:
            if z_node.state == NodeState.UNKNOWN:
                return True, f"Divergent: Flow allowed from {x} to {y}   via {z} (unknown)"
            return False, f"Divergent: Blocked at {z} (known)"

        elif rel_type == RelationType.CONVERGENTE:
            if z_node.state == NodeState.KNOWN:
                return True, f"Convergent: Flow allowed between {x} and {y} via {z} (known)"
            return False, f"Convergent: Blocked at {z} (unknown)"

        return False, "Unknown relationship pattern"

    def analyze_triple_connections(self) -> str:
    
        all_triples = self.get_all_possible_triples()
        if not all_triples:
            return "No triples found in network"

        results = []
        results.append("=== Triple Connection Analysis ===")
        
        # Test each triple with every other triple
        for i in range(len(all_triples)):
            for j in range(len(all_triples)):
                if i != j:
                    t1 = all_triples[i]
                    t2 = all_triples[j]
                    
                    # Check if last node of first triple matches first node of second
                    if t1[2] == t2[0]:
                        combined = (t1[0], t1[1], t1[2], t2[1], t2[2])
                        
                        # Verify directionality - first node should have no incoming edges (except possibly from second node)
                        is_valid_direction = True
                        for rel in self.relations:
                            if rel.target.name == t1[0] and rel.source.name != t1[1]:
                                is_valid_direction = False
                                break
                        
                        unique_nodes = len(set(combined))
                        
                        if not is_valid_direction:
                            # Try reversing the path
                            reversed_path = combined[::-1]
                            is_reversed_valid = True
                            
                            # Check if last node in reversed path is valid start
                            for rel in self.relations:
                                if rel.target.name == reversed_path[0] and rel.source.name != reversed_path[1]:
                                    is_reversed_valid = False
                                    break
                            
                            if is_reversed_valid:
                                combined = reversed_path
                                is_valid_direction = True
                        
                        if is_valid_direction:
                            if unique_nodes == len(combined):
                                results.append(f"Valid connection: {t1} -> {t2}")
                                results.append(f"  Path: {' -> '.join(combined)}")
                            elif combined[0] == combined[-1] and unique_nodes == len(combined)-1:
                                results.append(f"Loop detected: {t1} -> {t2}")
                                results.append(f"  Cycle: {' -> '.join(combined)}")
                            else:
                                results.append(f"Connection with duplicates: {t1} -> {t2}")
                                results.append(f"  Invalid path: {' -> '.join(combined)}")
                        else:
                            results.append(f"Invalid direction: {t1} -> {t2}")
                            results.append(f"  Path cannot start at {combined[0]}")

        # Also show all individual paths
        results.append("\n=== All Paths in Network ===")
        for node in self.nodes:
            paths = self.get_all_paths(node)
            if paths:
                results.append(f"\nPaths from {node}:")
                for path in paths:
                    results.append(" -> ".join(path))

        return "\n".join(results)
# [GUI code remains the same as previous implementation]
    
    
class NetworkGUI:
    def __init__(self, root):
        self.network = BayesianNetwork()
        self.root = root
        self.root.title("Bayesian Network Analyzer")
        self.root.geometry("1000x800")
        
        # Configure grid weights
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        
        # Create main frames
        self.input_frame = ttk.Frame(root, padding="10")
        self.input_frame.grid(row=0, column=0, sticky="ew")
        
        self.output_frame = ttk.Frame(root)
        self.output_frame.grid(row=1, column=0, sticky="nsew")
        
        # Input widgets
        self.create_input_widgets()
        
        # Output widgets
        self.create_output_widgets()
        
        # Analysis buttons
        self.create_analysis_buttons()
    
    def create_input_widgets(self):
        """Create all input widgets for relation creation"""
        # Node inputs
        ttk.Label(self.input_frame, text="Node 1:").grid(row=0, column=0, padx=5, pady=5)
        self.node1_entry = ttk.Entry(self.input_frame)
        self.node1_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(self.input_frame, text="Node 2:").grid(row=0, column=2, padx=5, pady=5)
        self.node2_entry = ttk.Entry(self.input_frame)
        self.node2_entry.grid(row=0, column=3, padx=5, pady=5)
        
        # Direction selector
        ttk.Label(self.input_frame, text="Direction:").grid(row=0, column=4, padx=5, pady=5)
        self.direction_combo = ttk.Combobox(self.input_frame, values=["->", "<-"], state="readonly")
        self.direction_combo.set("->")
        self.direction_combo.grid(row=0, column=5, padx=5, pady=5)
        
        # State selectors
        ttk.Label(self.input_frame, text="Node 1 State:").grid(row=1, column=0, padx=5, pady=5)
        self.node1_state = ttk.Combobox(self.input_frame, values=["known", "unknown"], state="readonly")
        self.node1_state.set("unknown")
        self.node1_state.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(self.input_frame, text="Node 2 State:").grid(row=1, column=2, padx=5, pady=5)
        self.node2_state = ttk.Combobox(self.input_frame, values=["known", "unknown"], state="readonly")
        self.node2_state.set("unknown")
        self.node2_state.grid(row=1, column=3, padx=5, pady=5)
        
        # Add relation button
        ttk.Button(self.input_frame, text="Add Relation", command=self.add_relation).grid(
            row=1, column=4, columnspan=2, padx=5, pady=5)
    
    def create_output_widgets(self):
        """Create output text widget with scrollbar"""
        self.output_text = tk.Text(self.output_frame, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(self.output_frame, orient="vertical", command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=scrollbar.set)
        
        self.output_text.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        self.output_frame.grid_columnconfigure(0, weight=1)
        self.output_frame.grid_rowconfigure(0, weight=1)
    
    def create_analysis_buttons(self):
        """Create buttons for different analysis functions"""
        button_frame = ttk.Frame(self.output_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=10, sticky="ew")
        
        ttk.Button(button_frame, text="Show All Paths", 
                  command=self.show_all_paths).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Analyze Triples", 
                  command=self.analyze_triples).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Check Triple Connections", 
                  command=self.check_triple_connections).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Clear Output", 
                  command=self.clear_output).pack(side="right", padx=5)
    
    def add_relation(self):
        """Add a new relation to the network"""
        node1 = self.node1_entry.get().strip()
        node2 = self.node2_entry.get().strip()
        
        if not node1 or not node2:
            messagebox.showerror("Error", "Both nodes must be specified")
            return
        
        direction = Direction.FORWARD if self.direction_combo.get() == "->" else Direction.BACKWARD
        node1_state = NodeState[self.node1_state.get().upper()]
        node2_state = NodeState[self.node2_state.get().upper()]
        
        # Flip nodes if direction is backward
        if direction == Direction.BACKWARD:
            node1, node2 = node2, node1
            node1_state, node2_state = node2_state, node1_state
        
        self.network.add_relation(node1, node2, direction, node1_state, node2_state)
        
        # Display the added relation
        display_dir = self.direction_combo.get()
        self.output_text.insert(tk.END, 
            f"Added relation: {self.node1_entry.get()} {display_dir} {self.node2_entry.get()}\n"
            f"  - {node1} state: {node1_state.value}\n"
            f"  - {node2} state: {node2_state.value}\n\n")
        
        # Clear entries
        self.node1_entry.delete(0, tk.END)
        self.node2_entry.delete(0, tk.END)
    
    def show_all_paths(self):
        """Display all paths in the network"""
        self.output_text.insert(tk.END, "\n=== All Paths in Network ===\n")
        
        for node in self.network.nodes:
            paths = self.network.get_all_paths(node)
            if paths:
                self.output_text.insert(tk.END, f"\nPaths from {node}:\n")
                for path in paths:
                    self.output_text.insert(tk.END, " -> ".join(path) + "\n")
        
        self.output_text.insert(tk.END, "\n")
        self.output_text.see(tk.END)
    
    def analyze_triples(self):
        """Analyze all triples in the network"""
        triples = self.network.get_all_possible_triples()
        
        self.output_text.insert(tk.END, "\n=== Triple Analysis ===\n")
        
        if not triples:
            self.output_text.insert(tk.END, "No triples found in network\n")
            return
        
        for triple in triples:
            x, z, y = triple
            rel_type = self.network.determine_relation_type(x, z, y)
            allowed, reason = self.network.check_triple_flow(x, z, y)
            
            self.output_text.insert(tk.END, 
                f"\nTriple: {x} -> {z} -> {y}\n"
                f"Type: {rel_type.value if rel_type else 'unknown'}\n"
                f"Flow: {'Allowed' if allowed else 'Blocked'}\n"
                f"Reason: {reason}\n")
        
        self.output_text.see(tk.END)
    
    def check_triple_connections(self):
        """Check connections between all triples with strict start node validation"""
        self.output_text.insert(tk.END, "\n=== Triple Connection Analysis ===\n")
        
        all_triples = self.network.get_all_possible_triples()
        if not all_triples:
            self.output_text.insert(tk.END, "No triples found in network\n")
            return
        
        # Get the first node in the network (assuming it's 'a' in this case)
        first_node = next(iter(self.network.nodes)) if self.network.nodes else None
        
        for i in range(len(all_triples)):
            for j in range(len(all_triples)):
                if i != j:
                    t1 = all_triples[i]
                    t2 = all_triples[j]
                    
                    if t1[2] == t2[0]:
                        combined = [t1[0], t1[1], t1[2], t2[1], t2[2]]
                        path_str = " -> ".join(combined)
                        
                        # Strict validation: path must start with first_node
                        if first_node and combined[0] != first_node:
                            self.output_text.insert(tk.END, 
                                f"Invalid start: {t1} -> {t2}\n"
                                f"  Path must start with {first_node}\n"
                                f"  Path: {path_str}\n\n")
                            continue
                        
                        # Check for duplicates or valid paths
                        unique_nodes = len(set(combined))
                        
                        if unique_nodes == len(combined):
                            self.output_text.insert(tk.END, 
                                f"Valid connection: {t1} -> {t2}\n"
                                f"  Path: {path_str}\n\n")
                        elif combined[0] == combined[-1] and unique_nodes == len(combined)-1:
                            self.output_text.insert(tk.END, 
                                f"Loop detected: {t1} -> {t2}\n"
                                f"  Cycle: {path_str}\n\n")
                        else:
                            self.output_text.insert(tk.END, 
                                f"Connection with duplicates: {t1} -> {t2}\n"
                                f"  Path: {path_str}\n\n")
        
        self.output_text.see(tk.END)
    
    def clear_output(self):
        """Clear the output text widget"""
        self.output_text.delete(1.0, tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkGUI(root)
    root.mainloop()