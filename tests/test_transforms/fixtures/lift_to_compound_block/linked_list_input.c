typedef int size_t;
extern void *malloc (size_t __size);
struct node {
  int data;
  struct node* next;
};

typedef struct node linked_list;

linked_list* create_node(int data) {
  linked_list* new_node = (linked_list*)malloc(sizeof(new_node));
  if (new_node == NULL)
    return NULL;
  new_node->data = data;
  return new_node;
}

int main() {
  linked_list* list;
  list = create_node(0);
  list->next = create_node(0);
  list->next->next = create_node(0);
  list->next->next->next = create_node(0);
  list->data = list->next->data;
  list->next->next->data = list->next->next->next->data;
  return 0;
}
