# Integration des fonctions et tableaux en asm

## 1. Fonctionnalités implémentées
Ce compilateur gère :

* **Structures de contrôle :** `if`, `while` et `for`.
* **Tableaux :** Gestion de tableaux unidimensionnels et bidimensionnels avec initialisation par littéraux.
* **Gestion mémoire :** Allocation locale sur la pile (stack) via `rbp` et support des variables globales.
* **Fonctions :** Définition, passage d'arguments (jusqu'à 6 registres), retour de valeur et récursivité.
* **Entrées/Sorties :** Support des arguments via la ligne de commande et affichage via `print()`.

## 2. Utilisation
1. Écrire le code dans `AsmIntegrationTest.c`.
2. Générer l'assembleur : `python nanoC.py`
3. Compiler : 
   nasm -f elf64 result.asm 
   gcc -no-pie result.o 
4. Exécuter : ./a.out arg1 arg2

## 3. Limites conues

* **Types :** Seul le type int est supporté.

* **Structures :** La grammaire est présente, mais l'accès aux champs n'est pas généré en assembleur.

* **Logique conditionnelle :** Pas de else  et pas d'opérateurs booléens (&&, ||).
  
* **Variables :** Pas de vérification sémantique (redéclaration, portée, ou type).

* **Return :** Le return doit obligatoirement être la toute dernière instruction de la fonction.
  
* **Fonctions :** Les paramètres sont limités aux 6 premiers registres (rdi, rsi, rdx, rcx, r8, r9).
