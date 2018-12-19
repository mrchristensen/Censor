#include <omp.h>
#include <stdio.h>

int main() {
  int a = 0;
#pragma omp parallel for
  for (int i = 0; i < 10; i = i + 1)
#pragma omp critical
    a += i;
  printf("%d\n", a);
}
