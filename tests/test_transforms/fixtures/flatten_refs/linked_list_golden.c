
struct node
{

  int data;

  struct node* next;
};

typedef struct node linked_list;

linked_list *create_node(int data)
{

  linked_list* new_node = (linked_list*)malloc(sizeof(new_node));

  if (new_node == NULL)
    return NULL;

  int *censor01 = &new_node->data;
  *censor01 = data;

  return new_node;
}

int main()
{
  linked_list *list;
  list = create_node(0);

  struct node **censor02 = &list->next;
  *censor02 = create_node(0);

  struct node **censor03 = &list->next;
  struct node **censor04 = &(*censor03)->next;
  *censor04 = create_node(0);

  struct node **censor05 = &list->next;
  struct node **censor06 = &(*censor05)->next;
  struct node **censor07 = &(*censor06)->next;
  *censor07 = create_node(0);

  int *censor08 = &list->data;
  struct node **censor09 = &list->next;
  int *censor010 = &(*censor09)->data;
  *censor08 = *censor010;

  struct node **censor011 = &list->next;
  struct node **censor012 = &(*censor011)->next;
  int *censor013 = &(*censor012)->data;
  struct node **censor014 = &list->next;
  struct node **censor015 = &(*censor014)->next;
  struct node **censor016 = &(*censor015)->next;
  int *censor017 = &(*censor016)->data;
  *censor013 = *censor017;

  return 0;
}
