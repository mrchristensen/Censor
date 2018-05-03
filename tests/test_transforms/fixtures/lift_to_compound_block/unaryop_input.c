int main() {
  int a[5];
  int i = 0;
  i = i++;
 LOOP:
  {
    a[i++] = 0;
    if (i < 4)
      goto LOOP;
  }
}
