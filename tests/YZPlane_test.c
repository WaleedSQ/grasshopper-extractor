#include <stdio.h>
#include <math.h>
#include <assert.h>
#include <stdbool.h>
#include "../c_components/YZPlane.h"

static int float_eq(float a, float b, float eps) {
    return fabsf(a - b) <= eps;
}

static void test_YZPlane_case1(void) {
    // Inputs traced from components.json via source IDs
    // origin = [0.0, 0.5, 2.0] (wired from Area Centroid "34529a8c-3dfd-4d96-865b-9e4cbfddad6c")
    YZPlaneInput in = {
        .origin = {0.0f, 0.5f, 2.0f}
    };
    
    YZPlaneOutput out = {0};
    
    YZPlane_eval(&in, &out);
    
    // Expected plane from evaluation_results.json
    float expected_origin[3] = {0.0f, 0.5f, 2.0f};
    float expected_x_axis[3] = {0.0f, 1.0f, 0.0f};
    float expected_y_axis[3] = {0.0f, 0.0f, 1.0f};
    float expected_z_axis[3] = {1.0f, 0.0f, 0.0f};
    
    for (int i = 0; i < 3; i++) {
        assert(float_eq(out.origin[i], expected_origin[i], 1e-5f));
        assert(float_eq(out.x_axis[i], expected_x_axis[i], 1e-5f));
        assert(float_eq(out.y_axis[i], expected_y_axis[i], 1e-5f));
        assert(float_eq(out.z_axis[i], expected_z_axis[i], 1e-5f));
    }
}

static void test_YZPlane_case2(void) {
    // Inputs traced from components.json via source IDs
    // origin = [0.0, 0.07000000000000002, 3.8] (wired from Area Centroid "01fd4f89-2b73-4e61-a51f-9c3df0c876fa")
    YZPlaneInput in = {
        .origin = {0.0f, 0.07000000000000002f, 3.8f}
    };
    
    YZPlaneOutput out = {0};
    
    YZPlane_eval(&in, &out);
    
    // Expected plane from evaluation_results.json
    float expected_origin[3] = {0.0f, 0.07000000000000002f, 3.8f};
    float expected_x_axis[3] = {0.0f, 1.0f, 0.0f};
    float expected_y_axis[3] = {0.0f, 0.0f, 1.0f};
    float expected_z_axis[3] = {1.0f, 0.0f, 0.0f};
    
    for (int i = 0; i < 3; i++) {
        assert(float_eq(out.origin[i], expected_origin[i], 1e-5f));
        assert(float_eq(out.x_axis[i], expected_x_axis[i], 1e-5f));
        assert(float_eq(out.y_axis[i], expected_y_axis[i], 1e-5f));
        assert(float_eq(out.z_axis[i], expected_z_axis[i], 1e-5f));
    }
}

void run_YZPlane_tests(void) {
    test_YZPlane_case1();
    test_YZPlane_case2();
    printf("YZPlane tests passed\n");
}
