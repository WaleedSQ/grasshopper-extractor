#include <stdio.h>
#include <math.h>
#include <assert.h>
#include <stdbool.h>
#include "../c_components/Subtraction.h"

static int float_eq(float a, float b, float eps) {
    return fabsf(a - b) <= eps;
}

static void test_Subtraction_case1(void) {
    // Inputs traced from components.json via source IDs
    // a = 3.8
    // b = 3.1
    SubtractionInput in = {
        .a = 3.8f,
        .b = 3.1f
    };
    
    SubtractionOutput out = {0};
    
    Subtraction_eval(&in, &out);
    
    float expected_result = 0.6999999999999997f;
    assert(float_eq(out.result, expected_result, 1e-5f));
}

static void test_Subtraction_case2(void) {
    // Inputs traced from components.json via source IDs
    // a = 10.0
    // b = 1
    SubtractionInput in = {
        .a = 10.0f,
        .b = 1.0f
    };
    
    SubtractionOutput out = {0};
    
    Subtraction_eval(&in, &out);
    
    float expected_result = 9.0f;
    assert(float_eq(out.result, expected_result, 1e-5f));
}

static void test_Subtraction_case3(void) {
    // Inputs traced from components.json via source IDs
    // a = 10.0
    // b = 1
    SubtractionInput in = {
        .a = 10.0f,
        .b = 1.0f
    };
    
    SubtractionOutput out = {0};
    
    Subtraction_eval(&in, &out);
    
    float expected_result = 9.0f;
    assert(float_eq(out.result, expected_result, 1e-5f));
}

static void test_Subtraction_case4(void) {
    // Inputs traced from components.json via source IDs
    // a = 4.5
    // b = 1.0
    SubtractionInput in = {
        .a = 4.5f,
        .b = 1.0f
    };
    
    SubtractionOutput out = {0};
    
    Subtraction_eval(&in, &out);
    
    float expected_result = 3.5f;
    assert(float_eq(out.result, expected_result, 1e-5f));
}

void run_Subtraction_tests(void) {
    test_Subtraction_case1();
    test_Subtraction_case2();
    test_Subtraction_case3();
    test_Subtraction_case4();
    printf("Subtraction tests passed\n");
}
