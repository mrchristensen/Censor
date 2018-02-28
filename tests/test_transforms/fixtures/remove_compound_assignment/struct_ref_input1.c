
struct rectangle {
    int x;
    int y;
};

typedef struct {
    int r;
} circle;

int main() {
    struct rectangle rect = {0,0};
    rect.x += 1;

    circle cir = {1};
    cir.r += 1;

    circle* cp = &cir;
    cp->r -= 1;

    return 0;
}
