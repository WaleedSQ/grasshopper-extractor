// Derived from evaluate_vector_xyz in gh_components_rotatingslats.py

#include "VectorXYZ.h"
#include <string.h>
#include <math.h>

void VectorXYZ_eval(const VectorXYZInput *in, VectorXYZOutput *out) {
    // Zero-initialize output
    memset(out, 0, sizeof(VectorXYZOutput));
    
    if (in->component_count > 0) {
        // Process array of components
        int count = in->component_count;
        if (count > VECTORXYZ_MAX_COUNT) {
            count = VECTORXYZ_MAX_COUNT;
        }
        
        for (int i = 0; i < count; i++) {
            float x = in->x_components[i];
            float y = in->y_components[i];
            float z = in->z_components[i];
            
            // GH Vector XYZ: vector = [x, y, z]
            out->vectors[i][0] = x;
            out->vectors[i][1] = y;
            out->vectors[i][2] = z;
            
            // GH Vector XYZ: compute length = sqrt(x² + y² + z²)
            out->lengths[i] = sqrtf(x * x + y * y + z * z);
        }
        
        out->vector_count = count;
        
        // Also set single outputs to first values for backward compatibility
        out->vector[0] = out->vectors[0][0];
        out->vector[1] = out->vectors[0][1];
        out->vector[2] = out->vectors[0][2];
        out->length = out->lengths[0];
    } else {
        // Single component mode (backward compatibility)
        float x = in->x_component;
        float y = in->y_component;
        float z = in->z_component;
        
        // GH Vector XYZ: vector = [x, y, z]
        out->vector[0] = x;
        out->vector[1] = y;
        out->vector[2] = z;
        
        // GH Vector XYZ: compute length = sqrt(x² + y² + z²)
        out->length = sqrtf(x * x + y * y + z * z);
        
        out->vector_count = 0;
    }
}

