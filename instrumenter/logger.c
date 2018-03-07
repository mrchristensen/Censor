void yeti_log_heap_access(char* mode, void* var, int thread_num, char* name) {
  printf("%s, %p, %d, %s\n", mode, var, thread_num, name);
}

void yeti_log_omp(char* action, char* construct) {
  printf("%s, %s", action, construct);
}
