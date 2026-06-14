int tableau_global[4];

int multiplier_tableau(int coeff) {
    int resultat = 0;
    int taille = len(tableau_global);
    
    for (int i = 0; i < taille; i = i + 1) {
        tableau_global[i] = tableau_global[i] * coeff;
        resultat = resultat + tableau_global[i];
    }
    
    return (resultat);
}

main(int a, int b) {
    tableau_global = {1, 2, 3, 4};
    
    print(9999); 
    int maximum = 0;
    if (a > b) {
        maximum = a;
        print(maximum);
    }
    if (a < b) {
        maximum = b;
        print(maximum);
    }

    print(9999); 
    int compteur = 3;
    while (compteur > 0) {
        print(compteur);
        compteur = compteur - 1;
    }

    print(9999); 
    int somme_totale = multiplier_tableau(a);
    
    print(somme_totale);

    return (0);
}