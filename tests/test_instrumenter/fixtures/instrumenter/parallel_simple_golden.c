void x()
{
}

void yeti_log_heap_access(char* mode, char* var, int index, int thread_num)
{
  printf("%s, %d, %d, %s\n", mode, index, thread_num, var);
}

void yeti_log_omp(char* action, char* construct)
{
  printf("%s, %s", action, construct);
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
