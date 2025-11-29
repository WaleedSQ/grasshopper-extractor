#include <stdio.h>
#include <math.h>
#include "config.h"
#include "sun_group.h"
#include "slats_group.h"
#include "direction_group.h"
#include "targets_group.h"
#include "core_group.h"

int main(void) {
    // Use default configuration
    ShadeConfig cfg = DEFAULT_CONFIG;
    
    // Declare output structures
    SunGroupOutput sun;
    SlatsGroupOutput slats;
    DirectionGroupOutput dir;
    TargetsGroupOutput targets;
    CoreGroupOutput core;
    
    // Evaluate groups in order
    printf("========================================\n");
    printf("Evaluating sun group...\n");
    printf("========================================\n");
    sun_group_eval(&cfg, &sun);
    printf("  Sun position (sun_pt): (%.6f, %.6f, %.6f)\n", sun.sun_pt[0], sun.sun_pt[1], sun.sun_pt[2]);
    printf("  Sun vector: (%.6f, %.6f, %.6f)\n", sun.sun_vector[0], sun.sun_vector[1], sun.sun_vector[2]);
    float sun_pt_len = sqrtf(sun.sun_pt[0]*sun.sun_pt[0] + sun.sun_pt[1]*sun.sun_pt[1] + sun.sun_pt[2]*sun.sun_pt[2]);
    printf("  Sun position magnitude: %.6f\n", sun_pt_len);
    
    printf("\n========================================\n");
    printf("Evaluating slats group...\n");
    printf("========================================\n");
    slats_group_eval(&cfg, &slats);
    printf("  Generated %d slats\n", slats.slat_count);
    for (int i = 0; i < slats.slat_count && i < 3; i++) {
        printf("  Slat %d rectangle corners:\n", i);
        for (int j = 0; j < 4; j++) {
            printf("    Corner %d: (%.6f, %.6f, %.6f)\n", 
                   j, slats.slat_rectangles[i][j][0], 
                   slats.slat_rectangles[i][j][1], 
                   slats.slat_rectangles[i][j][2]);
        }
    }
    
    printf("\n========================================\n");
    printf("Evaluating direction group...\n");
    printf("========================================\n");
    direction_group_eval(&cfg, &slats, &dir);
    printf("  Plane origin: (%.6f, %.6f, %.6f)\n", 
           dir.plane_origin[0], dir.plane_origin[1], dir.plane_origin[2]);
    printf("  Plane X-axis: (%.6f, %.6f, %.6f)\n", 
           dir.plane_x_axis[0], dir.plane_x_axis[1], dir.plane_x_axis[2]);
    printf("  Plane Y-axis: (%.6f, %.6f, %.6f)\n", 
           dir.plane_y_axis[0], dir.plane_y_axis[1], dir.plane_y_axis[2]);
    printf("  Plane Z-axis: (%.6f, %.6f, %.6f)\n", 
           dir.plane_z_axis[0], dir.plane_z_axis[1], dir.plane_z_axis[2]);
    
    printf("\n========================================\n");
    printf("Evaluating targets group...\n");
    printf("========================================\n");
    targets_group_eval(&cfg, &targets);
    printf("  Generated %d target points\n", targets.target_count);
    for (int i = 0; i < targets.target_count && i < 5; i++) {
        printf("  Target %d: (%.6f, %.6f, %.6f)\n", 
               i, targets.target_points[i][0], 
               targets.target_points[i][1], 
               targets.target_points[i][2]);
    }
    
    printf("\n========================================\n");
    printf("Evaluating core group...\n");
    printf("========================================\n");
    core_group_eval(&cfg, &sun, &slats, &dir, &targets, &core);
    
    printf("\nEvaluation complete!\n");
    return 0;
}

