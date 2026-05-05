# -*- coding: utf-8 -*-
"""
Created on Sat May  2 10:25:20 2026

@author: Laowy
"""

import customtkinter
import threading
import xml.etree.ElementTree as ET
import re
import os
from odf.opendocument import OpenDocumentText
from odf.text import P, Tab
from odf.style import Style, TextProperties, ParagraphProperties, TabStop, TabStops

titre_for_num = 1


# ==========================================
# 1. LOGIQUE DE TRAITEMENT XML & ODT
# ==========================================

def tri_naturel(texte):
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', texte)]



def extraire_meilleure_ligne(paroles):
    if not paroles: return "Sans_Titre"

    priorites = ['[C]'] + [f'[C{i}]' for i in range(1, 10)] + ['[V]'] + [f'[V{i}]' for i in range(1, 10)]
    
    # On cherche dans les blocs, puis en fallback
    def nettoyer_ligne(l):
        l = l.strip()
        if not l or l.startswith('.'): return None
        # Enlever les chiffres au début
        l = re.sub(r'^\d+', '', l).strip()
        # Enlever la ponctuation parasite au début (mais garder les lettres/chiffres)
        l = re.sub(r'^[!+?\'",;.:\s\-]+', '', l).strip()
        return " ".join(l.split()) if l else None

    # Étape 1 : Balises
    for balise in priorites:
        match = re.search(rf'{re.escape(balise)}\s*([\s\S]*?)(?=\[|$)', paroles, re.IGNORECASE)
        if match:
            for ligne in match.group(1).strip().split('\n'):
                lp = nettoyer_ligne(ligne)
                if lp: return lp

    # Étape 2 : Fallback intégral
    for ligne in paroles.strip().split('\n'):
        if ligne.strip().startswith('['): continue
        lp = nettoyer_ligne(ligne)
        if lp: return lp

    return "Sans_Titre"



def traiter_fichier_complet(chemin_src, nom_orig, dossier_dest, index_global):
    try:
        tree = ET.parse(chemin_src)
        root = tree.getroot()
        
        nom_sans_ext = os.path.splitext(nom_orig)[0]
        
        # --- NETTOYAGE PRÉALABLE DU NOM ---
        # 1. Supprimer les "(Bis)", "(bis)", "+Bis", etc.
        nom_sans_ext = re.sub(r'\(?\+?bis\)?', '', nom_sans_ext, flags=re.IGNORECASE).strip()
        # 2. Supprimer la ponctuation bizarre au tout début (ex: ! ou ')
        nom_sans_ext = re.sub(r'^[!+?\'",;.:\s\-]+', '', nom_sans_ext).strip()

        lyrics_node = root.find('lyrics')
        paroles = lyrics_node.text if (lyrics_node is not None and lyrics_node.text) else ""
        numero = str(index_global) 

        # Logique d'extraction (Regex)
        match = re.match(r'^([a-zA-Z]*\d+[a-zA-Z]*)\s*[-_]?\s*(.*)$', nom_sans_ext)
        
        if match:
            reste = match.group(2).strip()
            if not reste:
                titre_seul = extraire_meilleure_ligne(paroles)
            else:
                titre_seul = reste
        else:
            titre_seul = nom_sans_ext.strip()

        # Un dernier coup de propre sur le titre extrait
        titre_seul = re.sub(r'^[!+?\'",;.:\s\-]+', '', titre_seul).strip()
        nouveau_titre = f"{numero} {titre_seul}"

        # Mise à jour XML
        title_node = root.find('title')
        if title_node is not None: title_node.text = nouveau_titre
        else: ET.SubElement(root, 'title').text = nouveau_titre

        # Sauvegarde
        nom_final = re.sub(r'[\\/*?:"<>|]', "", nouveau_titre)
        if not os.path.exists(dossier_dest): os.makedirs(dossier_dest)
        tree.write(os.path.join(dossier_dest, nom_final), encoding="UTF-8", xml_declaration=True)
        
        return nom_final, True, titre_seul, numero, paroles
        
    except Exception as e:
        return str(e), False, "", "", ""
    
    
def traiter_fichier_index_seulement(chemin_src, nom_orig, dossier_dest, index_global):
    try:
        global titre_for_num
        tree = ET.parse(chemin_src)
        root = tree.getroot()
        
        nom_sans_ext = os.path.splitext(nom_orig)[0]
        
        # --- 1. NETTOYAGE PRÉALABLE DU NOM ---
        # Note : On ne supprime plus "bis" ici pour éviter de perdre l'info sur "26bis"
        # On nettoie uniquement la ponctuation bizarre au début
        nom_sans_ext = re.sub(r'^[!+?\'",;.:\s\-<]+', '', nom_sans_ext).strip()

        lyrics_node = root.find('lyrics')
        paroles = lyrics_node.text if (lyrics_node is not None and lyrics_node.text) else ""
        
        # Initialisation des variables
        numero = str(index_global)
        titre_seul = ""
        nouveau_titre = ""

        # --- 2. LOGIQUE CONDITIONNELLE (ORDRE DE PRIORITÉ) ---

        # CAS 1 : NUMÉRO COLLÉ À DES LETTRES (ex: "26bis", "25er", "956b", "756Tu")
        # On cherche des chiffres suivis immédiatement de lettres
        match_colle = re.match(r'^(\d+)([a-zA-Z].*)$', nom_sans_ext)
        
        if match_colle:
            numero = match_colle.group(1)
            titre_seul = match_colle.group(2).strip()
            nouveau_titre = f"{numero} {titre_seul}"

        # CAS 2 : NUMÉRO SEUL (ex: "123") -> On cherche le titre dans les paroles
        elif re.match(r'^\d+$', nom_sans_ext):
            numero = nom_sans_ext
            if (titre_for_num):
                titre_seul = extraire_meilleure_ligne(paroles)
                nouveau_titre = f"{numero} {titre_seul}"
            else:
                titre_seul = "1-Sans_titre"
                nouveau_titre = f"{numero}"

        # CAS 3 : NUMÉRO + TITRE DÉJÀ PROPRE (ex: "123 Mon Titre") -> LAISSER TEL QUEL
        elif re.match(r'^\d+[\s\-_].+', nom_sans_ext):
            match = re.match(r'^(\d+)[\s\-_]+(.*)$', nom_sans_ext)
            numero = match.group(1)
            titre_seul = match.group(2).strip()
            nouveau_titre = nom_sans_ext 

        # CAS 4 : RÉFÉRENCE + TITRE (ex: "AF123 Titre") -> NOUVEAU NUM + TITRE
        elif re.match(r'^[a-zA-Z]+\d+[a-zA-Z]*[\s\-_].+', nom_sans_ext):
            match = re.match(r'^[a-zA-Z]+\d+[a-zA-Z]*[\s\-_]+(.*)$', nom_sans_ext)
            numero = str(index_global)
            titre_seul = match.group(1).strip()
            nouveau_titre = f"{numero} {titre_seul}"

        # CAS 5 : TITRE SEUL (ou tout autre cas) -> NOUVEAU NUM + TITRE
        else:
            numero = str(index_global)
            titre_seul = nom_sans_ext
            nouveau_titre = f"{numero} {titre_seul}"

        # --- 3. MISE À JOUR ET SAUVEGARDE ---
        
        # Nettoyage final du titre (on enlève les "bis" parasites restants et ponctuation)
        titre_seul = re.sub(r'\(?\+?bis\)?', '', titre_seul, flags=re.IGNORECASE).strip()
        titre_seul = re.sub(r'^[!+?\'",;.:\s\-<]+', '', titre_seul).strip()
        
        # Recalcul du titre final si nécessaire (si le nettoyage a vidé le titre)
        if not titre_seul:
            titre_seul = extraire_meilleure_ligne(paroles)
            nouveau_titre = f"{numero} {titre_seul}"
        
        # Mise à jour du nœud <title> dans le XML
        title_node = root.find('title')
        if title_node is not None: 
            title_node.text = nouveau_titre
        else: 
            ET.SubElement(root, 'title').text = nouveau_titre

        # Nettoyage pour le nom du fichier Windows
        nom_final = re.sub(r'[\\/*?:"<>|]', "", nouveau_titre)
        
        if not os.path.exists(dossier_dest): 
            os.makedirs(dossier_dest)
            
        tree.write(os.path.join(dossier_dest, nom_final), encoding="UTF-8", xml_declaration=True)
        
        return nom_final, True, titre_seul, numero, paroles
        
    except Exception as e:
        return str(e), False, "", "", ""



def generer_index_odt(liste_chansons, dossier_dest):
    """Génère l'index puis les chants à la suite, séparés par 2 lignes."""
    if not liste_chansons:
        return
        
    chemin_fichier = os.path.join(dossier_dest, "Carnet_de_Chants.odt")
    doc = OpenDocumentText()

    # --- 1. CONFIGURATION DES STYLES ---
    
    # Style pour le titre "INDEX" et les lettres A, B, C
    style_titre_section = Style(name="StyleTitreSection", family="paragraph")
    style_titre_section.addElement(TextProperties(fontsize="22pt", fontweight="bold"))
    doc.automaticstyles.addElement(style_titre_section)

    # Style pour les lignes de l'index (Titre ........ Numéro)
    style_index_ligne = Style(name="StyleIndexLigne", family="paragraph")
    p_props_idx = ParagraphProperties()
    tabs = TabStops()
    tabs.addElement(TabStop(type="right", position="15cm", leaderstyle="dotted"))
    p_props_idx.addElement(tabs)
    style_index_ligne.addElement(p_props_idx)
    doc.automaticstyles.addElement(style_index_ligne)

    # Style pour le premier chant (pour forcer le saut de page après l'index)
    style_premier_chant = Style(name="StylePremierChant", family="paragraph")
    style_premier_chant.addElement(TextProperties(fontsize="20pt", fontweight="bold"))
    style_premier_chant.addElement(ParagraphProperties(breakbefore="page", margintop="1cm"))
    doc.automaticstyles.addElement(style_premier_chant)

    # Style pour les titres des chants suivants (sans saut de page)
    style_titre_chant = Style(name="StyleTitreChant", family="paragraph")
    style_titre_chant.addElement(TextProperties(fontsize="20pt", fontweight="bold"))
    style_titre_chant.addElement(ParagraphProperties(margintop="1cm"))
    doc.automaticstyles.addElement(style_titre_chant)

    # Style pour les paroles
    style_paroles = Style(name="StyleParoles", family="paragraph")
    style_paroles.addElement(TextProperties(fontsize="11pt", fontfamily="Arial"))
    doc.automaticstyles.addElement(style_paroles)

    # --- 2. PARTIE INDEX (Tri Alphabétique) ---
    liste_chansons.sort(key=lambda x: x[0].lower())
    
    doc.text.addElement(P(text="INDEX", stylename=style_titre_section))
    
    current_letter = ""
    for titre, num, paroles in liste_chansons:
        premiere_lettre = titre[0].upper()
        if premiere_lettre != current_letter:
            current_letter = premiere_lettre
            doc.text.addElement(P(text=current_letter, stylename=style_titre_section))
        
        p = P(stylename=style_index_ligne)
        p.addText(titre)
        p.addElement(Tab())
        p.addText(str(num))
        doc.text.addElement(p)

    # --- 3. PARTIE CHANTS (Tri Numérique) ---
    liste_chansons.sort(key=lambda x: tri_naturel(str(x[1])))

    for i, (titre, num, paroles) in enumerate(liste_chansons):
        # Pour le tout premier chant du carnet, on utilise le style avec saut de page
        style_titre = style_premier_chant if i == 0 else style_titre_chant
        
        # Titre du chant
        doc.text.addElement(P(text=f"{num} - {titre}", stylename=style_titre))
        
        # Paroles
        if paroles:
            for ligne in paroles.split('\n'):
                ligne = ligne.strip()
                if ligne.startswith('.'): continue # Ignore les accords
                doc.text.addElement(P(text=ligne, stylename=style_paroles))
        
        # Séparation : on ajoute 2 lignes vides après chaque chant
        doc.text.addElement(P(stylename=style_paroles))
        doc.text.addElement(P(stylename=style_paroles))

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
        
        # --- NOUVEAU : LA BARRE DE PROGRESSION ---
        self.progressbar = customtkinter.CTkProgressBar(self)
        self.progressbar.grid(row=4, column=0, padx=10, pady=10, sticky="ew", columnspan=2)
        self.progressbar.set(0) # On l'initialise à 0%
        
        self.switch_index_only = customtkinter.CTkSwitch(self, text="Index Only", fg_color="red", progress_color="green", command=self.switch_verify)
        self.switch_index_only.deselect()
        self.switch_index_only.grid(row=5, column=0, padx=10, pady=10, sticky="ew")
        
        self.checkbox_ajout_titre = customtkinter.CTkCheckBox(self, text="Add titles")
        self.checkbox_ajout_titre.grid(row=5, column=1, padx=10, pady=10, sticky="ew")
        self.switch_verify()
        
        
    def switch_verify(self):
        global titre_for_num
        if (self.switch_index_only.get()):
            self.checkbox_ajout_titre.configure(state="normal")
        else:
            self.checkbox_ajout_titre.deselect()
            titre_for_num = 0
            self.checkbox_ajout_titre.configure(state="disabled")
        
    
    def button_search_event(self):
        dossier = self.source.get()
        self.frame_found.clear_elements()
        self.progressbar.set(0)
        
        if os.path.exists(dossier):
            # On désactive le bouton pour éviter les clics multiples
            self.button_search.configure(state="disabled", text="Searching...")
            
            # Lancement du thread avec ta logique exacte
            thread = threading.Thread(target=self.search_worker, args=(dossier,), daemon=True)
            thread.start()
        else:
            self.frame_found.add_element("❌ Dossier introuvable", text_color="red")

    def search_worker(self, dossier):
        fichiers_trouves = []
        count = 0

        # --- RECHERCHE ET MISE À JOUR UI SIMULTANÉE ---
        for root, dirs, files in os.walk(dossier):
            # On trie les fichiers par dossier pour un affichage plus cohérent
            files.sort(key=tri_naturel) 
            
            for f in files:
                fichiers_trouves.append(f)
                count += 1
                
                # On envoie le fichier à l'interface immédiatement
                # Utiliser une capture de variable (f=f) pour éviter les erreurs de thread
                self.after(0, lambda nom=f: self.frame_found.add_element(nom))
        
        # Une fois le scan terminé, on met à jour le titre final et le bouton
        def finaliser_ui():
            self.frame_found.title_label.configure(text=f"{count} Fichiers trouvés")
            self.button_search.configure(state="normal", text="Search")

        self.after(0, finaliser_ui)
        
    def button_rename_event(self):
        """Cette fonction est appelée par le bouton. Elle lance le thread."""
        # On désactive le bouton pour éviter de cliquer 10 fois pendant le traitement
        self.button_rename.configure(state="disabled", text="Running...")
        self.progressbar.set(0)
        global titre_for_num
        titre_for_num = self.checkbox_ajout_titre.get()
        
        # On crée un "fil" (thread) qui va exécuter la fonction de traitement
        thread = threading.Thread(target=self.rename_worker)
        
        # On lance le thread en arrière-plan
        thread.start()

    def rename_worker(self):
        """C'est ici que le vrai travail se fait, sans bloquer l'interface."""
        dossier_src = self.source.get()
        dossier_dest = self.destination.get()
        
        # On utilise 'after' pour interagir avec l'UI en toute sécurité
        self.after(0, self.result_frame.clear_elements)
        
        if not os.path.exists(dossier_src) or dossier_dest == "":
            self.after(0, lambda: self.result_frame.add_element("❌ Erreur : Dossiers invalides", "red"))
            self.after(0, lambda: self.button_rename.configure(state="normal", text="Rename"))
            return

        fichiers_bruts = []
        for root, dirs, files in os.walk(dossier_src):
            for f in files:
                fichiers_bruts.append((os.path.join(root, f), f))
        
        fichiers_bruts.sort(key=lambda x: tri_naturel(x[1]))
        
        donnees_index = []
        count = 0
        size = len(fichiers_bruts)
        
        for i, (chemin, nom) in enumerate(fichiers_bruts, start=1):
            if (self.switch_index_only.get()):
                resultat, succes, titre_seul, numero, paroles = traiter_fichier_index_seulement(chemin, nom, dossier_dest, i)
            else :
                resultat, succes, titre_seul, numero, paroles = traiter_fichier_complet(chemin, nom, dossier_dest, i)
            
            # On met à jour l'interface au fur et à mesure
            if succes:
                donnees_index.append((titre_seul, numero, paroles))
                count += 1
                msg = f"✅ {nom} ➔ {resultat}"
                self.after(0, lambda m=msg: self.result_frame.add_element(m, "lightgreen"))
            else:
                msg = f"⚠️ Ignoré: {nom}"
                self.after(0, lambda m=msg: self.result_frame.add_element(m, "orange"))
                
            progress = (count / size)
            self.after(0, lambda m=msg: self.progressbar.set(progress))

        # Génération de l'ODT
        if donnees_index:
            generer_index_odt(donnees_index, dossier_dest)
            self.after(0, lambda: self.result_frame.add_element("📝 Index_Alphabétique.odt généré !", "cyan"))

        # Une fois fini, on réactive le bouton
        self.after(0, lambda: self.result_frame.title_label.configure(text=f"Résultats ({count} traités)"))
        self.after(0, lambda: self.button_rename.configure(state="normal", text="Rename"))


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("OpenSong sorter by LAO Wyatt")
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