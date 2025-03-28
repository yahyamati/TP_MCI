from enum import Enum
from typing import List, Dict
import tkinter as tk
from tkinter import ttk, messagebox


# Enum for node states and relation direction
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

# Node class
class Node:
    def __init__(self, name: str, state: NodeState = NodeState.UNKNOWN):
        self.name = name
        self.state = state

    def __str__(self):
        return f"{self.name} ({self.state.value})"

# Relation class
class Relation:
    def __init__(self, source: Node, target: Node, direction: Direction):
        self.source = source
        self.target = target
        self.direction = direction

    def __str__(self):
        return f"{self.source} {self.direction.value} {self.target}"

# BayesianNetwork class
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
            return RelationType.CONVERGENTE  # X -> Z <- Y
        elif len(incoming) == 1 and len(outgoing) == 1:
            return RelationType.SERIES  # X -> Z -> Y
        elif len(incoming) == 0 and len(outgoing) >= 2:
            return RelationType.DIVERGENTE  # Z -> X, Z -> Y
        return None

    def compute_final_path(self) -> str:
        if len(self.relations) < 1:
            return "Error: At least one relation is required."

        path_parts = []
        flow_justifications = []
        can_flow = True

        for i, rel in enumerate(self.relations):
            # Use only node names for the path
            if rel.direction == Direction.FORWARD:
                segment = f"{rel.source.name}->{rel.target.name}"
            else:
                segment = f"{rel.target.name}<-{rel.source.name}"

            if i > 0:
                prev_rel = self.relations[i - 1]
                if prev_rel.target == rel.source:  # Series: X -> Z -> Y
                    z = rel.source
                    x = prev_rel.source
                    y = rel.target
                    if self.infer_relation_type(z) == RelationType.SERIES:
                        if z.state == NodeState.UNKNOWN:
                            flow_justifications.append(
                                f"Information can flow from {x} to {y} because {z} is unknown (en série)"
                            )
                            if can_flow:
                                path_parts.append(segment)
                        else:
                            flow_justifications.append(
                                f"Information cannot flow from {x} to {y} because {z} is known (en série)"
                            )
                            can_flow = False
                elif rel.target == prev_rel.target:  # Convergente: X -> Z <- Y
                    z = rel.target
                    x = prev_rel.source
                    y = rel.source
                    if self.infer_relation_type(z) == RelationType.CONVERGENTE:
                        if z.state == NodeState.KNOWN:
                            flow_justifications.append(
                                f"Information can flow from {x} to {y} because {z} is known (convergente)"
                            )
                            if can_flow:
                                path_parts.append(segment)
                        else:
                            flow_justifications.append(
                                f"Information cannot flow from {x} to {y} because {z} is unknown (convergente)"
                            )
                            can_flow = False
            else:
                if can_flow:
                    path_parts.append(segment)

            if self.infer_relation_type(rel.source) == RelationType.DIVERGENTE:
                outgoing = [r for r in self.relations if r.source == rel.source]
                if len(outgoing) >= 2:
                    x, y = outgoing[0].target, outgoing[1].target
                    z = rel.source
                    if z.state == NodeState.UNKNOWN:
                        flow_justifications.append(
                            f"Information can flow from {x} to {y} because {z} is unknown (divergente)"
                        )
                    else:
                        flow_justifications.append(
                            f"Information cannot flow from {x} to {y} because {z} is known (divergente)"
                        )
                        can_flow = False

        final_path = "".join(path_parts) if path_parts else "No path where information can flow"
        justification = "Justification:\n" + "\n".join(flow_justifications) if flow_justifications else "Justification: No flow possible."
        return f"Final Path: {final_path}\n{justification}"
    
    
    
    


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