# -*- coding: utf-8 -*-
"""
Created on Sat May  2 10:25:20 2026

@author: Laowy
"""

import customtkinter
import xml.etree.ElementTree as ET
import re
import os
from odf.opendocument import OpenDocumentText
from odf.text import P, Tab
from odf.style import Style, TextProperties, ParagraphProperties, TabStop, TabStops

# ==========================================
# 1. LOGIQUE DE TRAITEMENT XML & ODT
# ==========================================

def tri_naturel(texte):
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', texte)]

def extraire_meilleure_ligne(paroles):
    priorites = ['[C]'] + [f'[C{i}]' for i in range(1, 10)] + ['[V]'] + [f'[V{i}]' for i in range(1, 10)]
    for balise in priorites:
        balise_esc = re.escape(balise)
        match = re.search(rf'{balise_esc}([\s\S]*?)(?=\[|$)', paroles, re.IGNORECASE)
        if match:
            for ligne in match.group(1).strip().split('\n'):
                ligne = ligne.strip()
                if not ligne or ligne.startswith('.'): continue
                ligne_propre = " ".join(re.sub(r'^\d+', '', ligne).split())
                if ligne_propre: return ligne_propre
    return "Sans_Titre"

def traiter_fichier(chemin_src, nom_orig, dossier_dest, index_global):
    try:
        tree = ET.parse(chemin_src)
        root = tree.getroot()
        
        nom_sans_ext = os.path.splitext(nom_orig)[0]
        lyrics_node = root.find('lyrics')
        paroles = lyrics_node.text if (lyrics_node is not None and lyrics_node.text) else ""
        
        # LOGIQUE D'EXTRACTION POUR L'INDEX
        if nom_sans_ext.isdigit():
            numero = nom_sans_ext
            titre_seul = extraire_meilleure_ligne(paroles)
            nouveau_titre = f"{numero} {titre_seul}"
            
        elif match := re.match(r'^(\d+)\s*[-_]?\s*(.*)', nom_sans_ext):
            numero = match.group(1)
            titre_seul = match.group(2).strip()
            if not titre_seul: titre_seul = extraire_meilleure_ligne(paroles)
            nouveau_titre = nom_sans_ext
            
        else:
            numero = str(index_global)
            titre_seul = nom_sans_ext
            nouveau_titre = f"{numero} {titre_seul}"

        # Mise à jour de l'XML
        title_node = root.find('title')
        if title_node is not None: title_node.text = nouveau_titre
        else: ET.SubElement(root, 'title').text = nouveau_titre

        nom_final = re.sub(r'[\\/*?:"<>|]', "", nouveau_titre)
        
        if not os.path.exists(dossier_dest): os.makedirs(dossier_dest)
        tree.write(os.path.join(dossier_dest, nom_final), encoding="UTF-8", xml_declaration=True)
        
        # On retourne le nom final, le succès, et les données pour l'index
        return nom_final, True, titre_seul, numero
    except Exception as e:
        return str(e), False, "", ""

def generer_index_odt(liste_chansons, dossier_dest):
    """Génère un index ODT groupé par lettre avec numéros alignés à droite."""
    if not liste_chansons:
        return
        
    chemin_fichier = os.path.join(dossier_dest, "Index_Alphabétique.odt")
    doc = OpenDocumentText()

    # --- STYLE POUR LES LETTRES (A, B, C...) ---
    style_lettre = Style(name="StyleLettre", family="paragraph")
    style_lettre.addElement(TextProperties(fontsize="22pt", fontweight="bold"))
    style_lettre.addElement(ParagraphProperties(margintop="0.5cm", marginbottom="0.2cm"))
    doc.automaticstyles.addElement(style_lettre)

    # --- STYLE POUR LES CHANTS ---
    style_chant = Style(name="StyleChant", family="paragraph")
    style_chant.addElement(TextProperties(fontsize="11pt", fontfamily="Arial"))
    
    # 1. Créer l'objet des propriétés de paragraphe
    p_props = ParagraphProperties()
    
    # 2. Créer l'objet contenant les tabulations
    tabs = TabStops()
    # On définit la butée à 15cm, alignée à droite, avec des points
    tabs.addElement(TabStop(type="right", position="15cm", leaderstyle="dotted"))
    
    # 3. IMBRICATION CORRECTE :
    # On ajoute les TabStops DANS les ParagraphProperties
    p_props.addElement(tabs)
    # On ajoute les ParagraphProperties DANS le Style
    style_chant.addElement(p_props)
    
    doc.automaticstyles.addElement(style_chant)

    # Tri alphabétique
    liste_chansons.sort(key=lambda x: x[0].lower())

    current_letter = ""
    for titre, num in liste_chansons:
        titre = titre.strip()
        if not titre: continue
        
        premiere_lettre = titre[0].upper()
        
        if premiere_lettre != current_letter:
            current_letter = premiere_lettre
            doc.text.addElement(P(text=current_letter, stylename=style_lettre))

        # --- MODIFICATION ICI ---
        p_chant = P(stylename=style_chant)
        
        # 1. On ajoute le texte du titre
        p_chant.addText(titre)
        
        # 2. On ajoute l'élément TabULATION (c'est lui qui déclenche les points)
        p_chant.addElement(Tab())
        
        # 3. On ajoute le numéro
        p_chant.addText(str(num))
        
        doc.text.addElement(p_chant)

    doc.save(chemin_fichier)


# ==========================================
# 2. INTERFACE GRAPHIQUE CUSTOMTKINTER
# ==========================================

class MyScrollableFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, title):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.title = title
        self.elements = []
        
        if title != "":
            self.title_label = customtkinter.CTkLabel(self, text=self.title, fg_color="gray30", corner_radius=6)
            self.title_label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")
        
    def add_element(self, label, text_color=None):
        new_row = len(self.elements) + 1
        element = customtkinter.CTkLabel(self, text=label, fg_color="gray25", corner_radius=6, text_color=text_color, anchor="w")
        element.grid(row=new_row, column=0, padx=10, pady=(10, 0), sticky="ew")
        self.elements.append(element)

    def clear_elements(self):
        for element in self.elements:
            element.destroy()
        self.elements.clear()


class MyFrame(customtkinter.CTkFrame):
    def __init__(self, master, title, result_frame):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.title = title
        self.result_frame = result_frame

        self.title_label = customtkinter.CTkLabel(self, text=self.title, fg_color="gray30", corner_radius=6)
        self.title_label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew", columnspan=2)
        
        self.source = customtkinter.CTkEntry(self, placeholder_text="Dossier Source...")
        self.source.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="ew")
        
        self.button_search = customtkinter.CTkButton(self, text="Search", command=self.button_search_event)
        self.button_search.grid(row=1, column=1, padx=10, pady=(10, 0), sticky="ew")
        
        self.frame_found = MyScrollableFrame(self, "Fichiers trouvés")
        self.frame_found.grid(row=2, column=0, padx=10, pady=10, sticky="nsew", columnspan=2)
        
        self.destination = customtkinter.CTkEntry(self, placeholder_text="Dossier Destination...")
        self.destination.grid(row=3, column=0, padx=10, pady=(10, 0), sticky="ew")
        
        self.button_rename = customtkinter.CTkButton(self, text="Rename", command=self.button_rename_event, fg_color="green", hover_color="darkgreen")
        self.button_rename.grid(row=3, column=1, padx=10, pady=(10, 0), sticky="ew")
        
    def button_search_event(self):
        dossier = self.source.get()
        self.frame_found.clear_elements()
        
        if os.path.exists(dossier):
            fichiers_trouves = []
            for root, dirs, files in os.walk(dossier):
                for f in files:
                    fichiers_trouves.append(f)
            
            fichiers_trouves.sort(key=tri_naturel)
            for f in fichiers_trouves:
                self.frame_found.add_element(f)
                
            self.frame_found.title_label.configure(text=f"{len(fichiers_trouves)} Fichiers trouvés")
        else:
            self.frame_found.add_element("❌ Dossier introuvable", text_color="red")
        
    def button_rename_event(self):
        dossier_src = self.source.get()
        dossier_dest = self.destination.get()
        self.result_frame.clear_elements()
        
        if not os.path.exists(dossier_src) or dossier_dest == "":
            self.result_frame.add_element("❌ Veuillez remplir les deux dossiers valides.", text_color="red")
            return

        fichiers_bruts = []
        for root, dirs, files in os.walk(dossier_src):
            for f in files:
                fichiers_bruts.append((os.path.join(root, f), f))
        
        fichiers_bruts.sort(key=lambda x: tri_naturel(x[1]))
        
        # Liste pour stocker les tuples (Titre, Numero) pour l'index
        donnees_index = []
        count = 0
        
        for i, (chemin, nom) in enumerate(fichiers_bruts, start=1):
            resultat, succes, titre_seul, numero = traiter_fichier(chemin, nom, dossier_dest, i)
            if succes:
                self.result_frame.add_element(f"✅ {nom} ➔ {resultat}", text_color="lightgreen")
                # On ajoute à notre liste pour le document .odt
                donnees_index.append((titre_seul, numero))
                count += 1
            else:
                self.result_frame.add_element(f"⚠️ Ignoré: {nom}", text_color="orange")
                
        # --- GÉNÉRATION DE L'ODT ICI ---
        if donnees_index:
            generer_index_odt(donnees_index, dossier_dest)
            self.result_frame.add_element("📝 Index_Alphabétique.odt généré avec succès !", text_color="cyan")
                
        self.result_frame.title_label.configure(text=f"Résultats ({count} traités)")


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("XML Renamer Pro")
        self.geometry("1000x600")
        
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(0, weight=1) 
        
        self.frame_result = MyScrollableFrame(self, "Résultats du renommage")
        self.frame_result.grid(row=0, column=1, padx=(5, 10), pady=10, sticky="nsew")
        
        self.frame_search = MyFrame(self, "Configuration", self.frame_result)
        self.frame_search.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="nsew")

if __name__ == "__main__":
    customtkinter.set_appearance_mode("dark")
    customtkinter.set_default_color_theme("blue") 
    app = App()
    app.mainloop()