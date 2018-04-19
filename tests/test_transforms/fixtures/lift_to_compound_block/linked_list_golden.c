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

  void *censor01 = malloc(sizeof(new_node));
  linked_list *new_node = (linked_list *) censor01;
  int censor02 = new_node == NULL;
  if (censor02)
    return NULL;

  new_node->data = data;

  return new_node;
}

int main()
{
  linked_list *list;
  list = create_node(0);
  list->next = create_node(0);
  struct node **censor03 = &list->next;
  (*censor03)->next = create_node(0);
  struct node **censor04 = &list->next;
  struct node **censor05 = &(*censor04)->next;
  (*censor05)->next = create_node(0);
  struct node **censor06 = &list->next;
  list->data = (*censor06)->data;
  struct node **censor07 = &list->next;
  struct node **censor08 = &(*censor07)->next;
  struct node **censor09 = &list->next;
  struct node **censor010 = &(*censor09)->next;
  struct node **censor011 = &(*censor010)->next;
  (*censor08)->data = (*censor011)->data;
  return 0;
}
