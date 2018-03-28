int main()
{
  int a = 0;
  int b = 1;
  int censor01;
  if (a > b)
    censor01 = a + b;
  else
    censor01 = a - b;
  if (censor01)
    a = 1;
  int censor02;
  if ((b - a) > 2)
    censor02 = 3;
  else
    censor02 = (b - a) + 2;
  b = censor02;
  char* str1 = "string1";
  char* str2;
  char* censor03;
  if (str1[0] == 's')
    censor03 = str1;
  else
    censor03 = str2;
  str2 = censor03;
}
