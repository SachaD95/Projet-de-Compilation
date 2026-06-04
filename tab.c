main(int n) {
    int t[5];
    int ligne0[3];
    int ligne1[3];
    int m[2];
    int x;
    int y;
    t = {10, 20, 30, 40, 50};
    print(len(t));
    print(t[2]);
    t[2] = 99;
    print(t[2]);
    x=t[0];
    print(x);
    ligne0 = {1, 2, 3};
    ligne1 = {4, 5, 6};
    m[0] = ligne0;
    m[1] = ligne1;

    print(len(m));
    print(len(m[0]));
    print(m[1][2]);
    m[1][2] = 42;
    print(m[1][2]);
    y=m[1][2];
    print(y);

    for (int k = 0; k < len(t); k = k + 1) {
        print(t[k]);
    }
    for (int i = 0; i < len(m); i = i + 1) {
        for (int j = 0; j < len(m[i]); j = j + 1) {
            print(m[i][j]);
        }
    }
    return (n);

}

