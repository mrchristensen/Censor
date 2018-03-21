void x()
{
}

void yeti_log_heap_access(char* mode, void* var, int thread_num, char* name)
{
  printf("%s, %p, %d, %s\n", mode, var, thread_num, name);
}

void yeti_log_omp(char* action, char* construct, int thread_num)
{
  printf("%s, %s, %d", action, construct, thread_num);
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
