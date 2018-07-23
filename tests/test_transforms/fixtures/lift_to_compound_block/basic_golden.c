int main()
{
  int censor01 = 1 + 3;
  int censor02 = 7 - 2;
  double censor03 = 4.5 + ((float) censor02);
  double censor04 = ((float) censor01) + censor03;
  int x = (int) censor04;
  int censor05 = 4 + 5;
  int censor06 = censor05 + 6;
  int censor07 = censor06 + 7;
  int censor08 = censor07 + 8;
  int censor09 = censor08 + 9;
  int y = censor09 + 10;
  int censor010 = x * x;
  int censor011 = y * y;
  int r2 = censor010 + censor011;
}
