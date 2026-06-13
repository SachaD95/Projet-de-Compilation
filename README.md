# README — Gestion des structures (struct) dans le mini compilateur

## 1. Objectif

Ce module ajoute la gestion des structures (`struct`) au mini compilateur :

- Définition de structures personnalisées (`typedef struct`)
- Instanciation via constructeur
- Initialisation par copie bloc-à-bloc
- Accès aux champs simples et imbriqués (`.`)
- Affectation dans les champs (lvalues)
- Garde-fous de type et d’arité
- Génération assembleur sans pollution de la pile

---

## 2. Représentation interne des structures

### 2.1 Dictionnaires globaux

Les structures sont stockées dans :

```python
structures = {}
structures_tailles = {}
```

Exemple :

```python
structures = {
    "Point": {
        "x": {"offset": 0, "type": "int"},
        "y": {"offset": 8, "type": "int"}
    }
}

structures_tailles = {"Point": 16}
```

### Convention mémoire
- Chaque `int` occupe **8 octets**
- Les offsets sont calculés séquentiellement
- Allocation sur la pile (`rbp`)

---

## 3. Déclaration de structure

### Syntaxe

```c
typedef struct {
    int x;
    int y;
} Point;
```

### Grammaire

```
struct_def : "typedef" "struct" "{" (field_decl ";")+ "}" IDENTIFIER ";"
```

Les structures imbriquées sont supportées :

```c
typedef struct {
    Point A;
    Point B;
} Ligne;
```

---

## 4. Garde-fous (Type checking)

### Objectif

Empêcher toute corruption mémoire lors de l’initialisation.

### Exemple interdit

```c
Point P2 = Point(2, P); // erreur : type invalide
```

### Vérifications

- Nombre d’arguments
- Type de chaque champ

```python
if len(args) != len(champs):
    raise TypeError(...)
```

```python
if type_arg != type_attendu:
    raise TypeError(...)
```

---

## 5. Initialisation des structures

### 5.1 Constructeur

```c
Point P = Point(2, 4);
```

ASM généré :

```asm
mov rax, 2
push rax
mov rax, 4
push rax
pop rax
mov [rbp-24], rax
pop rax
mov [rbp-32], rax
```

---

### 5.2 Copie de structure

```c
Point P2 = P;
```

ASM :

```asm
mov rax, [rbp-32]
mov [rbp-48], rax
mov rax, [rbp-24]
mov [rbp-40], rax
```

---

## 6. Accès aux champs

```c
print(P.x);
```

ASM :

```asm
mov rax, [rbp-32]
```

Les accès imbriqués sont résolus récursivement.

---

## 7. Affectation dans les champs

```c
P.x = 10;
```

ASM :

```asm
mov rax, 10
mov [rbp-32], rax
```

Étapes :
- Calcul de l’offset
- Vérification de type
- Émission du code

---

## 8. Fonction utilitaire `fmt_offset`

```python
fmt_offset(offset)
```

Formats :

- `-8 → [rbp-8]`
- `+16 → [rbp+16]`
- `0 → [rbp]`

---

## 9. Convention des registres

- `rax` : registre de travail principal
- `rbp` : base de la stack frame

---

## 10. Pretty printer

Reconstruction du code source :

- Structures
- Accès champs
- Constructeurs

---

## 11. Limitations

### 11.1 Pas d’opérations entre structures
```c
Point P3 = P1 + P2; // interdit
```

### 11.2 Alignement fixe
- Tous les champs = 8 octets
- Aucun packing

### 11.3 Pas de heap
- Allocation uniquement sur la stack
- Pas de pointeurs de structures
