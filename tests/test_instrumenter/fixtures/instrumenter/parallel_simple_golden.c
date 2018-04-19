void yeti_log_heap_access(char* mode, void* var, int thread_num)
{
  printf("%s, %p, %d\n", mode, var, thread_num);
}

void yeti_log_omp(char* action, char* construct, int thread_num)
{
  printf("%s, %s, %d\n", action, construct, thread_num);
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
    yeti_log_omp("enter", "parallel", omp_get_thread_num());
    x();
    yeti_log_omp("exit", "parallel", omp_get_thread_num());
  }
}
