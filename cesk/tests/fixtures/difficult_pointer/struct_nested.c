#include <stdio.h>
#include <stdlib.h>
struct one{
    int a;
    char b;
    char c;
    char d;
    char e;
};

struct two{
    int i;
    struct one a;
    char b;
    char c;
    char d;
    char e;
};

int main()
{
  struct two* tester = (struct two*)malloc(sizeof(struct two));
  struct one onee;
  onee.a = 0x68676665;
  onee.b = 'i';
  onee.c = 'j';
  onee.d = 'k';
  onee.e = 'l';
  tester->a = onee;
  tester->i = 0x64636261;
  tester->b = 'm';
  tester->c = 'n';
  tester->d = 'o';
  tester->e = 'p';
  char* c = (char*)tester;
  for (int i = 0; i < 16; i++){
      printf("%c",*c++);
  }
  printf("\n");
}