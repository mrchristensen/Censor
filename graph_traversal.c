#include <stdio.h>
#include <stdlib.h>
typedef struct Node Node;
typedef struct Element Element;

struct Node;
struct Element;
struct ElementList;

struct Element{
    Node* data;
    Element* next;
};

struct Node{
    int id;
    Element* neighbors;
};

void add_to_queue(Node*);

Node *A,*B,*C;

Element *queue;


void printNode(Node* toPrint){
    printf("%d\n", toPrint->id);
}

void printElements(Element* toPrint){
    printNode(toPrint->data);
    if (toPrint->next)
        printElements(toPrint->next);
}

void set_next(Node* from, Node* to){
    Element* list = from->neighbors;
    Element* newElement = malloc(sizeof(Element));
    newElement->data = to;

    if (!list){
        from->neighbors = newElement;
        return;
    }

    Element* currentElement = list;
    while(currentElement->next){
        currentElement = currentElement->next;
    }
    currentElement->next = newElement;
}

void set_head(Node* start){
    queue = malloc(sizeof(Element));
    queue->data = start;
    queue->next = 0;
}

int queue_not_empty(){
    return queue != 0;
}

Node* pop_queue(){
    Node* toReturn = queue->data;
    queue = queue->next;
    return toReturn;
}

void add_to_queue(Node* node){
    Element* toAddNext = node->neighbors;
    if (toAddNext == 0)
        return;
    if (queue == 0){
        queue = malloc(sizeof(Element));
        queue->data = toAddNext->data;
        toAddNext = toAddNext->next;
        queue->next = 0;
    }
    Element* last = queue;
    while(last->next)
        last = last->next;
    while(toAddNext){
        last->next = malloc(sizeof(Element));
        last = last->next;
        last->data = toAddNext->data;
        toAddNext = toAddNext->next;
        last->next = 0;
    }
}

void init(){
    A = malloc(sizeof(Node));
    B = malloc(sizeof(Node));
    C = malloc(sizeof(Node));
    A->id = 1;
    B->id = 2;
    C->id = 3;
    A->neighbors = 0;
    B->neighbors = 0;
    C->neighbors = 0;
    queue = 0;
}

int main(){
    init();
    set_next(A, B);
    set_next(A, C);
    set_next(B, C);
    set_next(C, A);
    set_head(A);
    while (queue_not_empty()){
        // add_to_queue(pop_queue());
        pop_queue();
    }
}