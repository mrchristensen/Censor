
int main() {
    char a = 0;
    short b = 0;
    int c = 0;
    unsigned char d = 0;
    unsigned short f = 0;
    unsigned int g = 0;
    long int h = 0;
    unsigned long int i = 0;
    long long int j = 0;
    unsigned long long int k = 0;


    a = b + c;
    b = a + c;
    c = b + a;

    a = a + a;
    a = (a + b) + (c + a);
    a = a + f;

    a = b + c + d + f + g + h + i + j + k;

}