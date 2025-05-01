import customtkinter as ctk
from tkinter import messagebox
import networkx as nx
import matplotlib.pyplot as plt
import itertools

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class ModernBayesianNetworkApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Réseau Bayésien - Interface Moderne")
        self.root.geometry("900x700")

        self.variables = []
        self.relations = []
        self.etats = {}

        # Couleurs personnalisées
        self.bg_color = "#2B2D42"
        self.accent_color = "#8D99AE"
        self.button_color = "#EF233C"
        self.text_color = "#EDF2F4"

        # Frame principale
        self.main_frame = ctk.CTkFrame(root, fg_color=self.bg_color, corner_radius=10)
        self.main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Section pour ajouter des variables
        self.var_frame = ctk.CTkFrame(
            self.main_frame, fg_color=self.bg_color, corner_radius=10
        )
        self.var_frame.pack(padx=10, pady=10, fill="x")

        self.var_label = ctk.CTkLabel(
            self.var_frame,
            text="Nouvelle Variable :",
            font=("Helvetica", 14),
            text_color=self.text_color,
        )
        self.var_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.var_entry = ctk.CTkEntry(
            self.var_frame,
            placeholder_text="Entrez le nom",
            width=200,
            font=("Helvetica", 12),
            fg_color="#3A3F5C",
        )
        self.var_entry.grid(row=0, column=1, padx=10, pady=5)

        self.state_label = ctk.CTkLabel(
            self.var_frame,
            text="État :",
            font=("Helvetica", 14),
            text_color=self.text_color,
        )
        self.state_label.grid(row=0, column=2, pady=5, sticky="w")

        self.state_combo = ctk.CTkComboBox(
            self.var_frame,
            values=["connu", "inconnu"],
            font=("Helvetica", 12),
            dropdown_fg_color="#3A3F5C",
        )
        self.state_combo.set("inconnu")
        self.state_combo.grid(row=0, column=3, padx=10, pady=5)

        self.add_var_btn = ctk.CTkButton(
            self.var_frame,
            text="Ajouter",
            command=self.ajouter_variable,
            fg_color=self.button_color,
            hover_color="#D90429",
            font=("Helvetica", 12, "bold"),
            corner_radius=15,
        )
        self.add_var_btn.grid(row=0, column=4, padx=10, pady=5)

        # Section pour ajouter des relations
        self.rel_frame = ctk.CTkFrame(
            self.main_frame, fg_color=self.bg_color, corner_radius=10
        )
        self.rel_frame.pack(padx=10, pady=10, fill="x")

        self.cause_label = ctk.CTkLabel(
            self.rel_frame,
            text="Cause :",
            font=("Helvetica", 14),
            text_color=self.text_color,
        )
        self.cause_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.cause_combo = ctk.CTkComboBox(
            self.rel_frame,
            values=self.variables,
            font=("Helvetica", 12),
            dropdown_fg_color="#3A3F5C",
        )
        self.cause_combo.grid(row=0, column=1, padx=10, pady=5)

        self.effet_label = ctk.CTkLabel(
            self.rel_frame,
            text="Effet :",
            font=("Helvetica", 14),
            text_color=self.text_color,
        )
        self.effet_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.effet_combo = ctk.CTkComboBox(
            self.rel_frame,
            values=self.variables,
            font=("Helvetica", 12),
            dropdown_fg_color="#3A3F5C",
        )
        self.effet_combo.grid(row=1, column=1, padx=10, pady=5)

        self.add_relation_btn = ctk.CTkButton(
            self.rel_frame,
            text="Ajouter Relation",
            command=self.ajouter_relation,
            fg_color=self.button_color,
            hover_color="#D90429",
            font=("Helvetica", 12, "bold"),
            corner_radius=15,
        )
        self.add_relation_btn.grid(row=1, column=2, padx=10, pady=5)

        # Section pour sélectionner le nœud de départ
        self.start_node_frame = ctk.CTkFrame(
            self.main_frame, fg_color=self.bg_color, corner_radius=10
        )
        self.start_node_frame.pack(padx=10, pady=10, fill="x")

        self.start_node_label = ctk.CTkLabel(
            self.start_node_frame,
            text="Nœud de départ :",
            font=("Helvetica", 14),
            text_color=self.text_color,
        )
        self.start_node_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.start_node_combo = ctk.CTkComboBox(
            self.start_node_frame,
            values=self.variables,
            font=("Helvetica", 12),
            dropdown_fg_color="#3A3F5C",
        )
        self.start_node_combo.grid(row=0, column=1, padx=10, pady=5)

        # Section pour les actions
        self.action_frame = ctk.CTkFrame(
            self.main_frame, fg_color=self.bg_color, corner_radius=10
        )
        self.action_frame.pack(padx=10, pady=10, fill="x")

        self.display_btn = ctk.CTkButton(
            self.action_frame,
            text="Afficher Graphe",
            command=self.afficher_graphe,
            fg_color="#048BA8",
            hover_color="#016782",
            font=("Helvetica", 12, "bold"),
            corner_radius=15,
            width=200,
        )
        self.display_btn.grid(row=0, column=0, padx=10, pady=10)

        self.detect_btn = ctk.CTkButton(
            self.action_frame,
            text="Détecter Triplets",
            command=self.detecter_relations_triplet,
            fg_color="#048BA8",
            hover_color="#016782",
            font=("Helvetica", 12, "bold"),
            corner_radius=15,
            width=200,
        )
        self.detect_btn.grid(row=0, column=1, padx=10, pady=10)

        self.circulation_btn = ctk.CTkButton(
            self.action_frame,
            text="Circulation Info",
            command=self.circulation_information,
            fg_color="#048BA8",
            hover_color="#016782",
            font=("Helvetica", 12, "bold"),
            corner_radius=15,
            width=200,
        )
        self.circulation_btn.grid(row=0, column=2, padx=10, pady=10)

        # Boîte de texte pour les résultats
        self.display_box = ctk.CTkTextbox(
            self.main_frame,
            height=350,
            width=850,
            font=("Helvetica", 12),
            fg_color="#3A3F5C",
            text_color=self.text_color,
        )
        self.display_box.pack(padx=10, pady=10, fill="both", expand=True)

    def afficher_message(self, texte):
        self.display_box.insert("end", texte + "\n")
        self.display_box.see("end")

    def ajouter_variable(self):
        nom = self.var_entry.get().strip()
        etat = self.state_combo.get()
        if nom and nom not in self.variables:
            self.variables.append(nom)
            self.etats[nom] = etat
            self.cause_combo.configure(values=self.variables)
            self.effet_combo.configure(values=self.variables)
            self.start_node_combo.configure(values=self.variables)
            self.afficher_message(f"[Variable] '{nom}' ajoutée avec état : {etat}")
            self.var_entry.delete(0, "end")
            if (
                not self.start_node_combo.get()
            ):  # Sélectionner le premier nœud par défaut
                self.start_node_combo.set(nom)
        else:
            messagebox.showwarning("Erreur", "Nom invalide ou déjà existant.")

    def ajouter_relation(self):
        cause = self.cause_combo.get()
        effet = self.effet_combo.get()
        if cause in self.variables and effet in self.variables and cause != effet:
            relation = (cause, effet)
            if relation not in self.relations:
                self.relations.append(relation)
                self.afficher_message(f"[Relation] {cause} → {effet}")
        else:
            messagebox.showwarning("Erreur", "Relation invalide.")

    def afficher_graphe(self):
        G = nx.DiGraph()
        G.add_nodes_from(self.variables)
        G.add_edges_from(self.relations)
        colors = ["green" if self.etats[v] == "connu" else "red" for v in G.nodes]

        plt.figure(figsize=(8, 6))
        pos = nx.spring_layout(G)
        nx.draw(
            G,
            pos,
            with_labels=True,
            nodePhoenixcolor=colors,
            edge_color="gray",
            arrows=True,
            node_size=2000,
            font_size=10,
            arrowsize=20,
        )
        plt.title("Réseau Bayésien")
        plt.show()

    def detecter_relations_triplet(self):
        if len(self.variables) < 3:
            messagebox.showinfo("Info", "Il faut au moins 3 variables.")
            return

        resultats = []
        relations = set(self.relations)

        for triplet in itertools.combinations(self.variables, 3):
            a, b, c = triplet
            if (a, b) in relations and (b, c) in relations:
                resultats.append(f"[Serie] {a} → {b} → {c}")
            elif (b, a) in relations and (b, c) in relations:
                resultats.append(f"[Divergente] {a} ← {b} → {c}")
            elif (a, b) in relations and (c, b) in relations:
                resultats.append(f"[Convergente] {a} → {b} ← {c}")

        self.afficher_message("=== Analyse des triplets ===")
        for res in resultats:
            self.afficher_message(res)

    def has_cycle(self):
        G = nx.DiGraph()
        G.add_nodes_from(self.variables)
        G.add_edges_from(self.relations)
        try:
            cycle = nx.find_cycle(G, orientation="original")
            return [node for node, _ in cycle]
        except nx.NetworkXNoCycle:
            return []

    def circulation_information(self):
        if len(self.variables) < 3:
            messagebox.showinfo("Info", "Il faut au moins 3 variables.")
            return

        start_node = self.start_node_combo.get()
        if not start_node:
            start_node = self.variables[0] if self.variables else None
        if not start_node:
            messagebox.showwarning(
                "Erreur",
                "Aucun nœud de départ sélectionné ou aucune variable disponible.",
            )
            return

        cycle = self.has_cycle()
        if cycle:
            self.afficher_message(f"Cycle détecté : {' → '.join(cycle)}")
            return

        self.afficher_message(
            f"=== Chemin final où l'information peut circuler (commençant par {start_node}) ==="
        )
        G = nx.DiGraph()
        G.add_nodes_from(self.variables)
        G.add_edges_from(self.relations)

        chemins_valides = []

        # Trouver tous les chemins commençant par start_node
        for target in self.variables:
            if target != start_node:
                for path in nx.all_simple_paths(G.to_undirected(), start_node, target):
                    if len(path) >= 2:  # Accepter les chemins d'au moins 2 nœuds
                        passe = True
                        for i in range(len(path) - 2):
                            a, b, c = path[i], path[i + 1], path[i + 2]
                            etat_b = self.etats.get(b, "inconnu")
                            if (a, b) in self.relations and (b, c) in self.relations:
                                if etat_b == "connu":
                                    passe = False
                                    break
                            elif (b, a) in self.relations and (b, c) in self.relations:
                                if etat_b == "connu":
                                    passe = False
                                    break
                            elif (a, b) in self.relations and (c, b) in self.relations:
                                if etat_b != "connu":
                                    passe = False
                                    break
                            else:
                                passe = False
                                break
                        if passe:
                            chemins_valides.append(path)

        if not chemins_valides:
            self.afficher_message("Aucun chemin valide trouvé.")
            return

        # Filtrer les chemins finaux (ceux qui se terminent par un blocage ou un nœud isolé)
        chemins_finaux = []
        for path in chemins_valides:
            chemin_final = path
            for i in range(len(path) - 1):
                current_node = path[i]
                next_node = path[i + 1]
                # Vérifier si le nœud suivant bloque l'information
                if i < len(path) - 2:
                    a, b, c = path[i], path[i + 1], path[i + 2]
                    etat_b = self.etats.get(b, "inconnu")
                    if (a, b) in self.relations and (b, c) in self.relations:
                        if etat_b == "connu":
                            chemin_final = path[: i + 2]  # Tronquer au point de blocage
                            break
                    elif (b, a) in self.relations and (b, c) in self.relations:
                        if etat_b == "connu":
                            chemin_final = path[: i + 2]
                            break
                    elif (a, b) in self.relations and (c, b) in self.relations:
                        if etat_b != "connu":
                            chemin_final = path[: i + 2]
                            break
                # Vérifier si le nœud est isolé (pas de relation sortante ou pas dans un triplet)
                outgoing_relations = [r for r in self.relations if r[0] == next_node]
                if not outgoing_relations:
                    chemin_final = path[: i + 2]  # Tronquer au nœud isolé
                    break
                # Vérifier si le nœud suivant ne peut pas former un triplet valide
                forms_triplet = False
                for c in self.variables:
                    if (next_node, c) in self.relations and c != current_node:
                        forms_triplet = True
                        break
                if not forms_triplet:
                    chemin_final = path[: i + 2]
                    break
            if chemin_final not in chemins_finaux:
                chemins_finaux.append(chemin_final)

        # Afficher tous les chemins finaux
        if chemins_finaux:
            for chemin in chemins_finaux:
                self.afficher_message(" → ".join(chemin))
                for j in self.justifier_chemin(chemin):
                    self.afficher_message("    " + j)
        else:
            self.afficher_message("Aucun chemin valide trouvé.")

    def justifier_chemin(self, chemin):
        justifications = []
        for i in range(len(chemin) - 2):
            a, b, c = chemin[i], chemin[i + 1], chemin[i + 2]
            etat_b = self.etats.get(b, "inconnu")

            if (a, b) in self.relations and (b, c) in self.relations:
                structure = f"série ({a} → {b} → {c})"
                if etat_b == "connu":
                    raison = f"bloqué car {b} est connu"
                else:
                    raison = f"l'information passe car {b} est inconnu"
                justifications.append(
                    f"triple [{a}, {b}, {c}] : {structure} → {raison}"
                )
            elif (b, a) in self.relations and (b, c) in self.relations:
                structure = f"divergence ({a} ← {b} → {c})"
                if etat_b == "connu":
                    raison = f"bloITIqué car {b} est connu"
                else:
                    raison = f"l'information passe car {b} est inconnu"
                justifications.append(
                    f"triple [{a}, {b}, {c}] : {structure} → {raison}"
                )
            elif (a, b) in self.relations and (c, b) in self.relations:
                structure = f"convergence ({a} → {b} ← {c})"
                if etat_b != "connu":
                    raison = f"bloqué car {b} est inconnu"
                else:
                    raison = f"l'information passe car {b} est connu"
                justifications.append(
                    f"triple [{a}, {b}, {c}] : {structure} → {raison}"
                )

        return justifications


if __name__ == "__main__":
    root = ctk.CTk()
    app = ModernBayesianNetworkApp(root)
    root.mainloop()