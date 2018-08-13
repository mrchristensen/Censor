#include <stdio.h>
#include <stdlib.h>
struct one
{
    char a;
    char b;
    char c;
    char d;
};

int main()
{
  struct one* tester = (struct one*)malloc(sizeof(struct one));
  tester->a = 'a';
  tester->b = 'b';
  tester->c = 'c';
  tester->d = 0;
  char* c = (char*)tester;
  for (int i = 0; i < 3; i++)
    printf("%c",*c++);
}
