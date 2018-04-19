void yeti_log_heap_access(char *mode, void *var, int thread_num)
{
  printf("%s, %p, %d\n", mode, var, thread_num);
}

void yeti_log_omp(char *action, char *construct, int thread_num)
{
  printf("%s, %s, %d\n", action, construct, thread_num);
}

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
    yeti_log_heap_access("read", &nl, omp_get_thread_num());
    int censor0473 = nl >= 1;
    yeti_log_heap_access("read", &censor0473, omp_get_thread_num());
    if (censor0473)
    {
      #pragma omp parallel
      {
        yeti_log_omp("enter", "parallel", omp_get_thread_num());
        {
          int censor038;
          yeti_log_heap_access("read", &ni, omp_get_thread_num());
          int censor0474 = ni + (-1);
          yeti_log_heap_access("read", &nj, omp_get_thread_num());
          int censor0475 = nj + (-1);
          yeti_log_heap_access("read", &censor0475, omp_get_thread_num());
          yeti_log_heap_access("read", &censor0474, omp_get_thread_num());
          int censor0476 = censor0474 < censor0475;
          yeti_log_heap_access("read", &censor0476, omp_get_thread_num());
          if (censor0476)
          {
            yeti_log_heap_access("read", &ni, omp_get_thread_num());
            yeti_log_heap_access("write", &censor038, omp_get_thread_num());
            censor038 = ni + (-1);
            goto censor0200_ENDIF;
          }

          {
            yeti_log_heap_access("read", &nj, omp_get_thread_num());
            yeti_log_heap_access("write", &censor038, omp_get_thread_num());
            censor038 = nj + (-1);
          }
          censor0200_ENDIF:
          (void ) 0;

          yeti_log_omp("enter", "for", omp_get_thread_num());
          #pragma omp for  private(c2)
          for (c1 = 0; c1 <= censor038; c1++)
          {
          }

          yeti_log_omp("exit", "for", omp_get_thread_num());
        }
        yeti_log_omp("exit", "parallel", omp_get_thread_num());
      }

    }
  }
}

int main(int argc, char** argv)
{
  return 0;
}

