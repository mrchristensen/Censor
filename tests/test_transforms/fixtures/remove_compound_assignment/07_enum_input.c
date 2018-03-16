
enum Color {
    RED,
    YELLOW = 2,
    BLUE
};

typedef enum {
    LEFT,
    RIGHT = 2,
    FORWARD,
    BACKWARD
} Direction;

int main() {
    enum Color c = RED;
    c += 1;

    Direction d = LEFT;
    d += 1;
}
