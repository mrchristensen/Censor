enum vals
{
  here,
  there,
  anywhere
};
int main()
{
  enum vals place;
  place = here;
  {
    int here_0 = 30;
    enum vals place_0 = here_0;
    printf("%d\n",place_0);
  }
  printf("%d\n",place);
}
