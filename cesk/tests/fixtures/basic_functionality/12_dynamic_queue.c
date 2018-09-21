#include <stdio.h>
#include <stdlib.h>

struct qNode {
    int data;
    struct qNode* next;
};

struct Dynamicq {
    struct qNode* head;
    struct qNode* tail; 
    int currentSize;
};

struct Dynamicq* newDynamicQ() {
    struct Dynamicq* q = (struct Dynamicq*) malloc(sizeof(struct Dynamicq));
    q->head = NULL;
    q->tail = NULL;
    q->currentSize = 0;
    return q;
}

void dynamicqPush(struct Dynamicq *q, int n) {
    struct qNode* node = (struct qNode*)malloc(sizeof(struct qNode));
    node->next = NULL;
    node->data = n;

    if (q->currentSize == 0) {
        q->head = node;
        q->tail = node;
    }
    else {
        q->tail->next = node;
        q->tail = node;
    }
    ++q->currentSize;
    return;
}

int dynamicqPop(struct Dynamicq *q) {
    if (q->currentSize == 0) {
        //TODO: actually should be some error if its empty
        return 0;
    }

    struct qNode* node = q->head;
    int n = node->data;
    q->head = node->next;
    --q->currentSize;
    free(node);
    return n;
}

void destruct(struct Dynamicq* q) {
    while(q->currentSize > 0) {
        dynamicqPop(q);
    }
    free(q);
}

int main() {
    struct Dynamicq* q = newDynamicQ();

    int i = 0;
	addLoop:
        dynamicqPush(q, i); 
		++i;
	if (i < 10) {
		goto addLoop;
	}

    i = 0;
    removeLoop:
        dynamicqPop(q); 
		++i;
	if (i < 9) {
		goto removeLoop;
	}

    int lastOne = dynamicqPop(q);
    printf("%d\n", lastOne);

    return 0;
}
