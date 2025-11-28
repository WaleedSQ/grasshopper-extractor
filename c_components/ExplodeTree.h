#ifndef EXPLODETREE_H
#define EXPLODETREE_H

// Derived from evaluate_explode_tree in gh_components_stripped.py

#define EXPLODETREE_MAX_ITEMS 1000

typedef struct {
    float items[EXPLODETREE_MAX_ITEMS];
    int item_count;
} ExplodeTreeInput;

typedef struct {
    float branch0[EXPLODETREE_MAX_ITEMS];
    int branch0_count;
} ExplodeTreeOutput;

void ExplodeTree_eval(const ExplodeTreeInput *in, ExplodeTreeOutput *out);

#endif // EXPLODETREE_H

