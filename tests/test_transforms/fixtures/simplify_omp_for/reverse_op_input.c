int main() {
    #pragma omp parallel
    {
        #pragma omp for
        for (int i = 0; 10 > i; ++i) {

        }

        #pragma omp for
        for (int i = 0; 10 > i; i += 10) {

        }
    }
}
