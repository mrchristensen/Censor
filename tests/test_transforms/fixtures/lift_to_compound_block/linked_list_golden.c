typedef int size_t;
extern void *malloc (size_t __size);
struct node
{
  int data;
  struct node* next;
};

typedef struct node linked_list;

linked_list *create_node(int data)
{
  linked_list *new_node = (linked_list *) malloc(sizeof(linked_list));
  int censor01 = new_node == NULL;
  if (censor01)
    return NULL;

  new_node->data = data;

  return new_node;
}

int main()
{
  linked_list *list;
  list = create_node(0);
  list->next = create_node(0);
  struct node **censor02 = &list->next;
  (*censor02)->next = create_node(0);
  struct node **censor03 = &list->next;
  struct node **censor04 = &(*censor03)->next;
  (*censor04)->next = create_node(0);
  struct node **censor05 = &list->next;
  list->data = (*censor05)->data;
  struct node **censor06 = &list->next;
  struct node **censor07 = &(*censor06)->next;
  struct node **censor08 = &list->next;
  struct node **censor09 = &(*censor08)->next;
  struct node **censor010 = &(*censor09)->next;
  (*censor07)->data = (*censor010)->data;
  return 0;
}
