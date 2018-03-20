
struct node
{

  int data;

  struct node* next;
};

typedef struct node linked_list;

linked_list *create_node(int data)
{

  linked_list* new_node = (linked_list*)malloc(sizeof(new_node));

  int censor01 = new_node == NULL;
  if (censor01)
    return NULL;

  int *censor02 = &new_node->data;
  *censor02 = data;

  return new_node;
}

int main()
{
  linked_list *list;
  list = create_node(0);

  struct node **censor03 = &list->next;
  *censor03 = create_node(0);

  struct node **censor04 = &list->next;
  struct node **censor05 = &(*censor04)->next;
  *censor05 = create_node(0);

  struct node **censor06 = &list->next;
  struct node **censor07 = &(*censor06)->next;
  struct node **censor08 = &(*censor07)->next;
  *censor08 = create_node(0);

  int *censor09 = &list->data;
  struct node **censor010 = &list->next;
  int *censor011 = &(*censor010)->data;
  *censor09 = *censor011;

  struct node **censor012 = &list->next;
  struct node **censor013 = &(*censor012)->next;
  int *censor014 = &(*censor013)->data;
  struct node **censor015 = &list->next;
  struct node **censor016 = &(*censor015)->next;
  struct node **censor017 = &(*censor016)->next;
  int *censor018 = &(*censor017)->data;
  *censor014 = *censor018;

  return 0;
}
