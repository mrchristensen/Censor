
typedef struct
{
  int x;
  long int y;
} rectangle;

typedef struct {
    float side1;
    double side2;
    double side3;
} triangle;

double diag(rectangle r) {
    double d = r.x * r.x + r.y*r.y;
    return sqrt(d);
}

double sqrt(double x) {
    int i = 0;

    double v = 0;
    double n = 0;
    int grenze = 12;
    double z = 10;

    for(i = 1; i < grenze + 1; i++){
        z = z * 0.1;

        while(v * v < x){
            v = v + z;
            if(v * v < x){
                n = v;
            }
        }
        v = n;
    }
    return n;
}

int main() {
    rectangle r;
    r.x = 3;
    r.y = 5;

    triangle t;
    t.side1 = r.x;
    t.side2 = r.y;
    t.side3 = diag(r);
    return 0;
}
