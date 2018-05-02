void yeti_log_memory_access(char* mode, void* var, char* task_id) {
  printf("%s, %p, %s\n", mode, var, task_id);
}

void yeti_log_post(char* task_id, char* parent_id) {
  printf("post, %s, %s\n", task_id, parent_id);
}

void yeti_log_isolated(char* task_id, char* parent_id) {
  printf("isolated, %s, %s\n", task_id, parent_id);
}

void yeti_log_await(void) {
  printf("await\n");
}

void yeti_log_ewait(void) {
  printf("ewait\n");
}

char* yeti_make_task_id(void) {
  int task_id;
#pragma omp atomic capture
  {
    yeti_task_id_generator++;
    task_id = yeti_task_id_generator;
  }
  char* yeti_task_id = (char*)malloc(sizeof(task_id));
  sprintf(yeti_task_id, "%d", task_id);
  return yeti_task_id;
}
