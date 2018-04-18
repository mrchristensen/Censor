int main(int argc, char** argv) {
  int a = 1;
  int *p_int = &a;
  int b[10];
  int (*p_arr)[10] = &b;
  *p_int = a + 1;
  (*p_arr)[0] = b[0];
}
