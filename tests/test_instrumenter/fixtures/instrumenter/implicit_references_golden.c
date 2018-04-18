void yeti_log_heap_access(char* mode, void* var, int thread_num)
{
  printf("%s, %p, %d\n", mode, var, thread_num);
}

void yeti_log_omp(char* action, char* construct, int thread_num)
{
  printf("%s, %s, %d\n", action, construct, thread_num);
}

int main(int argc, char** argv)
{
  int a = 0;
  int sum = 0;
  int values[10] = {1,2,3,4,5,6,7,8,9,10};
  #pragma omp parallel
  {
    yeti_log_omp("enter", "parallel", omp_get_thread_num());
    yeti_log_heap_access("clause read", &a, omp_get_thread_num());
    yeti_log_heap_access("clause read", &sum, omp_get_thread_num());
    yeti_log_omp("enter", "for", omp_get_thread_num());
#pragma omp for firstprivate(a) lastprivate(a) schedule(static, 1) reduction(+:sum)
    for (int i = 0; i < 10; i++)
    {
      yeti_log_heap_access("write", &a, omp_get_thread_num());
      a++;
      yeti_log_heap_access("read", &values[i], omp_get_thread_num());
      yeti_log_heap_access("read", &sum, omp_get_thread_num());
      yeti_log_heap_access("write", &sum, omp_get_thread_num());
      sum = sum + values[i];
    }
    yeti_log_omp("exit", "for", omp_get_thread_num());
    yeti_log_heap_access("clause write", &a, omp_get_thread_num());
    yeti_log_heap_access("clause write", &sum, omp_get_thread_num());
    yeti_log_omp("exit", "parallel", omp_get_thread_num());
  }
}
