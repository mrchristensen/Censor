struct rectangle {
    int x;
    int y;
};

typedef struct rectangle rectangle;

union Data {
    int i;
    float f;
};

int main() {
    rectangle r = {0,0};
    r.x += 1;

    struct rectangle *p = &r;
    p->y += 1;

    union Data d;
    d.i = 1;
    d.i += 1;

    union Data *dp = &d;
    dp->f += 1;

    return 0;
}
