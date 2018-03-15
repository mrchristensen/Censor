struct node
{
  int data[10];
  struct node *next;
};
int main()
{
  int a[5][5];

    int *censor01 = &a[1][2];
    *censor01 = (*censor01) + 5;

  int b[5][5][5];

    int *censor02 = &b[1][2][3];
    *censor02 = (*censor02) + 5;

  struct node n;

    int *censor03 = &n.data[0];
    *censor03 = (*censor03) + 1;


    int *censor04 = &n.next->data[0];
    *censor04 = (*censor04) + 1;


    int *censor05 = &n.next->next->data[0];
    *censor05 = (*censor05) + 1;

  struct node *ns[10];

    int *censor06 = &ns[0]->next.data[0];
    *censor06 = (*censor06) + 1;

}

