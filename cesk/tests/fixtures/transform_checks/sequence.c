#include <stdio.h>

int f() {
  char c = 'f';
  printf("%c\n", c);
  return 0;
}

int g(){
  char c = 'g';
  printf("%c\n", c);
  return 1;
}

int show(int a, int b){
  printf("%d\n",a);
  printf("%d\n",b);
  return 1;
}

int x(){
  char c = 'x';
  printf("%c\n", c);
  return 1;
}

int big_test(){
  int a = 2;
  int b = 3;
  int c = 7;
  a = ((g() + b) && f()?a:g())?(g(),show(3,f())):(f(),f(),f());
  return a;
}

int main() {
  printf("%d\n",big_test());
  f();
  x();
  g();
  int a;
  a = f() && f();
  x();
  a = g() && g();
  x();
  a = g() && f();
  x();
  a = f() && g();
  x();
  a = f() || f();
  x();
  a = g() || g();
  x();
  a = g() || f();
  x();
  a = f() || g();
  x();
  a = g()?g():f();
  x();
  a = g()?f():g();
  x();
  a = (g(),f(),f(),f(),g());
  x();
  g(),f(),g(),f(),g();
  printf("%d\n",1 && 1);
  printf("%d\n",0 && 1);
  printf("%d\n",1 && 0);
  printf("%d\n",0 && 0);
  printf("%d\n",1 || 1);
  printf("%d\n",0 || 1);
  printf("%d\n",1 || 0);
  printf("%d\n",0 || 0);
  printf("%d\n",1?2:3);
  printf("%d\n",0?2:3);
  show(f() + 2,(1,2,3,a = 80,a+4));
  show(1,g());
  return 0;
}
