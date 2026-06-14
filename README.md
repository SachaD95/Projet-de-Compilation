# Pretty Printer - Intégration des Fonctions, Tableaux et Structures.


## Fonctionnalités Intégrées

Le script est capable d'analyser un code source (via un mini-langage de style C) et de le régénérer proprement selon les règles de syntaxe suivantes :

1. **Gestion des Fonctions** : 
   * Définition de fonctions avec paramètres typés (`pp_fonction`).
   * Gestion de la fonction principale `main`.
   * Appels de fonctions récursives ou imbriquées (ex: `fact(n - 1)`).
2. **Gestion des Tableaux & Matrices** :
   * Déclarations de tableaux scalaires et littéraux de tableaux (`{10, 20, 30}`).
   * Tableaux à deux dimensions (matrices) et accès par double indice (`m[1][2]`).
   * Utilisation de la fonction native `len(t)` pour récupérer la taille.
3. **Gestion des Structures (Enregistrements)** :
   * Définition de structures complexes via `typedef struct { ... } Nom;`.
   * Accès aux champs imbriqués via la notation pointée (ex: `L.A.x`).
   * Instanciation via des constructeurs de structures.

---

## Architecture du Code

Le fichier principal est structuré en deux parties majeures :

* **La Grammaire Lark (`grammaire`)** : Définit les règles syntaxiques (expressions, *lvalues*, commandes, déclarations, fonctions et structures) et résout les ambiguïtés d'analyse.
* **Le Pretty Printer (`pp_...`)** : Un ensemble de fonctions récursives qui parcourent l'Arbre de Syntaxe Abstraite (AST) généré par Lark pour reconstruire une chaîne de caractères parfaitement formatée et lisible.

