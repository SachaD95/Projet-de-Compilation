typedef struct {
    int x;
    int y;
} Point;

typedef struct {
    Point A;
    Point B;
} Ligne;

int add(int x, int y){
    z = x + y;
    return(z);
}

int sub(int x, int y){
    z = x - y;
    return(z);
}

int mul(int x, int y){
    z = x * y;
    return(z);
}

int fact(int n){
    result = 1;

    if(n > 1){
        result = n * fact(n - 1);
    }

    return(result);
}

main(int n){



    int t[fact(3)];

    t = {10,20,30,40,50,60};

    print(len(t));
    print(t[2]);

    t[2] = 99;

    print(t[2]);





    int ligne0[3];
    int ligne1[3];

    ligne0 = {1,2,3};
    ligne1 = {4,5,6};

    int m[2];

    m[0] = ligne0;
    m[1] = ligne1;

    print(len(m));
    print(len(m[0]));

    print(m[1][2]);

    m[1][2] = 42;

    print(m[1][2]);


    Point P;

    P = Point(2,4);

    

    print(P.x);
    print(P.y);



    Point pts[2];

    pts[0] = Point(1,2);
    pts[1] = Point(7,8);

    print(pts[0].x);
    print(pts[1].y);



    Ligne L;

    L.A = Point(10,20);
    L.B = Point(30,40);

    print(L.A.x);
    print(L.B.y);



    print(
        sub(
            add(
                mul(n,n),
                fact(4)
            ),
            3
        )
    );



    for (int i = 0; i < len(t); i = i + 1) {
        print(t[i]);
    }

    return(n);
}