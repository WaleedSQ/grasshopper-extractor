#include <stdio.h>
#include <math.h>
#include <assert.h>
#include <stdbool.h>
#include "../c_components/Circle.h"

static int float_eq(float a, float b, float eps) {
    return fabsf(a - b) <= eps;
}

static void test_Circle_case1(void) {
    // Inputs traced from components.json via source IDs
    // plane = Plane from PlaneNormal "b8cbaed8-c6f7-4c1c-b9ba-88320b975081"
    //   origin = [0.0, 0.07000000000000002, 3.8]
    //   x_axis = [0, 1, 0]
    //   y_axis = [0, 0, 1]
    //   z_axis = [1, 0, 0]
    // radius = 0.1 (from persistent_data)
    CircleInput in = {
        .plane_origin = {0.0f, 0.07000000000000002f, 3.8f},
        .plane_x_axis = {0.0f, 1.0f, 0.0f},
        .plane_y_axis = {0.0f, 0.0f, 1.0f},
        .plane_z_axis = {1.0f, 0.0f, 0.0f},
        .radius = 0.1f
    };
    
    CircleOutput out = {0};
    
    Circle_eval(&in, &out);
    
    // Expected center from evaluation_results.json
    float expected_center[3] = {0.0f, 0.07000000000000002f, 3.8f};
    float expected_radius = 0.1f;
    
    for (int i = 0; i < 3; i++) {
        assert(float_eq(out.center[i], expected_center[i], 1e-5f));
    }
    assert(float_eq(out.radius, expected_radius, 1e-5f));
}

void run_Circle_tests(void) {
    test_Circle_case1();
    printf("Circle tests passed\n");
}
