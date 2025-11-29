#include <stdio.h>
#include <math.h>
#include <assert.h>
#include <stdbool.h>
#include "../c_components/Negative.h"

static int float_eq(float a, float b, float eps) {
    return fabsf(a - b) <= eps;
}

static void test_Negative_case1(void) {
    // Inputs traced from components.json via source IDs
    // value = 3.8
    NegativeInput in = {
        .value = 3.8f
    };
    
    NegativeOutput out = {0};
    
    Negative_eval(&in, &out);
    
    float expected_result = -3.8f;
    assert(float_eq(out.result, expected_result, 1e-5f));
}

static void test_Negative_case2(void) {
    // Inputs traced from components.json via source IDs
    // value = 0.0
    NegativeInput in = {
        .value = 0.0f
    };
    
    NegativeOutput out = {0};
    
    Negative_eval(&in, &out);
    
    float expected_result = -0.0f;
    assert(float_eq(out.result, expected_result, 1e-5f));
}

static void test_Negative_case3(void) {
    // Inputs traced from components.json via source IDs
    // value = 2.5
    NegativeInput in = {
        .value = 2.5f
    };
    
    NegativeOutput out = {0};
    
    Negative_eval(&in, &out);
    
    float expected_result = -2.5f;
    assert(float_eq(out.result, expected_result, 1e-5f));
}

static void test_Negative_case4(void) {
    // Inputs traced from components.json via source IDs
    // value = 0.04
    NegativeInput in = {
        .value = 0.04f
    };
    
    NegativeOutput out = {0};
    
    Negative_eval(&in, &out);
    
    float expected_result = -0.04f;
    assert(float_eq(out.result, expected_result, 1e-5f));
}

static void test_Negative_case5(void) {
    // Inputs traced from components.json via source IDs
    // value = -3.8
    NegativeInput in = {
        .value = -3.8f
    };
    
    NegativeOutput out = {0};
    
    Negative_eval(&in, &out);
    
    float expected_result = 3.8f;
    assert(float_eq(out.result, expected_result, 1e-5f));
}

static void test_Negative_case6(void) {
    // Inputs traced from components.json via source IDs
    // value = 0.0
    NegativeInput in = {
        .value = 0.0f
    };
    
    NegativeOutput out = {0};
    
    Negative_eval(&in, &out);
    
    float expected_result = -0.0f;
    assert(float_eq(out.result, expected_result, 1e-5f));
}

void run_Negative_tests(void) {
    test_Negative_case1();
    test_Negative_case2();
    test_Negative_case3();
    test_Negative_case4();
    test_Negative_case5();
    test_Negative_case6();
    printf("Negative tests passed\n");
}
