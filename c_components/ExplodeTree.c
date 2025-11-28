// Derived from evaluate_explode_tree in gh_components_stripped.py

#include "ExplodeTree.h"

void ExplodeTree_eval(const ExplodeTreeInput *in, ExplodeTreeOutput *out) {
    // GH Explode Tree: extract Branch 0 (first branch)
    out->branch0_count = in->item_count;
    for (int i = 0; i < in->item_count && i < EXPLODETREE_MAX_ITEMS; i++) {
        out->branch0[i] = in->items[i];
    }
}

