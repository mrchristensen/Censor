void yeti_log_memory_access(char *mode, void *var)
{
  int thread_num = omp_get_thread_num();
  int ancestor_num = omp_get_ancestor_thread_num(omp_get_level()-1);
  printf("%s, %p, %d, %d\n", mode, var, thread_num, ancestor_num);
}

void yeti_log_omp(char *action, char *construct)
{
  int thread_num = omp_get_thread_num();
  int ancestor_num = omp_get_ancestor_thread_num(omp_get_level()-1);
  printf("%s, %s, %d, %d\n", action, construct, thread_num, ancestor_num);
}

#pragma BEGIN #include<omp.h>
#pragma END
void x()
{
}

int main()
{
  #pragma omp parallel
  {
    yeti_log_omp("enter", "parallel");
    x();
    yeti_log_omp("exit", "parallel");
  }
}
