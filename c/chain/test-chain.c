#include <time.h>
#include <stdlib.h>
#include <stdio.h>

typedef struct NodeTag {
    struct NodeTag *next;
    struct NodeTag *random;
    int data;
} Node;

void printListData(Node *source)
{
    Node *node = source;
    do {
        printf("Node %d (%p), next %d (%p), random %d (%p)\n",node->data,node, node->next ? node->next->data : -1, node->next, node->random->data, node->random );
        node = node -> next;
    } while (node);
}


Node *copyList(Node *head)
{
    static Node * first=NULL;

    static Node ** newcupls[10];
    static Node * future_update[10];

    static int future_current=0;
    static int future_update_top=0;

//    if(!newcupls) newcupls = malloc(sizeof(Node*)*10);
//    if(!future_update) future_update = malloc(sizeof(Node)*10);

    Node * cur = malloc(sizeof(Node));
//    Node * bak;
//    Node * old_next;
    newcupls[future_current] = malloc(sizeof(Node)*2);
    newcupls[future_current][0] = head;
    newcupls[future_current][1] = cur;
    future_current++;
    if( !first ) first = cur;
    cur->data = head->data+100;
    
    //cur->random = malloc(sizeof(Node*) * 2);
    printf(" copied %d ", cur->data);
    //old_next = head->next;
    cur->random = NULL;//head->random;
    for(int i=0;i<future_current; i++){
        if( head->random == newcupls[future_current][0] ){
            cur->random = newcupls[future_current][1];
            printf("random was to prev: %d", cur->random->data);
        }
    }
    if(!cur->random){
        future_update[future_update_top] = cur;
        future_update_top++;
    }
    if( head->next ){
        printf(" next...\n");
        cur->next = copyList( head->next );
        if( cur->next ) printf(" next is %d\n", cur->next->data);
    }else{
        printf("\n---\n");
/*
        bak = first;
        while( bak ){
            printf("<<<\t new:%d rand(to old)%d rand-new:%p next-new:%p", bak->data, bak->random->data, bak->random->next, bak->next);
            printf("\t\t %d\n", bak->random->next->data);
            //bak->random = bak->random->next;
            bak = bak->next;
        }
*/
    }
    return cur;
}

int main()
{
    srand(time(NULL));
    int count = 10;
    Node *sourceArray = malloc(count * sizeof(Node));
    for (int i = 0; i < count; i++)
    {
        Node *node = &sourceArray[i];
        node->data = i;
        node->random = &sourceArray[(rand() % count)];
        if (i < count - 1)
        {
            node->next = &sourceArray[i + 1];
        }
        else
        {
            node->next = NULL;
        }
    }
    
    printf("\nOLD LIST\n");
    Node *node = &sourceArray[0];
    printListData(node);
    
    Node *newList = copyList(node);
    printf("\nPRINT NEW LIST DATA %p\n", newList);
//    printListData(newList);
    return 0;
}