#include <stdio.h>
#include <math.h>
#include <assert.h>
#include <stdbool.h>
#include "../c_components/UnitY.h"

static int float_eq(float a, float b, float eps) {
    return fabsf(a - b) <= eps;
}

static void test_UnitY_case1(void) {
    // Inputs traced from components.json via source IDs
    // Factor = -0.07 (wired from Series "306c324a-3b04-4c46-bd5a-d11cacfe8fdb" first value)
    UnitYInput in = {
        .factor = -0.07f
    };
    
    UnitYOutput out = {0};
    
    UnitY_eval(&in, &out);
    
    float expected_vector[3] = {0.0f, -0.07f, 0.0f};
    for (int i = 0; i < 3; i++) {
        assert(float_eq(out.unit_vector[i], expected_vector[i], 1e-5f));
    }
}

static void test_UnitY_case2(void) {
    // Inputs traced from components.json via source IDs
    // Factor = 0.0 (wired from Negative "1288cc78-451b-423d-bbc4-2e1a268f1389" first value which is -0.0)
    UnitYInput in = {
        .factor = 0.0f
    };
    
    UnitYOutput out = {0};
    
    UnitY_eval(&in, &out);
    
    float expected_vector[3] = {0.0f, 0.0f, 0.0f};
    for (int i = 0; i < 3; i++) {
        assert(float_eq(out.unit_vector[i], expected_vector[i], 1e-5f));
    }
}

void run_UnitY_tests(void) {
    test_UnitY_case1();
    test_UnitY_case2();
    printf("UnitY tests passed\n");
}
