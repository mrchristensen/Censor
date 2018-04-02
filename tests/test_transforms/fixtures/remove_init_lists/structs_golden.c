struct rect
{
  int x;
  int y;
};
struct rect r;
void censor01_INIT_GLOBALS();
int main()
{
  censor01_INIT_GLOBALS();
  struct rect s;
  s.x = 7;
  s.y = 8;
}

void censor01_INIT_GLOBALS()
{
  r.x = 4;
  r.y = 5;
}
