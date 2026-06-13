typedef struct {
    int x;
    int y;
} Point;

typedef struct {
    Point A;
    Point B;
} Ligne;

main(int n) {
    Point P = Point(2, 4);
    Point P2 = P;
    print(P.x);
    return(0);
}