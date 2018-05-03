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
void x(char *yeti_task_id, char *yeti_parent_task_id)
{
}

int main()
{
  char *yeti_task_id = yeti_make_task_id();
  char *yeti_parent_task_id = yeti_task_id;
  #pragma omp parallel
  {
    char *yeti_parent_task_id = yeti_task_id;
    char *yeti_task_id = yeti_make_task_id();
    yeti_log_post(yeti_task_id, yeti_parent_task_id);
    x(yeti_task_id, yeti_parent_task_id);
  }
  yeti_log_await();
}
