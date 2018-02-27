void yeti_log_heap_access(char* mode, void* var, int thread_num) {
  printf("%s, %08x, %d\n", mode, &(var), thread_num);
}

void yeti_log_omp(char* action, char* construct) {
  printf("%s, %s", action, construct);
}
