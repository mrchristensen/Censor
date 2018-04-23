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
#pragma omp parallel
  {
    yeti_log_omp("enter", "parallel", omp_get_thread_num());
    int a = 1;
    yeti_log_memory_access("read", &a, omp_get_thread_num());
    int *p_int = &a;
    int b[10];
    yeti_log_memory_access("read", &b, omp_get_thread_num());
    int (*p_arr)[10] = &b;
    yeti_log_memory_access("read", &a, omp_get_thread_num());
    yeti_log_memory_access("read", &p_int, omp_get_thread_num());
    yeti_log_memory_access("write", p_int, omp_get_thread_num());
    *p_int = a + 1;
    yeti_log_memory_access("read", &b, omp_get_thread_num());
    yeti_log_memory_access("read", &b[0], omp_get_thread_num());
    yeti_log_memory_access("read", &p_arr, omp_get_thread_num());
    yeti_log_memory_access("read", p_arr, omp_get_thread_num());
    yeti_log_memory_access("write", &(*p_arr)[0], omp_get_thread_num());
    (*p_arr)[0] = b[0];
    yeti_log_omp("exit", "parallel", omp_get_thread_num());
  }
}
