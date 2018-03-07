
struct rectangle {
    int x;
    int y;
};

union Data {
    int i;
    float f;
};

int main() {
    struct rectangle rect = {0,0};
    rect.x += 1;

    struct rectangle *p = &rect;
    p->y += 1;

    union Data d;
    d.i = 1;
    d.i += 1;

    union Data *dp = &d;
    dp->f += 1;

    return 0;
}
