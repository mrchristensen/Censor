
int factorial(int x) {
    if (x == 0)
        return 1;
    else {
        return x * factorial(x - 1);
    }
}

int main(int argc, char** argv) {
    if (argc < 2) {
        return 1;
    }

    int input = atoi(argv[1]);
    int output = factorial(input);
    return 0;
}
