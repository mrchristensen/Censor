
struct tnode
{
  int data[10];
  struct tnode *c[10];
};
int main()
{

  struct tnode r = {{0,1,2,3,4,5,6,7,8,9}, {}};
  struct tnode s = {{0,1,2,3,4,5,6,7,8,9}, {}};
  r.c[0] = &s;

  int i = 0;
  int d = r.c[i++]->data[i];
}