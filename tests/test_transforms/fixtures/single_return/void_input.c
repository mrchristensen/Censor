
void otherStuff() {
    return;
}

void differentOtherStuff() {
    return;
}

void doStuff(int x) {
    if (x > 1) {
        otherStuff();
        return;
    }
    else if (x < -1) {
        differentOtherStuff();
        return;
    }
    else {
        return;
    }
}
