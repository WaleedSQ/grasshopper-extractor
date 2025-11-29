#include <stdio.h>
#include <math.h>
#include <assert.h>
#include <stdbool.h>
#include "../c_components/UnitZ.h"

static int float_eq(float a, float b, float eps) {
    return fabsf(a - b) <= eps;
}

static void test_UnitZ_case1(void) {
    // Inputs traced from components.json via source IDs
    // Factor = 3.8 (wired from Negative "3a96e7fa-3a91-4dd9-a965-18049ca7617e" first value)
    UnitZInput in = {
        .factor = 3.8f
    };
    
    UnitZOutput out = {0};
    
    UnitZ_eval(&in, &out);
    
    float expected_vector[3] = {0.0f, 0.0f, 3.8f};
    for (int i = 0; i < 3; i++) {
        assert(float_eq(out.unit_vector[i], expected_vector[i], 1e-5f));
    }
}

void run_UnitZ_tests(void) {
    test_UnitZ_case1();
    printf("UnitZ tests passed\n");
}
