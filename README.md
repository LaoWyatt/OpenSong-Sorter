# 🎵 OpenSong Sorter

**OpenSong Sorter** est une application desktop moderne développée en Python, conçue pour automatiser l'organisation, le renommage et la génération de carnets de chants à partir de fichiers XML **OpenSong**.

L'outil nettoie les titres, réattribue une numérotation propre et génère automatiquement un fichier ODT (LibreOffice/Word) contenant un index alphabétique suivi de l'intégralité des paroles.

---

## ✨ Fonctionnalités

*   **🔍 Recherche Multithread** : Scannez vos dossiers sans jamais faire geler l'interface graphique.
*   **🧹 Nettoyage Intelligent** : 
    *   Supprime automatiquement les mentions parasites comme `(bis)`, `(Bis)` ou `+Bis`.
    *   Nettoie la ponctuation orpheline en début de titre (`!`, `'`, `<`, etc.).
    *   Si un titre est manquant ou mal nommé, l'algorithme cherche la meilleure ligne dans les paroles (Refrain `[C]` ou Couplet `[V]`).
*   **🔢 Renommage Automatique** : Applique une numérotation séquentielle propre basée sur un tri naturel (1, 2, 10 au lieu de 1, 10, 2).
*   **📝 Génération de Carnet de Chants (ODT)** :
    *   **Index Alphabétique** : Généré au début avec numéros alignés à droite via des tabulations à points.
    *   **Saut de page** : Un saut de page automatique sépare l'index du premier chant.
    *   **Mise en page** : Titres de chants en grande police (taille 20), paroles en Arial 11, et deux lignes vides entre chaque chant.
    *   **Filtre d'accords** : Ignore automatiquement les lignes commençant par un point (`.`) pour un carnet de texte propre.
*   **💻 Interface Moderne** : Développée avec `CustomTkinter` pour un look "Dark Mode" élégant avec barre de progression.

---

## 🚀 Installation

### Prérequis
*   Python 3.10 ou plus récent.
*   Bibliothèques nécessaires :
    ```bash
    pip install customtkinter odfpy
    ```

    ---

## 🛠️ Utilisation

1.  **Dossier Source** : Entrez le chemin du dossier contenant vos fichiers XML OpenSong originaux.
2.  **Search** : Cliquez pour lister les fichiers et vérifier que le dossier est bien lu.
3.  **Dossier Destination** : Entrez le chemin où vous souhaitez enregistrer les nouveaux fichiers.
4.  **Rename** : Lance le processus. La barre de progression indique l'avancée.
5.  **Résultat** : 
    *   Les fichiers XML renommés sont créés dans la destination.
    *   Le fichier `Carnet_de_Chants.odt` est généré au même endroit.

---

## 📂 Structure du Projet

*   `traiter_fichier()` : Coeur de la logique (Parsing XML, nettoyage regex, sauvegarde).
*   `extraire_meilleure_ligne()` : Analyse sémantique des paroles pour trouver un titre de secours.
*   `generer_index_odt()` : Création du document texte avec gestion des styles et sauts de page.
*   `App` / `MyFrame` : Architecture GUI asynchrone pour une expérience fluide.

---

## 📝 Licence
Projet créé par **Laowy** (Wyatt) - 2026.
Libre d'utilisation et de modification pour les besoins des communautés et églises utilisant OpenSong.