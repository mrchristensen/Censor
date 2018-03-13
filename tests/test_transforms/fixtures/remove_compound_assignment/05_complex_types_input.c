
struct node {
    int data[10];
    struct node* next;
};

int main() {
    int a[5][5];
    a[1][2] += 5;

    int b[5][5][5];
    b[1][2][3] += 5;

    struct node n;
    n.data[0] += 1;

    n.next->data[0] += 1;

    n.next->next->data[0] += 1;

    struct node *ns[10];

    ns[0]->next.data[0] += 1;
}