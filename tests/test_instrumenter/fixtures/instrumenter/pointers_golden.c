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
int main(int argc, char** argv)
{
#pragma omp parallel
  {
    yeti_log_omp("enter", "parallel");
    int a = 1;
    yeti_log_memory_access("read", &a);
    int *p_int = &a;
    int b[10];
    yeti_log_memory_access("read", &b);
    int (*p_arr)[10] = &b;
    yeti_log_memory_access("read", &a);
    yeti_log_memory_access("read", &p_int);
    yeti_log_memory_access("write", p_int);
    *p_int = a + 1;
    yeti_log_memory_access("read", &b);
    yeti_log_memory_access("read", &b[0]);
    yeti_log_memory_access("read", &p_arr);
    yeti_log_memory_access("read", p_arr);
    yeti_log_memory_access("write", &(*p_arr)[0]);
    (*p_arr)[0] = b[0];
    yeti_log_memory_access("read", &b);
    yeti_log_memory_access("read", &b[0]);
    int *c = &b[0];
    yeti_log_omp("exit", "parallel");
  }
}
