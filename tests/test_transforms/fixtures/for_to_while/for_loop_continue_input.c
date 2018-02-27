int main() {
    int j = 0;
    for (int i = 0; i < 10; i++) {
        if (i % 2 == 0)
            continue;
        j++;
        continue;
        j--;
    }
}
