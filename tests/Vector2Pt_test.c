#include <stdio.h>
#include <math.h>
#include <assert.h>
#include <stdbool.h>
#include "../c_components/Vector2Pt.h"

static int float_eq(float a, float b, float eps) {
    return fabsf(a - b) <= eps;
}

static void test_Vector2Pt_case1(void) {
    // Inputs traced from components.json via source IDs
    // point_a = [0, -0.07, 0]
    // point_b = [0, 0, 3.8]
    // unitize = False
    Vector2PtInput in = {
        .point_a = {0.0f, -0.07f, 0.0f},
        .point_b = {0.0f, 0.0f, 3.8f},
        .unitize = false
    };
    
    Vector2PtOutput out = {0};
    
    Vector2Pt_eval(&in, &out);
    
    float expected_vector[3] = {0.0f, 0.07f, 3.8f};
    for (int i = 0; i < 3; i++) {
        assert(float_eq(out.vector[i], expected_vector[i], 1e-5f));
    }
}

void run_Vector2Pt_tests(void) {
    test_Vector2Pt_case1();
    printf("Vector2Pt tests passed\n");
}
