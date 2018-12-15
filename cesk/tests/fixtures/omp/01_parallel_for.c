#include <omp.h>
#include <stdio.h>

int main() {
  int a[10];
#pragma omp parallel for
  for (int i = 0; i < 10; i = i + 1)
    a[i] = i;
  for (int i = 0; i < 10; i++)
    printf("%d\n", a[i]);
}
