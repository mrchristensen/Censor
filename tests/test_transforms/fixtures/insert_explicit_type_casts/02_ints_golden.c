int main()
{
  char a = (char) 0;
  short b = (short) 0;
  int c = 0;
  unsigned char d = (unsigned char) 0;
  unsigned short f = (unsigned short) 0;
  unsigned int g = (unsigned int) 0;
  long int h = (long int) 0;
  unsigned long int i = (unsigned long int) 0;
  long long int j = (long long int) 0;
  unsigned long long int k = (unsigned long long int) 0;
  a = (char) (b + c);
  b = (short) (((int) a) + c);
  c = (int) (b + ((short) a));
  a = a + a;
  a = (char) ((((short) a) + b) + (c + ((int) a)));
  a = (char) (((unsigned short) a) + f);
  a = (char) (((unsigned long long int) (((long long int) (((unsigned long int) (((long int) ((((unsigned short) ((b + c) + ((short) d))) + f) + g)) + h)) + i)) + j)) + k);
}
