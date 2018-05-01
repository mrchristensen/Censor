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
  int a = 0;
  int sum = 0;
  int values[10];
  int i;
  #pragma omp parallel
  {
    yeti_log_omp("enter", "parallel");
    yeti_log_memory_access("clause read", &values);
    yeti_log_memory_access("clause read", &values[0]);
    yeti_log_memory_access("clause read", &values);
    yeti_log_memory_access("clause read", &values[1]);
    yeti_log_memory_access("clause read", &values);
    yeti_log_memory_access("clause read", &values[2]);
    yeti_log_memory_access("clause read", &values);
    yeti_log_memory_access("clause read", &values[3]);
    yeti_log_memory_access("clause read", &values);
    yeti_log_memory_access("clause read", &values[4]);
    yeti_log_memory_access("clause read", &values);
    yeti_log_memory_access("clause read", &values[5]);
    yeti_log_memory_access("clause read", &values);
    yeti_log_memory_access("clause read", &values[6]);
    yeti_log_memory_access("clause read", &values);
    yeti_log_memory_access("clause read", &values[7]);
    yeti_log_memory_access("clause read", &values);
    yeti_log_memory_access("clause read", &values[8]);
    yeti_log_memory_access("clause read", &values);
    yeti_log_memory_access("clause read", &values[9]);
    yeti_log_memory_access("clause read", &sum);
    yeti_log_omp("enter", "for");
#pragma omp for firstprivate(values) lastprivate(a) schedule(static, 1) reduction(+:sum)
    for (i = 0; i < 10; i++)
    {
      yeti_log_memory_access("write", &a);
      a++;
      yeti_log_memory_access("read", &sum);
      yeti_log_memory_access("read", &values);
      yeti_log_memory_access("read", &i);
      yeti_log_memory_access("read", &values[i]);
      yeti_log_memory_access("write", &sum);
      sum = sum + values[i];
      yeti_log_memory_access("write", &i);
      yeti_log_memory_access("read", &i);
    }
    yeti_log_omp("exit", "for");
    yeti_log_memory_access("clause write", &a);
    yeti_log_memory_access("clause write", &sum);
    yeti_log_omp("exit", "parallel");
  }
}
