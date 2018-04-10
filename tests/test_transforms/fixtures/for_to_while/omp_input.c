
int main() {
    #pragma omp parallel
    {
        #pragma omp for
        for (int i = 0; i < 10; ++i) {
            for (int j = 0; j < 10; ++j) {

            }
        }

        #pragma omp for
        for (int i = 0; i < 10; ++i) {

        }
    }
}