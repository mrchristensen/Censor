
int main() {
    float a = 0;
    double b = 0;
    long double c = 0;

    a = b + c;
    b = a + c;
    c = b + a;

    a = a + a;

    a = (a + b) + (c + a);

    int i;
    i = i + a;
    i = b + i;
    i = i + c;

}