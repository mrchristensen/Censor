#pragma BEGIN #include<omp.h>

int main(int argc, char** argv) {
  int sum = 0;
#pragma omp parallel num_threads(2)
  {
    int i;
#pragma omp for reduction(+:sum) schedule(static, 50)
    for (i = 0; i < 100; i++)
    {
      sum = sum + i;
    }
  }
}
