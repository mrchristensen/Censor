int main() {
  int j = 0;
  for (int i = 0; i < 10; i++) {
    while (j < 10) {
      j++;
      if (j % 2 == 0)
        continue;
      j++;
    }
    j = 0;
  }
}
