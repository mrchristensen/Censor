typedef struct
{
  int r;
} circle;
typedef long int uint16;
int main()
{
  circle cir = {1};
  {
    int *censor01 = &cir.r;
    *censor01 = (*censor01) + 1;
  }
  circle *cp = &cir;
  {
    int *censor02 = &cp->r;
    *censor02 = (*censor02) - 1;
  }
  uint16 i = 1.5;
  {
    uint16 *censor03 = &i;
    *censor03 = (*censor03) + 1;
  }



  return 0;
}

