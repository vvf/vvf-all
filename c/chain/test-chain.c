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

typedef int TAction(int);

int test_act_add100(int a){ return a+100; };
int test_act_add100(int a){ return a+1000; };
int act_none(int x){ return x; }
Node *copyList(Node *head, TAction *act )
{
    static Node * first=NULL;

    static Node * newcupls[10][2];

    static int cupls_counter=0;


    Node * cur = malloc(sizeof(Node));
    Node * old_next;

//    newcupls[cupls_counter] = malloc(sizeof(Node)*2);
    if( !first ) first = cur;
    if(!act) act = act_none;
    cur->data = (*act)(head->data);

    //cur->random = malloc(sizeof(Node*) * 2);
    printf(" copied %d ", cur->data);
    old_next = head->next;
    cur->random = (Node *)newcupls[cupls_counter];
    newcupls[cupls_counter][0] = head->random;
    newcupls[cupls_counter][1] = NULL;
    cupls_counter++;
    head->next = cur;
    if( old_next ){
//        printf(" next...\n");
        cur->next = copyList( old_next, act );
//        if( cur->next ) printf(" next is %d\t", cur->next->data);

        if( !((Node **)cur->random)[1] ){ // have never be here
            ((Node **)cur->random)[1] = ((Node **)cur->random)[0]->next;
            printf(" !!! ");
        }
        cur->random = ((Node **)cur->random)[1];
        //printf("random-> %d\n", cur->random->data );

        head->next = old_next; // restore pointer in old chain
    }else{
        //printf("\n--- top ---\n");
        for( int i=0;i<cupls_counter ; i++){
            newcupls[i][1] = newcupls[i][0]->next; // here next is pointer to a node in the new chain
        }
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
    
    Node *newList = copyList(node, test_act_add100);
    printf("\nPRINT NEW LIST DATA %p\n", newList);
    printListData(newList);
    Node *newList2 = copyList(newList, test_act_add100);
    printf("\nOLD LIST\n");
    printListData(newList2);
    return 0;
}