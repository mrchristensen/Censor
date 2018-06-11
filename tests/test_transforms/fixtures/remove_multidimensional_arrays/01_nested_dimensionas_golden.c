int main()
{
  int censor01 = 5 * 6;
  int censor02 = 3 * 4;
  int (*(*arr)[censor02])[censor01];
  *((*((*((*(arr + 0)) + ((4 * 1) + 2))) + 3)) + ((6 * 4) + 5));
  *((*(arr + 1)) + ((4 * 2) + 3));
  (*(arr + 1)) + ((4 * 2) + 3);
  (*(arr + 1)) + (2 * 4);
  (*(arr + 1)) + (2 * 4); 
  return 0;
}
