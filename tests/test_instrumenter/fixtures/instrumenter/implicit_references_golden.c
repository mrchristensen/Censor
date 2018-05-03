int yeti_task_id_generator = -1;
#pragma BEGIN #include<stdlib.h>
#pragma END
#pragma BEGIN #include<stdio.h>
#pragma END
void yeti_log_memory_access(char *mode, void *var, char *task_id)
{
  printf("%s, %p, %s\n", mode, var, task_id);
}

void yeti_log_post(char *task_id, char *parent_id)
{
  printf("post, %s, %s\n", task_id, parent_id);
}

void yeti_log_isolated(char *task_id, char *parent_id)
{
  printf("isolated, %s, %s\n", task_id, parent_id);
}

void yeti_log_await(void)
{
  printf("await\n");
}

void yeti_log_ewait(void)
{
  printf("ewait\n");
}

char *yeti_make_task_id(void)
{
  int task_id;
  #pragma omp atomic capture
  {
    yeti_task_id_generator++;
    task_id = yeti_task_id_generator;
  }
  char *yeti_task_id = (char *) malloc(sizeof(task_id));
  sprintf(yeti_task_id, "%d", task_id);
  return yeti_task_id;
}

#pragma BEGIN #include<omp.h>
#pragma END
int main(int argc, char** argv)
{
  char *yeti_task_id = yeti_make_task_id();
  char *yeti_parent_task_id = yeti_task_id;
  int a = 0;
  int sum = 0;
  int values[10];
  int i;
  #pragma omp parallel
  {
    char *yeti_parent_task_id = yeti_task_id;
    char *yeti_task_id = yeti_make_task_id();
    yeti_log_post(yeti_task_id, yeti_parent_task_id);
    yeti_log_memory_access("clause read", &values, yeti_task_id);
    yeti_log_memory_access("clause read", &values[0], yeti_task_id);
    yeti_log_memory_access("clause read", &values, yeti_task_id);
    yeti_log_memory_access("clause read", &values[1], yeti_task_id);
    yeti_log_memory_access("clause read", &values, yeti_task_id);
    yeti_log_memory_access("clause read", &values[2], yeti_task_id);
    yeti_log_memory_access("clause read", &values, yeti_task_id);
    yeti_log_memory_access("clause read", &values[3], yeti_task_id);
    yeti_log_memory_access("clause read", &values, yeti_task_id);
    yeti_log_memory_access("clause read", &values[4], yeti_task_id);
    yeti_log_memory_access("clause read", &values, yeti_task_id);
    yeti_log_memory_access("clause read", &values[5], yeti_task_id);
    yeti_log_memory_access("clause read", &values, yeti_task_id);
    yeti_log_memory_access("clause read", &values[6], yeti_task_id);
    yeti_log_memory_access("clause read", &values, yeti_task_id);
    yeti_log_memory_access("clause read", &values[7], yeti_task_id);
    yeti_log_memory_access("clause read", &values, yeti_task_id);
    yeti_log_memory_access("clause read", &values[8], yeti_task_id);
    yeti_log_memory_access("clause read", &values, yeti_task_id);
    yeti_log_memory_access("clause read", &values[9], yeti_task_id);
    yeti_log_memory_access("clause read", &sum, yeti_task_id);
#pragma omp for firstprivate(values) lastprivate(a) schedule(static, 1) reduction(+:sum)
    for (i = 0; i < 10; i++)
    {
      yeti_log_memory_access("write", &a, yeti_task_id);
      a++;
      yeti_log_memory_access("read", &sum, yeti_task_id);
      yeti_log_memory_access("read", &values, yeti_task_id);
      yeti_log_memory_access("read", &i, yeti_task_id);
      yeti_log_memory_access("read", &values[i], yeti_task_id);
      yeti_log_memory_access("write", &sum, yeti_task_id);
      sum = sum + values[i];
    }
    yeti_log_memory_access("clause write", &a, yeti_task_id);
    yeti_log_memory_access("clause write", &sum, yeti_task_id);
    yeti_log_await();
  }
  yeti_log_await();
}
