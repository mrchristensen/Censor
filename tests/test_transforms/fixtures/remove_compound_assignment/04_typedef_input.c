typedef struct {
    int r;
} circle;

typedef long int uint16;

int main() {

    circle cir = {1};
    cir.r += 1;

    circle* cp = &cir;
    cp->r -= 1;

    uint16 i = 1.5;
    i += 1;


    return 0;
}
