#ifndef LISTITEM_H
#define LISTITEM_H

// Derived from evaluate_list_item in gh_components_stripped.py

#define LISTITEM_MAX_SIZE 1000

typedef struct {
    float list[LISTITEM_MAX_SIZE];
    int list_size;
    int index;
    bool wrap;
} ListItemInput;

typedef struct {
    float item;
    bool valid;
} ListItemOutput;

void ListItem_eval(const ListItemInput *in, ListItemOutput *out);

#endif // LISTITEM_H

