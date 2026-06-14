# Projet-de-Compilation

## Fonctionnalités

### Structures (`typedef struct`)

* Définition de structures contenant des types primitifs ou d'autres structures.
* Structures contenant des tableaux.
* Accès aux membres avec l'opérateur `.`.
* Affectation directe entre structures.
* Copie complète du contenu d'une structure lors des affectations et des retours de fonction.

Exemple :

```c
typedef struct {
    int id;
    int scores[5];
} Joueur;
```

### Tableaux

* Tableaux à une dimension.
* Tableaux à deux dimensions.
* Initialisation par liste de valeurs.
* Fonction native `len()` permettant de récupérer la taille d'un tableau à la compilation.
* Tableaux de structures.
* Tableaux de pointeurs de fonctions.

Exemples :

```c
int valeurs[10];
int matrice[5][5];
int t[3] = {1, 2, 3};
```

### Fonctions

* Fonctions avec plusieurs paramètres.
* Retour de valeurs entières.
* Retour de structures complètes.
* Respect de la convention d'appel x86_64 System V ABI (`rdi`, `rsi`, `rdx`, `rcx`, `r8`, `r9`).
* Appels indirects via une adresse calculée.

Exemple :

```c
tableau_fonctions[0](42);
```

### Structures de contrôle

* Instructions `if`.
* Boucles `while`.
* Boucles `for`.
* Affichage d'entiers avec `print()`.

Exemple :

```c
for (int i = 0; i < 10; i = i + 1) {
    print(i);
}
```

---

## Exemples d'utilisation

### Structure contenant un tableau de fonctions

```c
typedef struct {
    int id;
    int actions[3];
} Robot;

int avancer(int vitesse) {
    print(vitesse);
    return(1);
}

main() {
    Robot r1;

    r1.id = 7;
    r1.actions[0] = avancer;

    r1.actions[0](100);

    return(0);
}
```

### Tableau de structures

```c
typedef struct {
    int id;
    int notes[3];
} Eleve;

main() {
    Eleve classe[30];

    classe[0].id = 101;
    classe[0].notes[2] = 18;

    print(classe[0].notes[2]);

    return(0);
}
```

### Retour d'une structure par une fonction

```c
typedef struct {
    int position[2];
} Point;

Point creer_point(int x, int y) {
    Point p;

    p.position[0] = x;
    p.position[1] = y;

    return(p);
}

main() {
    Point joueur;

    joueur = creer_point(5, 12);

    print(joueur.position[1]);

    return(0);
}
```

---

## Installation

### Dépendances

Le projet utilise la bibliothèque Python Lark pour l'analyse syntaxique :

```bash
pip install lark
```

### Organisation des fichiers

Le compilateur attend la présence d'un fichier source nommé `test.c` dans le même répertoire que le script Python.

```text
MonProjet/
├── compiler_v2.py
└── test.c
```

---

## Compilation

Lancer le compilateur :

```bash
python compiler_v2.py
```

Cette commande génère un fichier assembleur nommé :

```text
Result.asm
```

Assembler et lier le programme sous Linux :

```bash
nasm -f elf64 Result.asm -o Result.o
gcc -no-pie Result.o -o programme
```

Exécuter le programme :

```bash
./programme
```

---

## État du projet

Le compilateur prend actuellement en charge :

* les variables entières ;
* les structures imbriquées ;
* les tableaux 1D et 2D ;
* les tableaux de structures ;
* les tableaux de fonctions ;
* les appels indirects ;
* les retours de structures ;
* les instructions `if`, `while` et `for` ;
* la génération de code NASM x86_64.

Le projet reste expérimental et sert principalement de démonstrateur autour de la génération de code, de la gestion mémoire et de l'orthogonalité des types.
