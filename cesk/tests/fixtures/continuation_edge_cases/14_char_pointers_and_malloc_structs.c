#include <stdio.h>
#include <stdlib.h>
struct one{
    int a;
    char b;
    char c;
    char d;
};

int main(){
  int i = 97;
  char ch = i;
  printf("%c\n",ch);
  int * x = 0;
  long * y = 0;
  char * c = 0;
  x++;y++;c++;
  printf("%ld\n",(long) x);
  printf("%ld\n",(long) y);
  printf("%ld\n",(long) c);

  struct one* tester = (struct one*)malloc(sizeof(struct one));
  tester->a = 0x64636261;
  tester->b = 'e';
  tester->c = 'f';
  tester->d = 0;
  c = (char*)tester;
  c += 3;
  for (int i = 0; i < 3; i++,c++){
      printf("%c",(char)*(c));
  }
}
