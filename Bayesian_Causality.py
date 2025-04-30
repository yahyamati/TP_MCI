from enum import Enum
from typing import List, Dict,Tuple
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
    SERIES = "en_serie"          # X -> Z -> Y
    DIVERGENTE = "divergente"    # Z -> X, Z -> Y

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

    def add_node(self, name: str, state: NodeState) -> Node:
        if name not in self.nodes:
            self.nodes[name] = Node(name, state)
        return self.nodes[name]

    def add_relation(self, source_name: str, target_name: str, direction: Direction, source_state: NodeState, target_state: NodeState):
        source = self.add_node(source_name, source_state)
        target = self.add_node(target_name, target_state)
        self.relations.append(Relation(source, target, direction))

    def infer_relation_type(self, node: Node) -> RelationType:
        incoming = [r for r in self.relations if r.target == node]
        outgoing = [r for r in self.relations if r.source == node]
        if len(incoming) >= 2 and len(outgoing) == 0:
            return RelationType.CONVERGENTE
        elif len(incoming) == 1 and len(outgoing) == 1:
            return RelationType.SERIES
        elif len(incoming) == 0 and len(outgoing) >= 2:
            return RelationType.DIVERGENTE
        return None
    
    
    def has_cycle(self) -> List[str]:
        """Vérifie si le graphe contient un cycle et retourne le cycle sous forme de liste de nœuds."""
        visited = set()
        rec_stack = set()
        parent = {}  # Suit le parent de chaque nœud pour reconstruire le cycle
        cycle = []

        def dfs(node: Node) -> bool:
            visited.add(node.name)
            rec_stack.add(node.name)

            # Trouver les voisins (relations directes)
            neighbors = [r.target for r in self.relations if r.source == node and r.direction == Direction.FORWARD]
            for neighbor in neighbors:
                if neighbor.name not in visited:
                    parent[neighbor.name] = node.name  # Enregistrer le parent
                    if dfs(neighbor):
                        return True
                elif neighbor.name in rec_stack and not cycle:
                    # Cycle détecté, reconstruire le cycle
                    current = node.name
                    cycle.append(current)
                    while current != neighbor.name:
                        current = parent[current]
                        cycle.append(current)
                    cycle.append(neighbor.name)  # Ajouter le nœud final pour fermer le cycle
                    cycle.reverse()  # Inverser pour avoir l'ordre correct
                    return True

            rec_stack.remove(node.name)
            return False

        for node in self.nodes.values():
            if node.name not in visited:
                parent[node.name] = None  # Nœud racine n'a pas de parent
                if dfs(node):
                    return cycle
        return []

    def find_all_triplets(self) -> List[Tuple[Node, Node, Node, str, RelationType]]:
        """Find all triplets (series, convergente, divergente) in the graph."""
        triplets = []
        
        # Series: X -> Z -> Y
        for rel1 in self.relations:
            if rel1.direction == Direction.FORWARD:
                x, z = rel1.source, rel1.target
                for rel2 in self.relations:
                    if rel2.source == z and rel2.direction == Direction.FORWARD:
                        y = rel2.target
                        path_segment = f"{x.name}->{z.name}->{y.name}"
                        triplets.append((x, z, y, path_segment, RelationType.SERIES))
        
        # Convergente: X -> Z <- Y
        for z in self.nodes.values():
            incoming = [r for r in self.relations if r.target == z and r.direction == Direction.FORWARD]
            if len(incoming) >= 2:
                for i, rel1 in enumerate(incoming):
                    for rel2 in incoming[i+1:]:
                        x, y = rel1.source, rel2.source
                        path_segment = f"{x.name}->{z.name}<->{y.name}"
                        triplets.append((x, z, y, path_segment, RelationType.CONVERGENTE)) 
        
        # Divergente: Z -> X, Z -> Y
        for z in self.nodes.values():
            outgoing = [r for r in self.relations if r.source == z and r.direction == Direction.FORWARD]
            if len(outgoing) >= 2:
                for i, rel1 in enumerate(outgoing):
                    for rel2 in outgoing[i+1:]:
                        x, y = rel1.target, rel2.target
                        path_segment = f"{z.name}->{x.name},{z.name}->{y.name}"
                        triplets.append((x, z, y, path_segment, RelationType.DIVERGENTE))
        
        return triplets

    def compute_final_path(self) -> str:
        if len(self.relations) < 1:
            return "Error: At least one relation is required."
        
        cycle = self.has_cycle()
        if cycle:
            return f"Cycle détecté : {','.join(cycle)}"

        # Store valid triplets where flow is allowed
        valid_triplets = {}  # (x, z, y) -> (path_segment, relation_type)
        flow_justifications = []

        # Test all triplets
        for x, z, y, path_segment, rel_type in self.find_all_triplets():
            if rel_type == RelationType.SERIES:
                if z.state == NodeState.UNKNOWN:
                    valid_triplets[(x.name, z.name, y.name)] = (path_segment, rel_type)
                    flow_justifications.append(
                        f"Information can flow from {x} to {y} because {z} is unknown (en série)"
                    )
                else:
                    flow_justifications.append(
                        f"Information cannot flow from {x} to {y} because {z} is known (en série)"
                    )
            elif rel_type == RelationType.CONVERGENTE:
                if z.state == NodeState.KNOWN:
                    valid_triplets[(x.name, z.name, y.name)] = (path_segment, rel_type)
                    flow_justifications.append(
                        f"Information can flow from {x} to {y} because {z} is known (convergente)"
                    )
                else:
                    flow_justifications.append(
                        f"Information cannot flow from {x} to {y} because {z} is unknown (convergente)"
                    )
            elif rel_type == RelationType.DIVERGENTE:
                if z.state == NodeState.UNKNOWN:
                    valid_triplets[(x.name, z.name, y.name)] = (path_segment, rel_type)
                    flow_justifications.append(
                        f"Information can flow from {x} to {y} because {z} is unknown (divergente)"
                    )
                else:
                    flow_justifications.append(
                        f"Information cannot flow from {x} to {y} because {z} is known (divergente)"
                    )

        # Print valid triplets for debugging
        print("Valid Triplets Dictionary:")
        for key, (value, rel_type) in valid_triplets.items():
            print(f"  {key}: {value} ({rel_type.value})")

        # Find the first node (no incoming edges)
        all_nodes = set(self.nodes.keys())
        target_nodes = set()
        for rel in self.relations:
            if rel.direction == Direction.FORWARD:
                target_nodes.add(rel.target.name)
            else:
                target_nodes.add(rel.source.name)
        first_nodes = all_nodes - target_nodes

        # Combine triplets into paths
        final_paths = []
        def build_path(current_triplet: Tuple[str, str, str], path: List[str], start_node: str):
            if not path:
                path = [valid_triplets[current_triplet][0]]
            x, z, y = current_triplet
            # Find triplets starting at y
            next_triplets = [(x2, z2, y2) for (x2, z2, y2) in valid_triplets if x2 == y]
            if not next_triplets:
                # Only add path if it starts with a first node
                if start_node in first_nodes:
                    final_paths.append("->".join(path))
                return
            for next_triplet in next_triplets:
                build_path(next_triplet, path + [valid_triplets[next_triplet][0]], start_node)

        # Start building paths from each valid triplet
        for triplet in valid_triplets:
            x, _, _ = triplet
            build_path(triplet, [], x)

        # Format output
        if not final_paths:
            final_path = "No path where information can flow"
        else:
            final_path = "\n".join(f"Path: {path}" for path in final_paths)
        justification = "Justification:\n" + "\n".join(flow_justifications) if flow_justifications else "Justification: No flow possible."
        return f"Final Paths:\n{final_path}\n{justification}"
    
    
    
    


# class NetworkInterface:
#     def __init__(self):
#         self.network = BayesianNetwork()

#     def run(self):
#         print("Welcome to Bayesian Network Causality Interface")
#         while True:
#             print("\nOptions: 1) Add Tuple  2) Compute Path  3) Exit")
#             choice = input("Choose an option: ")
            
#             if choice == "1":
#                 self.add_tuple()
#             elif choice == "2":
#                 print(self.network.compute_final_path())
#             elif choice == "3":
#                 print("Goodbye!")
#                 break
#             else:
#                 print("Invalid option.")

#     def add_tuple(self):
#         tuple_input = input("Enter tuple (e.g., 'X,Z'): ").split(",")
#         if len(tuple_input) != 2:
#             print("Invalid tuple format.")
#             return
        
#         first, second = tuple_input[0].strip(), tuple_input[1].strip()
        
        
#         state_first = input(f"State of {first} (known/unknown): ").lower()
#         state_second = input(f"State of {second} (known/unknown): ").lower()
#         state_first = NodeState.KNOWN if state_first == "known" else NodeState.UNKNOWN
#         state_second = NodeState.KNOWN if state_second == "known" else NodeState.UNKNOWN
        
        
#         direction = input("Direction (-> or <-): ")
#         direction = Direction.FORWARD if direction == "->" else Direction.BACKWARD
        
        
        
#         if direction == Direction.FORWARD:
#             source,target = first,second
#             source_state, target_state = state_first, state_second
            
#         else: # Direction.BACKWARD
#             source,target=second,first
#             source_state, target_state = state_second, state_first
            
        
#         self.network.add_relation(source, target, direction, source_state, target_state)
#         display_str = f"{first} -> {second}" if direction == Direction.FORWARD else f"{first} <- {second}"
#         print(f"Added: {display_str}")
#         # print(f"Added: {source} ({source_state.value}) {direction.value} {target} ({target_state.value})")
            
        

# # Run the interface
# if __name__ == "__main__":
#     interface = NetworkInterface()
#     interface.run()



class NetworkGUI:
    def __init__(self, root):
        self.network = BayesianNetwork()
        self.root = root
        self.root.title("Bayesian Network Causality Interface")
        self.root.geometry("600x500")

        # Input frame
        input_frame = ttk.Frame(root, padding="10")
        input_frame.pack(fill="x")

        ttk.Label(input_frame, text="Tuple (e.g., 'X,Z'):").grid(row=0, column=0, padx=5, pady=5)
        self.tuple_entry = ttk.Entry(input_frame)
        self.tuple_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="State of First:").grid(row=1, column=0, padx=5, pady=5)
        self.state_first = ttk.Combobox(input_frame, values=["known", "unknown"], state="readonly")
        self.state_first.set("unknown")
        self.state_first.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="State of Second:").grid(row=2, column=0, padx=5, pady=5)
        self.state_second = ttk.Combobox(input_frame, values=["known", "unknown"], state="readonly")
        self.state_second.set("unknown")
        self.state_second.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Direction:").grid(row=3, column=0, padx=5, pady=5)
        self.direction = ttk.Combobox(input_frame, values=["->", "<-"], state="readonly")
        self.direction.set("->")
        self.direction.grid(row=3, column=1, padx=5, pady=5)

        ttk.Button(input_frame, text="Add Tuple", command=self.add_tuple).grid(row=4, column=0, columnspan=2, pady=10)

        # Output frame
        output_frame = ttk.Frame(root, padding="10")
        output_frame.pack(fill="both", expand=True)

        ttk.Label(output_frame, text="Network Output:").pack()
        self.output_text = tk.Text(output_frame, height=15, width=70)
        self.output_text.pack(fill="both", expand=True)

        ttk.Button(output_frame, text="Compute Path", command=self.compute_path).pack(pady=10)

    def add_tuple(self):
        tuple_input = self.tuple_entry.get().strip()
        if "," not in tuple_input or len(tuple_input.split(",")) != 2:
            messagebox.showerror("Error", "Invalid tuple format. Use 'X,Z'.")
            return

        first, second = [x.strip() for x in tuple_input.split(",")]
        state_first = NodeState[self.state_first.get().upper()]
        state_second = NodeState[self.state_second.get().upper()]
        
        # Map Combobox direction value to Direction enum
        direction_str = self.direction.get()
        if direction_str == "->":
            direction = Direction.FORWARD
        elif direction_str == "<-":
            direction = Direction.BACKWARD
        else:
            messagebox.showerror("Error", "Invalid direction selected.")
            return

        if direction == Direction.FORWARD:
            source, target = first, second
            source_state, target_state = state_first, state_second
        else:
            source, target = second, first
            source_state, target_state = state_second, state_first

        self.network.add_relation(source, target, direction, source_state, target_state)
        display_str = f"{first} -> {second}" if direction == Direction.FORWARD else f"{first} <- {second}"
        self.output_text.insert(tk.END, f"Added: {display_str}\n")
        self.tuple_entry.delete(0, tk.END)  # Clear entry after adding

    def compute_path(self):
        result = self.network.compute_final_path()
        self.output_text.delete(1.0, tk.END)  # Clear previous output
        self.output_text.insert(tk.END, result + "\n")

# Run the GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkGUI(root)
    root.mainloop()