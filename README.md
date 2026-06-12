# README — Gestion des tableaux dans le mini compilateur

# 1. Objectif

Les fonctionnalités principales ajoutées sont :

* tableaux 1D
* tableaux 2D
* indexation
* affectation dans les tableaux
* initialisation par littéraux
* tailles dynamiques
* fonction `len(...)`
* parcours avec boucles
* génération assembleur correspondante

---

# 2. Représentation interne des tableaux

## 2.1 Convention mémoire

Chaque tableau est représenté par deux symboles mémoire :

```text
nom_len
nom_data
```

Exemple :

```c
int t[5];
```

génère :

```asm
t_len:  dq 5
t_data: times 5 dq 0
```

Convention :

* `_len` contient la taille logique
* `_data` contient les données du tableau

Cette convention est utilisée partout dans le compilateur.

---

# 3. Tableaux 1D

## 3.1 Déclaration

Syntaxe supportée :

```c
int t[5];
```

Règle de grammaire :

```python
decl : TYPE IDENTIFIER "[" expression "]" -> decl_array
```

La taille est une expression complète.

Donc :

```c
int t[3 + 2];
```

est valide.

---

# 4. Tableaux dynamiques

## 4.1 Principe

La taille d’un tableau peut être calculée dynamiquement.

Exemple :

```c
int t[x + 1];
```

ou :

```c
int t[fact(3)];
```

Le compilateur distingue :

* taille littérale
* taille calculée

---

## 4.2 Détection

Fonction utilisée :

```python
def est_entier_litteral(expr_ast)
```

Elle vérifie si la taille est directement un entier.

---

## 4.3 Cas statique

Exemple :

```c
int t[5];
```

Allocation exacte :

```asm
t_data: times 5 dq 0
```

---

## 4.4 Cas dynamique

Exemple :

```c
int t[x];
```

La taille réelle est inconnue à la compilation.

Le compilateur réserve alors :

```python
MAX_TAILLE = 1024
```

Puis :

```asm
t_data: times 1024 dq 0
```

et stocke la taille réelle dans :

```asm
t_len
```

---

# 5. Initialisation des tableaux

## 5.1 Tableaux 1D

Exemple :

```c
t = {1,2,3};
```

AST :

```python
array_literal
```

Génération ASM :

```asm
mov [rel t_data + 0], ...
mov [rel t_data + 8], ...
mov [rel t_data + 16], ...
```

Chaque case occupe 8 octets (`dq`).

---

# 6. Tableaux 2D

# 6.1 Représentation

Les tableaux 2D sont implémentés comme :

```text
tableau de pointeurs vers sous-tableaux
```

Donc :

```c
m[0]
```

contient l’adresse d’un autre tableau.

---

# 6.2 Initialisation

Exemple :

```c
m = {{1,2},{3,4}};
```

Le compilateur crée :

```asm
m_0_len
m_0_data

m_1_len
m_1_data
```

Puis :

```asm
m_data[0] = adresse de m_0_data
m_data[1] = adresse de m_1_data
```

---

# 6.3 Convention spéciale

La longueur d’un sous-tableau est stockée juste avant `_data`.

Convention :

```text
[address - 8]
```

contient la longueur.

Cette convention permet :

```c
len(m[i])
```

---

# 7. Fonction len(...)

## 7.1 Cas simple

```c
len(t)
```

génère :

```asm
mov rax, [rel t_len]
```

---

## 7.2 Cas 2D

```c
len(m[i])
```

Étapes :

1. lire l’adresse du sous-tableau
2. accéder à `[adresse - 8]`

Code ASM :

```asm
mov rax, [rax - 8]
```

---

# 8. Indexation

## 8.1 Tableau 1D

```c
t[i]
```

Calcul :

```text
adresse = base + i * 8
```

ASM :

```asm
imul rax, 8
add rax, base
```

---

# 8.2 Tableau 2D

```c
m[i][j]
```

Étapes :

1. calculer `m[i]`
2. récupérer l’adresse du sous-tableau
3. calculer `j`
4. accéder à la case


---

# 9. Affectation dans les tableaux

## 9.1 Affectation simple

```c
t[i] = x;
```

Le compilateur :

1. calcule `x`
2. calcule l’adresse de `t[i]`
3. écrit dans la mémoire

---

## 9.2 Affectation 2D

```c
m[i][j] = x;
```

Même principe avec double adressage.

---

# 10. Fonction nom_racine(...)

Fonction importante :

```python
def nom_racine(noeud)
```

Rôle :

retrouver le nom réel du tableau même dans :

```c
m[i][j]
```

Exemple :

```text
m[i][j]
→ m
```

Cette fonction est utilisée partout dans la génération ASM.

---

# 11. Convention des registres

## r12

sauvegarde temporaire de valeur.

---

# 12. Gestion des boucles

Les tableaux sont principalement utilisés avec :

```c
for (...)
```

Le compilateur génère des labels uniques grâce à :

```python
compteur = iter(range(...))
```

Exemple :

```asm
for_debut_12:
...
for_fin_12:
```

---

# 13. Pretty Printer

Le pretty printer reconstruit :

```c
t[2]
```

ou :

```c
{{1,2},{3,4}}
```

à partir de l’AST.

Il sert surtout à :

* debug
* validation du parsing
* vérification des transformations

---

# 14. Cas particuliers gérés

## 14.1 2D déguisé

Le compilateur détecte :

```c
{{1,2},{3,4}}
```

même lorsque Lark le parse comme :

```python
array_literal
```

au lieu de :

```python
array2d_literal
```

Hack utilisé :

```python
rhs.children[0].data == "array_literal"
```

---

# 15. Limitations connues

# 15.1 Pas de vérification des bornes

Exemple :

```c
t[999]
```

possible sans erreur.

---

# 15.2 Pas de vérification des tailles

Exemple :

```c
int t[2];
t = {1,2,3,4};
```

aucune erreur.

---

# 15.3 Pas de vraie allocation dynamique

Le compilateur réserve toujours :

```python
MAX_TAILLE
```

pour les tableaux dynamiques.

Il n’utilise pas :

* malloc
* heap
* free

---

# 15.4 Pas de tableaux multidimensionnels génériques

Support réel limité à :

* 1D
* 2D

Pas de :

```c
t[i][j][k]
```

---


# 15.5 Tous les tableaux contiennent des qword

Convention actuelle :

```asm
dq
```

Donc chaque case fait 8 octets.

Même pour des `int`.

---

# 16. Limitations syntaxiques

La syntaxe :

```c
int m[2][3];
```

n’est pas supportée.

Le compilateur utilise :

```c
int m[2];
```

puis :

```c
m[0] = ligne0;
```

---

