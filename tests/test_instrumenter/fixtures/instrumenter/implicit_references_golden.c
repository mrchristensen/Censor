void yeti_log_memory_access(char* mode, void* var, int thread_num)
{
  printf("%s, %p, %d\n", mode, var, thread_num);
}

void yeti_log_omp(char* action, char* construct, int thread_num)
{
  printf("%s, %s, %d\n", action, construct, thread_num);
}

#pragma BEGIN #include<omp.h>
#pragma END
int main(int argc, char** argv)
{
  int a = 0;
  int sum = 0;
  int values[10];
  int i;
  #pragma omp parallel
  {
    yeti_log_omp("enter", "parallel", omp_get_thread_num());
    yeti_log_memory_access("clause read", &values, omp_get_thread_num());
    yeti_log_memory_access("clause read", &values[0], omp_get_thread_num());
    yeti_log_memory_access("clause read", &values, omp_get_thread_num());
    yeti_log_memory_access("clause read", &values[1], omp_get_thread_num());
    yeti_log_memory_access("clause read", &values, omp_get_thread_num());
    yeti_log_memory_access("clause read", &values[2], omp_get_thread_num());
    yeti_log_memory_access("clause read", &values, omp_get_thread_num());
    yeti_log_memory_access("clause read", &values[3], omp_get_thread_num());
    yeti_log_memory_access("clause read", &values, omp_get_thread_num());
    yeti_log_memory_access("clause read", &values[4], omp_get_thread_num());
    yeti_log_memory_access("clause read", &values, omp_get_thread_num());
    yeti_log_memory_access("clause read", &values[5], omp_get_thread_num());
    yeti_log_memory_access("clause read", &values, omp_get_thread_num());
    yeti_log_memory_access("clause read", &values[6], omp_get_thread_num());
    yeti_log_memory_access("clause read", &values, omp_get_thread_num());
    yeti_log_memory_access("clause read", &values[7], omp_get_thread_num());
    yeti_log_memory_access("clause read", &values, omp_get_thread_num());
    yeti_log_memory_access("clause read", &values[8], omp_get_thread_num());
    yeti_log_memory_access("clause read", &values, omp_get_thread_num());
    yeti_log_memory_access("clause read", &values[9], omp_get_thread_num());
    yeti_log_memory_access("clause read", &sum, omp_get_thread_num());
    yeti_log_omp("enter", "for", omp_get_thread_num());
    yeti_log_memory_access("read", &i, omp_get_thread_num());
#pragma omp for firstprivate(values) lastprivate(a) schedule(static, 1) reduction(+:sum)
    for (i = 0; i < 10; i++)
    {
      yeti_log_memory_access("write", &a, omp_get_thread_num());
      a++;
      yeti_log_memory_access("read", &values, omp_get_thread_num());
      yeti_log_memory_access("read", &i, omp_get_thread_num());
      yeti_log_memory_access("read", &values[i], omp_get_thread_num());
      yeti_log_memory_access("read", &sum, omp_get_thread_num());
      yeti_log_memory_access("write", &sum, omp_get_thread_num());
      sum = sum + values[i];
      yeti_log_memory_access("write", &i, omp_get_thread_num());
      yeti_log_memory_access("read", &i, omp_get_thread_num());
    }
    yeti_log_omp("exit", "for", omp_get_thread_num());
    yeti_log_memory_access("clause write", &a, omp_get_thread_num());
    yeti_log_memory_access("clause write", &sum, omp_get_thread_num());
    yeti_log_omp("exit", "parallel", omp_get_thread_num());
  }
}
