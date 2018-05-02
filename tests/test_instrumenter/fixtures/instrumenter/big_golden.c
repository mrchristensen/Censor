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
int censor0465 = 128 + 0;
int censor0466 = 128 + 0;
int censor0467 = 128 + 0;
int censor0468 = 128 + 0;
int censor0469 = 128 + 0;
int censor0470 = 128 + 0;
int censor0471 = 128 + 0;
int censor0472 = 128 + 0;
static void init_array(char *yeti_task_id, char *yeti_parent_task_id, int ni, int nj, int nk, int nl, int nm, double A[censor0466][censor0465], double B[censor0468][censor0467], double C[censor0470][censor0469], double D[censor0472][censor0471])
{
  {
    int c2;
    int c1;
    yeti_log_memory_access("read", &nl, yeti_task_id);
    int censor0473 = nl >= 1;
    yeti_log_memory_access("read", &censor0473, yeti_task_id);
    if (censor0473)
    {
      #pragma omp parallel
      {
        char *yeti_parent_task_id = yeti_task_id;
        char *yeti_task_id = yeti_make_task_id();
        yeti_log_post(yeti_task_id, yeti_parent_task_id);
        {
          int censor038;
          yeti_log_memory_access("read", &ni, yeti_task_id);
          int censor0474 = ni + (-1);
          yeti_log_memory_access("read", &nj, yeti_task_id);
          int censor0475 = nj + (-1);
          yeti_log_memory_access("read", &censor0474, yeti_task_id);
          yeti_log_memory_access("read", &censor0475, yeti_task_id);
          int censor0476 = censor0474 < censor0475;
          yeti_log_memory_access("read", &censor0476, yeti_task_id);
          if (censor0476)
          {
            yeti_log_memory_access("read", &ni, yeti_task_id);
            yeti_log_memory_access("write", &censor038, yeti_task_id);
            censor038 = ni + (-1);
            goto censor0200_ENDIF;
          }

          {
            yeti_log_memory_access("read", &nj, yeti_task_id);
            yeti_log_memory_access("write", &censor038, yeti_task_id);
            censor038 = nj + (-1);
          }
          censor0200_ENDIF:
          (void ) 0;

          yeti_log_memory_access("read", &censor038, yeti_task_id);
          #pragma omp for  private(c2) nowait
          for (c1 = 0; c1 <= censor038; c1++)
          {
            yeti_log_memory_access("write", &c1, yeti_task_id);
            yeti_log_memory_access("read", &c1, yeti_task_id);
            yeti_log_memory_access("read", &censor038, yeti_task_id);
          }

        }
      }
      yeti_log_await();
    }
  }
}

int main(int argc, char** argv)
{
  char *yeti_task_id = yeti_make_task_id();
  char *yeti_parent_task_id = yeti_task_id;
  return 0;
}

