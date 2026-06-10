int add(int x, int y){
    z = x+y;
    return(z);
}

int sub(int x, int y){
    z = x-y;
    return(z);
}

int mul(int x, int y){
    z = x*y;
    return(z);
}

int fact(int n){
    result = 1;
    if(n > 1){
        result = n * fact(n - 1);
    }
    return(result);
}


main(int a, int b){
    return(sub(add(mul(a, a), mul(b, b)),fact(a)));
}