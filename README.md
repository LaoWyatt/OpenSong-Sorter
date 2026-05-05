# 🎵 OpenSong Sorter & Songbook Generator

**OpenSong Sorter** est un utilitaire desktop puissant conçu pour automatiser l'organisation des bibliothèques de chants au format XML **OpenSong**. Il nettoie les noms de fichiers, harmonise la numérotation et génère un carnet de chants complet au format `.odt` (LibreOffice/Word).

---

## ✨ Fonctionnalités Clés

### 📂 Traitement de Fichiers
*   **Renommage Intelligent** : Analyse les noms de fichiers pour corriger la ponctuation, les espaces manquants et les anciennes références.
*   **Logique "Collage"** : Détecte et répare automatiquement les numéros collés aux lettres (ex: `26bis` ➔ `26 bis`, `756Tu` ➔ `756 Tu`).
*   **Nettoyage Regex** : Supprime les mentions parasites comme `(bis)`, `+Bis`, et la ponctuation orpheline en début de titre (`<`, `!`, `'`).
*   **Fallback sur Paroles** : Si un titre est manquant, l'IA du script extrait le premier vers du refrain `[C]` ou du couplet `[V]`.

### 📝 Génération de Carnet de Chants (ODT)
*   **Index Automatique** : Crée un index alphabétique avec pagination (titre à gauche, numéros alignés à droite avec points de suite).
*   **Mise en Page Pro** : Un chant par section, titres en gras (20pt), paroles en Arial (11pt).
*   **Filtre d'Accords** : Supprime automatiquement les lignes d'accords (commençant par `.`) pour un rendu propre destiné aux chanteurs.
*   **Sauts de Page** : Sépare intelligemment l'index de la partie chants.

### 💻 Interface Graphique (GUI)
*   **Asynchrone (Multithreading)** : L'interface ne gèle jamais, même pendant le traitement de centaines de fichiers.
*   **Barre de Progression** : Suivi en temps réel de l'avancement du renommage.
*   **Mode "Index Only"** : Option pour conserver la structure existante tout en générant uniquement le carnet de chants.

---

## 🛠️ Installation

### Prérequis
*   **Python 3.10+**
*   **Bibliothèques nécessaires** :
    ```bash
    pip install customtkinter odfpy
    ```

   ---

## 📖 Guide d'Utilisation

1.  **Dossier Source** : Indiquez le dossier contenant vos fichiers XML OpenSong originaux.
2.  **Search** : Cliquez pour prévisualiser la liste des fichiers détectés.
3.  **Dossier Destination** : Indiquez où enregistrer les nouveaux fichiers et le carnet ODT.
4.  **Index Only (Option)** : Cochez cette case si vous ne voulez pas modifier vos numéros de chants actuels.
5.  **Rename** : Lancez le processus. Une fois terminé, le fichier `Carnet_de_Chants.odt` sera disponible dans votre dossier de destination.

---

## 🔍 Logique de Tri & Renommage

Le script suit cet ordre de priorité pour chaque fichier :
1.  **Numéro collé** : `25er` ➔ `25 er` | `756Tu` ➔ `756 Tu`.
2.  **Numéro seul** : `123` ➔ cherche le titre dans les paroles.
3.  **Référence Recueil** : `AF123 Titre` ➔ `[NouveauNum] Titre`.
4.  **Titre seul** : `Mon Chant` ➔ `[NouveauNum] Mon Chant`.

---

## ⚖️ Licence
Réalisé par **Laowy (LAO Wyatt)** - 2026.
Libre d'utilisation pour les églises et organisations utilisant OpenSong.