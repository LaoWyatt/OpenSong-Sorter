# 🎵 OpenSong Sorter & Songbook Generator

**OpenSong Sorter** est un utilitaire desktop puissant conçu pour automatiser l'organisation, le nettoyage et l'exportation de bibliothèques de chants au format XML **OpenSong**. 

L'outil permet de transformer une collection de fichiers XML souvent mal nommés en une bibliothèque ordonnée et de générer automatiquement un carnet de chants professionnel au format `.odt` (compatible LibreOffice et Microsoft Word).

---

## ✨ Fonctionnalités Clés

### 📂 Traitement et Renommage Intelligent
*   **Nettoyage Automatique** : Supprime les caractères parasites au début des titres (`!`, `'`, `?`, `<`) et les mentions répétitives comme `(bis)` ou `+Bis`.
*   **Correction de la Numérotation** : Détecte et répare les numéros collés aux lettres (ex: `26bis` ➔ `26 bis`, `756Tu` ➔ `756 Tu`).
*   **Extraction de Titre par IA (Fallback)** : Si un fichier n'a pas de titre ou seulement un numéro, le script analyse le XML pour extraire la première ligne du refrain `[C]` ou du couplet `[V]`.
*   **Tri Naturel** : Classe les fichiers de manière humaine (1, 2, 10) plutôt que purement alphabétique (1, 10, 2).

### 📝 Génération de Carnet de Chants (ODT)
*   **Index Alphabétique** : Crée automatiquement un index avec des points de suite et une pagination alignée à droite.
*   **Mise en Page Pro** : Applique des styles de texte optimisés (Titres en 20pt gras, Paroles en Arial 11pt).
*   **Nettoyage des Accords** : Pour le carnet de chants, le script filtre les lignes d'accords (commençant par `.`) pour ne garder que le texte.
*   **Sauts de Page** : L'index est automatiquement séparé de la partie chants par un saut de page.

### 💻 Interface Moderne (GUI)
*   **Multi-threading** : Le traitement s'exécute en arrière-plan. L'interface reste fluide et ne "gèle" jamais.
*   **Suivi en Temps Réel** : Une barre de progression et une console de résultats affichent l'état d'avancement de chaque fichier.
*   **Mode "Index Only"** : Une option pour générer le carnet sans modifier vos numéros de fichiers originaux.

---

## 🛠️ Installation

### Prérequis
*   **Python 3.10+**
*   **Bibliothèques requises** :
    ```bash
    pip install customtkinter odfpy
    ```

---

## 📖 Guide d'Utilisation

1.  **Source** : Indiquez le dossier contenant vos fichiers OpenSong originaux.
2.  **Search** : Cliquez pour prévisualiser la liste des fichiers.
3.  **Destination** : Choisissez le dossier où seront créés les nouveaux fichiers et le carnet ODT.
4.  **Options** : 
    *   Cochez **Index Only** pour garder votre numérotation actuelle.
    *   Cochez **Add Titles** si vous voulez que le script trouve un titre aux fichiers qui n'ont qu'un numéro.
5.  **Rename** : Lancez l'automatisation. Le fichier `Carnet_de_Chants.odt` apparaîtra dans votre dossier de destination à la fin du processus.

---

## 🔍 Logique de Renommage (Ordre de priorité)

Le script analyse le nom du fichier selon ces étapes :
1.  **Cas "Collé"** : `25bis` ➔ `25 bis`.
2.  **Cas "Numéro Seul"** : `123` ➔ Cherche le titre dans le texte du chant.
3.  **Cas "Référence"** : `AF123 Mon Titre` ➔ `[NouveauNum] Mon Titre`.
4.  **Cas "Titre Seul"** : `Mon Chant` ➔ `[NouveauNum] Mon Chant`.

---

## 👤 Auteur
Développé par **Laowy (LAO Wyatt)** — 2026.  
*Outil dédié à la simplification de la gestion liturgique et musicale.*