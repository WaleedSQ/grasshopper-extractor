#include <stdio.h>
#include <math.h>
#include <assert.h>
#include <stdbool.h>
#include "../c_components/Degrees.h"

static int float_eq(float a, float b, float eps) {
    return fabsf(a - b) <= eps;
}

static void test_Degrees_case1(void) {
    // Inputs traced from components.json via source IDs
    // radians = 0.4100522259871638
    DegreesInput in = {
        .radians = 0.4100522259871638f
    };
    
    DegreesOutput out = {0};
    
    Degrees_eval(&in, &out);
    
    float expected_degrees = 23.49426192900914f;
    assert(float_eq(out.degrees, expected_degrees, 1e-5f));
}

void run_Degrees_tests(void) {
    test_Degrees_case1();
    printf("Degrees tests passed\n");
}
