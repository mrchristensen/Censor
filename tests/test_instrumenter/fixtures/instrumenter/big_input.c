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
    int censor0473 = nl >= 1;
    if (censor0473)
    {
      #pragma omp parallel
      {
        {
          int censor038;
          int censor0474 = ni + (-1);
          int censor0475 = nj + (-1);
          int censor0476 = censor0474 < censor0475;
          if (censor0476)
          {
            censor038 = ni + (-1);
            goto censor0200_ENDIF;
          }

          {
            censor038 = nj + (-1);
          }
          censor0200_ENDIF:
          (void ) 0;

          #pragma omp for  private(c2)
          for (c1 = 0; c1 <= censor038; c1++) {

          }

        }
      }

    }
  }
}

int main(int argc, char** argv) {
  return 0;
}

