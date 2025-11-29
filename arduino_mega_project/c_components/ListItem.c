// Derived from evaluate_list_item in gh_components_stripped.py

#include "ListItem.h"
#include <stdbool.h>

void ListItem_eval(const ListItemInput *in, ListItemOutput *out) {
    // GH List Item: extract item by index
    if (in->list_size == 0) {
        out->valid = false;
        return;
    }
    
    int idx = in->index;
    
    if (in->wrap) {
        // GH List Item: wrap index
        idx = idx % in->list_size;
        if (idx < 0) {
            idx += in->list_size;
        }
    } else {
        // GH List Item: out-of-range returns invalid
        if (idx < 0 || idx >= in->list_size) {
            out->valid = false;
            return;
        }
    }
    
    out->item = in->list[idx];
    out->valid = true;
}

