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
                    source_state: NodeState, target_state: NodeState):
        source_node = self.add_node(source, source_state)
        target_node = self.add_node(target, target_state)
        rel = Relation(source_node, target_node, direction)
        self.relations.append(rel)
        
        # Build adjacency list (track both directions with their actual direction)
        if direction == Direction.FORWARD:
            self.adjacency[source].append((target, direction))
        else:
            self.adjacency[target].append((source, direction))

    def get_all_paths(self, start: str) -> List[List[str]]:
        """Find all possible paths starting from given node, following both directions"""
        paths = []
        visited = set()
        
        def dfs(node: str, current_path: List[str]):
            visited.add(node)
            current_path.append(node)
            
            # Get all connections (both directions)
            connections = self.adjacency.get(node, [])
            
            if not connections:
                paths.append(current_path.copy())
            else:
                for neighbor, direction in connections:
                    if neighbor not in visited:
                        dfs(neighbor, current_path.copy())
            
            visited.remove(node)
            current_path.pop()
        
        dfs(start, [])
        return paths

    def get_non_overlapping_triples(self, path: List[str]) -> List[Tuple[str, str, str]]:
        """Generate non-overlapping triples (a,b,c), (c,d,e)"""
        triples = []
        i = 0
        while i + 2 < len(path):
            triples.append((path[i], path[i+1], path[i+2]))
            i += 2  # Move to next non-overlapping triple
        return triples

    def determine_relation_type(self, x: str, z: str, y: str) -> Optional[RelationType]:
        """Determine the relationship pattern between three nodes"""
        # Check all possible relation combinations
        x_to_z = any(r.source.name == x and r.target.name == z for r in self.relations)
        z_to_x = any(r.source.name == z and r.target.name == x for r in self.relations)
        z_to_y = any(r.source.name == z and r.target.name == y for r in self.relations)
        y_to_z = any(r.source.name == y and r.target.name == z for r in self.relations)

        if x_to_z and z_to_y:
            return RelationType.SERIES  # X -> Z -> Y
        elif z_to_x and z_to_y:
            return RelationType.DIVERGENTE  # Z -> X and Z -> Y
        elif x_to_z and y_to_z:
            return RelationType.CONVERGENTE  # X -> Z <- Y
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
                return True, f"Divergent: Flow allowed from {x} to {y} via {z} (unknown)"
            return False, f"Divergent: Blocked at {z} (known)"

        elif rel_type == RelationType.CONVERGENTE:
            if z_node.state == NodeState.KNOWN:
                return True, f"Convergent: Flow allowed between {x} and {y} via {z} (known)"
            return False, f"Convergent: Blocked at {z} (unknown)"

        return False, "Unknown relationship pattern"

    def compute_all_paths(self) -> str:
        if not self.nodes:
            return "No nodes in network"

        # Step 1: Find ALL possible triples in the network
        all_triples = set()
        nodes = list(self.nodes.keys())
        
        # Check all possible node combinations
        for z in nodes:
            # Get all connections to/from z
            connected = [rel for rel in self.relations 
                        if rel.source.name == z or rel.target.name == z]
            
            # Find divergent (z is parent)
            children = [rel.target.name for rel in connected if rel.source.name == z]
            if len(children) >= 2:
                for i in range(len(children)):
                    for j in range(i+1, len(children)):
                        all_triples.add((children[i], z, children[j]))
            
            # Find convergent (z is child)
            parents = [rel.source.name for rel in connected if rel.target.name == z]
            if len(parents) >= 2:
                for i in range(len(parents)):
                    for j in range(i+1, len(parents)):
                        all_triples.add((parents[i], z, parents[j]))
            
            # Find series connections
            for x in parents:
                for y in children:
                    all_triples.add((x, z, y))

        # Step 2: Analyze each triple
        results = []
        for x, z, y in all_triples:
            allowed, justification = self.check_triple_flow(x, z, y)
            rel_type = self.determine_relation_type(x, z, y)
            
            results.append({
                'triple': f"{x}-{z}-{y}",
                'type': rel_type.name if rel_type else "unknown",
                'flow': "Allowed" if allowed else "Blocked",
                'reason': justification
            })

        # Step 3: Format output
        output = ["Network Analysis:"]
        for result in results:
            output.append(f"\nTriple: {result['triple']}")
            output.append(f"Type: {result['type']}")
            output.append(f"Status: {result['flow']}")
            output.append(f"Reason: {result['reason']}")
    
        return "\n".join(output) if results else "No triples found"

# [GUI code remains the same as previous implementation]
    
    

class NetworkGUI:
    def __init__(self, root):
        self.network = BayesianNetwork()
        self.root = root
        self.root.title("Bayesian Network Path Analyzer")
        self.root.geometry("900x700")

        # Input frame
        input_frame = ttk.Frame(root, padding="10")
        input_frame.pack(fill="x")

        ttk.Label(input_frame, text="Source Node:").grid(row=0, column=0, padx=5, pady=5)
        self.source_entry = ttk.Entry(input_frame)
        self.source_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Target Node:").grid(row=1, column=0, padx=5, pady=5)
        self.target_entry = ttk.Entry(input_frame)
        self.target_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Direction:").grid(row=2, column=0, padx=5, pady=5)
        self.direction = ttk.Combobox(input_frame, values=["->", "<-"], state="readonly")
        self.direction.set("->")
        self.direction.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Source State:").grid(row=3, column=0, padx=5, pady=5)
        self.source_state = ttk.Combobox(input_frame, values=["known", "unknown"], state="readonly")
        self.source_state.set("unknown")
        self.source_state.grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Target State:").grid(row=4, column=0, padx=5, pady=5)
        self.target_state = ttk.Combobox(input_frame, values=["known", "unknown"], state="readonly")
        self.target_state.set("unknown")
        self.target_state.grid(row=4, column=1, padx=5, pady=5)

        ttk.Button(input_frame, text="Add Relation", command=self.add_relation).grid(
            row=5, column=0, columnspan=2, pady=10)

        # Output frame
        output_frame = ttk.Frame(root, padding="10")
        output_frame.pack(fill="both", expand=True)

        self.output_text = tk.Text(output_frame, height=25, width=100)
        scrollbar = ttk.Scrollbar(output_frame, orient="vertical", command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=scrollbar.set)
        self.output_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        ttk.Button(output_frame, text="Compute All Paths", command=self.compute_paths).pack(pady=10)

    def add_relation(self):
        source = self.source_entry.get().strip()
        target = self.target_entry.get().strip()
        
        if not source or not target:
            messagebox.showerror("Error", "Both source and target must be specified")
            return

        direction = Direction.FORWARD if self.direction.get() == "->" else Direction.BACKWARD
        source_state = NodeState[self.source_state.get().upper()]
        target_state = NodeState[self.target_state.get().upper()]

        # Flip source/target if direction is backward
        if direction == Direction.BACKWARD:
            source, target = target, source
            source_state, target_state = target_state, source_state

        self.network.add_relation(source, target, direction, source_state, target_state)
        self.output_text.insert(tk.END, 
            f"Added relation: {self.source_entry.get()} {self.direction.get()} {self.target_entry.get()}\n"
            f"  - Source state: {source_state.value}\n"
            f"  - Target state: {target_state.value}\n\n")
        
        # Clear entries
        self.source_entry.delete(0, tk.END)
        self.target_entry.delete(0, tk.END)

    def compute_paths(self):
        result = self.network.compute_all_paths()
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, result + "\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkGUI(root)
    root.mainloop()