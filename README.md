# Gstion des fonctions

## 1. Ce qui a été réalisé

Ce module ajoute la gestion des fonctions au compilateur.

Fonctionnalités implémentées :

* Déclaration de fonctions.
* Paramètres de fonctions.
* Appel de fonctions.
* Appels imbriqués de fonctions.
* Récursivité.
* Variables locales simples.
* Passage des paramètres via les registres x86-64.
* Génération du code assembleur correspondant.

Exemples acceptés :

```c
int add(int x, int y){
    z = x + y;
    return(z);
}

main(int a, int b){
    return(add(a,b));
}
```

```c
int fact(int n){
    result = 1;
    if(n > 1){
        result = n * fact(n - 1);
    }
    return(result);
}

main(int n){
    return(fact(n));
}
```

---

## 2. Comment utiliser le compilateur

Écrire le programme nanoC dans le fichier :

```
source.c
```

Générer l'assembleur :

```bash
python nanoC.py
```

Le compilateur produit :

```
result.asm
```

Assembler :

```bash
nasm -f elf64 result.asm
```

Éditer les liens :

```bash
gcc -no-pie result.o
```

Exécuter :

```bash
./a.out arg1 arg2 ...
```

---

## 3. Principes d'implémentation

### 3.1 Appel de fonction

Une expression de la forme :

```c
f(a,b)
```

est reconnue par la règle :

```ebnf
expression : IDENTIFIER "(" args ")" -> appel
```

Le compilateur génère :

1. Évaluation des arguments.
2. Placement des arguments dans les registres.
3. Instruction `call`.

---

### 3.2 Passage des arguments

Convention utilisée :

| Argument | Registre |
| -------- | -------- |
| 1        | rdi      |
| 2        | rsi      |
| 3        | rdx      |
| 4        | rcx      |
| 5        | r8       |
| 6        | r9       |

---

### 3.3 Création de la pile locale

À l'entrée d'une fonction :

Une zone mémoire locale est réservée pour les paramètres et les variables locales.

---

### 3.4 Variables locales

Les variables locales sont stockées relativement à `rbp`.

Exemple :

```asm
[rbp-8]
[rbp-16]
```

Le dictionnaire `contexte` associe chaque variable à son offset dans la pile.

---

### 3.5 Valeur de retour

La valeur retournée par une fonction est placée dans :

```asm
rax
```

avant l'instruction :

```asm
ret
```

L'appelant récupère donc automatiquement le résultat dans `rax`.

---

### 3.6 Récursivité

Les appels récursifs fonctionnent car chaque appel possède sa propre pile d'activation.

---

## 4. Hypothèses et limitations

### Limitation 1 : nombre maximal de paramètres

Seuls les six premiers paramètres sont supportés :

```text
rdi
rsi
rdx
rcx
r8
r9
```

Les paramètres supplémentaires ne sont pas gérés.

---

### Limitation 2 : types

Un seul type existe :

```c
int
```

---

### Limitation 3 : variables locales

Les variables locales sont créées automatiquement lors de la première affectation.

Exemple :

```c
z = x + y;
```

Il n'est pas nécessaire d'écrire :

```c
int z;
```

---

### Limitation 4 : vérification sémantique

Le compilateur ne vérifie pas :

* l'existence préalable d'une variable ;
* les redéclarations ;
* la compatibilité des types ;
* le nombre d'arguments lors d'un appel.

---

## 5. Tests effectués

Tests validés :

* addition de deux entiers ;
* appels imbriqués ;
* plusieurs fonctions ;
* récursivité (factorielle) ;
* expressions arithmétiques utilisant des appels de fonctions.

Tous les programmes de test produisent un code assembleur valide et s'exécutent correctement.
