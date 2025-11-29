#include <stdio.h>
#include <math.h>
#include <assert.h>
#include <stdbool.h>
#include "../c_components/Division.h"

static int float_eq(float a, float b, float eps) {
    return fabsf(a - b) <= eps;
}

static void test_Division_case1(void) {
    // Inputs traced from components.json via source IDs
    // a = 5.0
    // b = 2
    DivisionInput in = {
        .a = 5.0f,
        .b = 2.0f
    };
    
    DivisionOutput out = {0};
    
    Division_eval(&in, &out);
    
    float expected_result = 2.5f;
    assert(float_eq(out.result, expected_result, 1e-5f));
}

static void test_Division_case2(void) {
    // Inputs traced from components.json via source IDs
    // a = 0.08
    // b = 2
    DivisionInput in = {
        .a = 0.08f,
        .b = 2.0f
    };
    
    DivisionOutput out = {0};
    
    Division_eval(&in, &out);
    
    float expected_result = 0.04f;
    assert(float_eq(out.result, expected_result, 1e-5f));
}

static void test_Division_case3(void) {
    // Inputs traced from components.json via source IDs
    // a = 0.6999999999999997
    // b = 9.0
    DivisionInput in = {
        .a = 0.6999999999999997f,
        .b = 9.0f
    };
    
    DivisionOutput out = {0};
    
    Division_eval(&in, &out);
    
    float expected_result = 0.07777777777777775f;
    assert(float_eq(out.result, expected_result, 1e-5f));
}

static void test_Division_case4(void) {
    // Inputs traced from components.json via source IDs
    // a = 3.5
    // b = 9.0
    DivisionInput in = {
        .a = 3.5f,
        .b = 9.0f
    };
    
    DivisionOutput out = {0};
    
    Division_eval(&in, &out);
    
    float expected_result = 0.3888888888888889f;
    assert(float_eq(out.result, expected_result, 1e-5f));
}

void run_Division_tests(void) {
    test_Division_case1();
    test_Division_case2();
    test_Division_case3();
    test_Division_case4();
    printf("Division tests passed\n");
}
