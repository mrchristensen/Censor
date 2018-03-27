int main() {
    int i = 0;
    if (true) {
        i = 10;
        if (true) {
            i = 20;
        } else {
            i = 30;
        }
    }
    return 0;
}
