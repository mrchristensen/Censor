
int main() {
    #pragma omp parallel
    {
        #pragma omp for
        for (int i = 0; i < 10; ++i) {

        }

        #pragma omp for
        for (int i = 0; i < 10; i += 10) {

        }
    }
}