typedef struct
{
  int x;
  int y;
} rectangle;
rectangle mkRect(int x, int y)
{
  rectangle censor02;
  rectangle r = {x, y};

    censor02 = r;
    goto censor01;

  censor01:
  return censor02;

}

int floor_double(float x)
{
  int censor04;

    censor04 = x * 2;
    goto censor03;

  censor03:
  return censor04;

}

int main()
{
  int censor06;
  rectangle r = mkRect(3, 5);
  int i = floor_double(3.9);

    censor06 = 0;
    goto censor05;

  censor05:
  return censor06;

}
