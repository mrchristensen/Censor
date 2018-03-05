int main()
{
  int a = 0;
  {
    int *censor01 = &a;
    *censor01 = (*censor01) + 1;
  }

  int arr[8] = {1, 2, 3, 4, 5, 6};
  {
    int *censor02 = &arr[1];
    *censor02 = (*censor02) + 1;
  }

  int *p = arr;
  {
    int **censor03 = &p;
    *censor03 = (*censor03) + 1;
  }
  {
    int *censor04 = &(*p);
    *censor04 = (*censor04) + 1;
  }
  int **p2 = arr;
  {
    int *censor05 = &(*(*p2));
    *censor05 = (*censor05) + 1;
  }
  {
    int *censor06 = &(*(&a));
    *censor06 = (*censor06) + 1;
  }

  {
    int *censor07 = &(*(p + 3));
    *censor07 = (*censor07) + 1;
  }
  long int b;
  {
    long int *censor08 = &b;
    *censor08 = (*censor08) + 1;
  }
  {
    int *censor09 = &(*(p + b));
    *censor09 = (*censor09) + 1;
  }

}
