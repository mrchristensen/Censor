void x() {
}

int main() {
  #pragma omp parallel
  {
    x();
  }
}
