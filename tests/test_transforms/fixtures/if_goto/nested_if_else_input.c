int main() {
    int i = 0;
    if (true) {
        i = 10;
        if (true) {
            i = 20;
        } else {
            i = 30;
        }
    } else {
        i = 40;
        if (true) {
            i = 50;
        } else {
            i = 60;
        }
    }
    return 0;
}
