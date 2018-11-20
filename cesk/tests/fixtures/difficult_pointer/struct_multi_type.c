#include <stdio.h>
#include <stdlib.h>
struct one{
    int a;
    char b;
    char c;
    char d;
};

int main()
{
  struct one* tester = (struct one*)malloc(sizeof(struct one));
  tester->a = 0x64636261;
  tester->b = 'e';
  tester->c = 'f';
  tester->d = 0;
  char* c = (char*)tester;
  c += 3;
  for (int i = 0; i < 3; i++,c++){
      printf("%c",(char)*(c));
  }
}
