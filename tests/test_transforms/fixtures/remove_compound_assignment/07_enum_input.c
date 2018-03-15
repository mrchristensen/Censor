
enum Color {
    RED,
    YELLOW,
    BLUE
};

typedef enum {
    LEFT,
    RIGHT,
    FORWARD,
    BACKWARD
} Direction;

int main() {
    enum Color c = RED;
    c += 1;

    Direction d = LEFT;
    d += 1;
}
