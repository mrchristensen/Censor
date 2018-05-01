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
int censor0465 = 128 + 0;
int censor0466 = 128 + 0;
int censor0467 = 128 + 0;
int censor0468 = 128 + 0;
int censor0469 = 128 + 0;
int censor0470 = 128 + 0;
int censor0471 = 128 + 0;
int censor0472 = 128 + 0;
static void init_array(int ni, int nj, int nk, int nl, int nm, double A[censor0466][censor0465], double B[censor0468][censor0467], double C[censor0470][censor0469], double D[censor0472][censor0471])
{
  {
    int c2;
    int c1;
    yeti_log_memory_access("read", &nl);
    int censor0473 = nl >= 1;
    yeti_log_memory_access("read", &censor0473);
    if (censor0473)
    {
      #pragma omp parallel
      {
        yeti_log_omp("enter", "parallel");
        {
          int censor038;
          yeti_log_memory_access("read", &ni);
          int censor0474 = ni + (-1);
          yeti_log_memory_access("read", &nj);
          int censor0475 = nj + (-1);
          yeti_log_memory_access("read", &censor0474);
          yeti_log_memory_access("read", &censor0475);
          int censor0476 = censor0474 < censor0475;
          yeti_log_memory_access("read", &censor0476);
          if (censor0476)
          {
            yeti_log_memory_access("read", &ni);
            yeti_log_memory_access("write", &censor038);
            censor038 = ni + (-1);
            goto censor0200_ENDIF;
          }

          {
            yeti_log_memory_access("read", &nj);
            yeti_log_memory_access("write", &censor038);
            censor038 = nj + (-1);
          }
          censor0200_ENDIF:
          (void ) 0;

          yeti_log_omp("enter", "for nowait");
          yeti_log_memory_access("read", &censor038);
          #pragma omp for  private(c2) nowait
          for (c1 = 0; c1 <= censor038; c1++)
          {
            yeti_log_memory_access("write", &c1);
            yeti_log_memory_access("read", &c1);
            yeti_log_memory_access("read", &censor038);
          }

          yeti_log_omp("exit", "for nowait");
        }
        yeti_log_omp("exit", "parallel");
      }

    }
  }
}

int main(int argc, char** argv)
{
  return 0;
}

