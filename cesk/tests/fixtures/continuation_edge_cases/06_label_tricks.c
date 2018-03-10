int main() {
    int i = 2;
    if (i == 2) {
        label: 
        i = 0;
    }
    else {
        label:
        i = 1;
    }
    goto label;
    return i;
}
