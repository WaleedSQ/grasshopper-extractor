#include <stdio.h>
#include <math.h>
#include <assert.h>
#include <stdbool.h>
#include "../c_components/PlaneNormal.h"

static int float_eq(float a, float b, float eps) {
    return fabsf(a - b) <= eps;
}

static void test_PlaneNormal_case1(void) {
    // Inputs traced from components.json via source IDs
    // origin = [0.0, 0.07000000000000002, 3.8] (wired from Area Centroid "01fd4f89-2b73-4e61-a51f-9c3df0c876fa")
    // z_axis = [0.0, -1.0, 0.0] (wired from UnitY "def742ff-b2bc-4fcd-833f-523d99cca69d")
    PlaneNormalInput in = {
        .origin = {0.0f, 0.07000000000000002f, 3.8f},
        .z_axis = {0.0f, -1.0f, 0.0f}
    };
    
    PlaneNormalOutput out = {0};
    
    PlaneNormal_eval(&in, &out);
    
    // Expected plane from evaluation_results.json
    float expected_origin[3] = {0.0f, 0.07000000000000002f, 3.8f};
    float expected_x_axis[3] = {1.0f, 0.0f, 0.0f};
    float expected_y_axis[3] = {0.0f, 0.0f, 1.0f};
    float expected_z_axis[3] = {0.0f, -1.0f, 0.0f};
    
    for (int i = 0; i < 3; i++) {
        assert(float_eq(out.origin[i], expected_origin[i], 1e-5f));
        assert(float_eq(out.x_axis[i], expected_x_axis[i], 1e-5f));
        assert(float_eq(out.y_axis[i], expected_y_axis[i], 1e-5f));
        assert(float_eq(out.z_axis[i], expected_z_axis[i], 1e-5f));
    }
}

static void test_PlaneNormal_case2(void) {
    // Inputs traced from components.json via source IDs
    // origin = [0.0, 0.07000000000000002, 3.1] (wired from Area Centroid)
    // z_axis = [-1.0, 0.0, 0.0] (wired from UnitY)
    PlaneNormalInput in = {
        .origin = {0.0f, 0.07000000000000002f, 3.1f},
        .z_axis = {-1.0f, 0.0f, 0.0f}
    };
    
    PlaneNormalOutput out = {0};
    
    PlaneNormal_eval(&in, &out);
    
    // Expected plane from evaluation_results.json
    float expected_origin[3] = {0.0f, 0.07000000000000002f, 3.1f};
    float expected_x_axis[3] = {0.0f, 1.0f, 0.0f};
    float expected_y_axis[3] = {0.0f, 0.0f, -1.0f};
    float expected_z_axis[3] = {-1.0f, 0.0f, 0.0f};
    
    for (int i = 0; i < 3; i++) {
        assert(float_eq(out.origin[i], expected_origin[i], 1e-5f));
        assert(float_eq(out.x_axis[i], expected_x_axis[i], 1e-5f));
        assert(float_eq(out.y_axis[i], expected_y_axis[i], 1e-5f));
        assert(float_eq(out.z_axis[i], expected_z_axis[i], 1e-5f));
    }
}

void run_PlaneNormal_tests(void) {
    test_PlaneNormal_case1();
    test_PlaneNormal_case2();
    printf("PlaneNormal tests passed\n");
}
