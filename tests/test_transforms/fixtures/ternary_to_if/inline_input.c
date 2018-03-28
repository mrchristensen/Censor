int main() {
  int a = 0;
  int b = 1;
  if ((a > b ? a + b : a - b))
    a = 1;
  b = (b - a) > 2 ? 3 : b - a + 2;
  char* str1 = "string1";
  char* str2;
  str2 = str1[0] == 's' ? str1 : str2;
}
