
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
    struct Dynamicq* censor0 = (struct Dynamicq*) malloc(sizeof(struct Dynamicq));
    censor0->head = 0;
    censor0->tail = 0;
    censor0->currentSize = 0;
    return censor0;
}

void dynamicqPush(struct Dynamicq *q, int censor1) {
    struct qNode* node = (struct qNode*)malloc(sizeof(struct qNode));
    node->next = 0;
    node->data = censor1;

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
        return 0;
    }

    struct qNode* node = q->head;
    int n = node->data;
    q->head = node->next;
    --q->currentSize;
    free(node);
    return n;
}

void destruct(struct Dynamicq* censor3) {
    while(censor3->currentSize > 0) {
        dynamicqPop(censor3);
    }
    free(censor3);
}

int main() {
    struct Dynamicq* q = newDynamicQ();

    int i = 0;
	censor5:
        dynamicqPush(q, i);
		++i;
	if (i < 10) {
		goto censor5;
	}

    i = 0;
    censor2:
        dynamicqPop(q);
		++i;
	if (i < 9) {
		goto censor2;
	}

    int censor4 = dynamicqPop(q);

    return 0;
}