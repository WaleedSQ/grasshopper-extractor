#include <stdio.h>
#include <math.h>
#include <assert.h>
#include <stdbool.h>
#include "../c_components/Line.h"

static int float_eq(float a, float b, float eps) {
    return fabsf(a - b) <= eps;
}

static void test_Line_case1(void) {
    // Inputs traced from components.json via source IDs
    // start_point = [0.0, 0.07000000000000002, 3.8]
    // end_point = [0.0, 4.5, 4.0]
    LineInput in = {
        .start_point = {0.0f, 0.07000000000000002f, 3.8f},
        .end_point = {0.0f, 4.5f, 4.0f},
        .use_two_points = true,
        .direction = {0.0f, 0.0f, 0.0f},
        .length = 0.0f
    };
    
    LineOutput out = {0};
    
    Line_eval(&in, &out);
    
    float expected_start[3] = {0.0f, 0.07000000000000002f, 3.8f};
    float expected_end[3] = {0.0f, 4.5f, 4.0f};
    for (int i = 0; i < 3; i++) {
        assert(float_eq(out.start[i], expected_start[i], 1e-5f));
        assert(float_eq(out.end[i], expected_end[i], 1e-5f));
    }
}

static void test_Line_case2(void) {
    // Inputs traced from components.json via source IDs
    // start_point = [0.0, 0.07000000000000002, 3.8]
    // end_point = [33219.83722907802, -61164.45101596277, 71804.52272172064]
    LineInput in = {
        .start_point = {0.0f, 0.07000000000000002f, 3.8f},
        .end_point = {33219.83722907802f, -61164.45101596277f, 71804.52272172064f},
        .use_two_points = true,
        .direction = {0.0f, 0.0f, 0.0f},
        .length = 0.0f
    };
    
    LineOutput out = {0};
    
    Line_eval(&in, &out);
    
    float expected_start[3] = {0.0f, 0.07000000000000002f, 3.8f};
    float expected_end[3] = {33219.83722907802f, -61164.45101596277f, 71804.52272172064f};
    for (int i = 0; i < 3; i++) {
        assert(float_eq(out.start[i], expected_start[i], 1e-5f));
        assert(float_eq(out.end[i], expected_end[i], 1e-5f));
    }
}

static void test_Line_case3(void) {
    // Inputs traced from components.json via source IDs
    // start_point = [0.0, 0.16989824417738197, 3.8045100787439]
    // end_point = [0.0, 0.005152775447297975, 3.8761238298288405]
    LineInput in = {
        .start_point = {0.0f, 0.16989824417738197f, 3.8045100787439f},
        .end_point = {0.0f, 0.005152775447297975f, 3.8761238298288405f},
        .use_two_points = true,
        .direction = {0.0f, 0.0f, 0.0f},
        .length = 0.0f
    };
    
    LineOutput out = {0};
    
    Line_eval(&in, &out);
    
    float expected_start[3] = {0.0f, 0.16989824417738197f, 3.8045100787439f};
    float expected_end[3] = {0.0f, 0.005152775447297975f, 3.8761238298288405f};
    for (int i = 0; i < 3; i++) {
        assert(float_eq(out.start[i], expected_start[i], 1e-5f));
        assert(float_eq(out.end[i], expected_end[i], 1e-5f));
    }
}

void run_Line_tests(void) {
    test_Line_case1();
    test_Line_case2();
    test_Line_case3();
    printf("Line tests passed\n");
}
