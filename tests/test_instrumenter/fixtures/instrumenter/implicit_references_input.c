int main(int argc, char** argv) {
  int a = 0;
  int sum = 0;
  int values[10];
#pragma omp parallel for firstprivate(values) lastprivate(a) schedule(static, 1) reduction(+:sum)
  for (int i = 0; i < 10; i++) {
    a++;
    sum = sum + values[i];
  }
}
