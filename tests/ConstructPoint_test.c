#include <stdio.h>
#include <math.h>
#include <assert.h>
#include <stdbool.h>
#include "../c_components/ConstructPoint.h"

static int float_eq(float a, float b, float eps) {
    return fabsf(a - b) <= eps;
}

static void test_ConstructPoint_case1(void) {
    // Inputs traced from components.json via source IDs
    // x_coordinate = 0 (persistent_data)
    // y_coordinate = -2 (persistent_data)
    // z_coordinate = 7 (persistent_data)
    ConstructPointInput in = {
        .x = 0.0f,
        .y = -2.0f,
        .z = 7.0f
    };
    
    ConstructPointOutput out = {0};
    
    ConstructPoint_eval(&in, &out);
    
    float expected_point[3] = {0.0f, -2.0f, 7.0f};
    for (int i = 0; i < 3; i++) {
        assert(float_eq(out.point[i], expected_point[i], 1e-5f));
    }
}

static void test_ConstructPoint_case2(void) {
    // Inputs traced from components.json via source IDs
    // x_coordinate = 0 (persistent_data)
    // y_coordinate = 3 (persistent_data)
    // z_coordinate = -3 (persistent_data)
    ConstructPointInput in = {
        .x = 0.0f,
        .y = 3.0f,
        .z = -3.0f
    };
    
    ConstructPointOutput out = {0};
    
    ConstructPoint_eval(&in, &out);
    
    float expected_point[3] = {0.0f, 3.0f, -3.0f};
    for (int i = 0; i < 3; i++) {
        assert(float_eq(out.point[i], expected_point[i], 1e-5f));
    }
}

static void test_ConstructPoint_case3(void) {
    // Inputs traced from components.json via source IDs
    // x_coordinate = 0 (persistent_data, no sources)
    // y_coordinate = 4.5 (wired from slider "125e7c20-d243-4cdc-927b-568ceb6315b5")
    // z_coordinate = 4.0 (wired from slider "bd24b9c6-a1a1-42dd-a0be-e1c33df4146b")
    ConstructPointInput in = {
        .x = 0.0f,
        .y = 4.5f,
        .z = 4.0f
    };
    
    ConstructPointOutput out = {0};
    
    ConstructPoint_eval(&in, &out);
    
    float expected_point[3] = {0.0f, 4.5f, 4.0f};
    for (int i = 0; i < 3; i++) {
        assert(float_eq(out.point[i], expected_point[i], 1e-5f));
    }
}

static void test_ConstructPoint_case4(void) {
    // Inputs traced from components.json via source IDs
    // x_coordinate = 2.5 (wired from Division "4c2fdd4e-7313-4735-8688-1dbdf5aeaee0")
    // y_coordinate = 0.04 (wired from Division "eedce522-16c4-4b3a-8341-c26cc0b6bb91")
    // z_coordinate = 0 (persistent_data, no sources)
    ConstructPointInput in = {
        .x = 2.5f,
        .y = 0.04f,
        .z = 0.0f
    };
    
    ConstructPointOutput out = {0};
    
    ConstructPoint_eval(&in, &out);
    
    float expected_point[3] = {2.5f, 0.04f, 0.0f};
    for (int i = 0; i < 3; i++) {
        assert(float_eq(out.point[i], expected_point[i], 1e-5f));
    }
}

static void test_ConstructPoint_case5(void) {
    // Inputs traced from components.json via source IDs
    // x_coordinate = -2.5 (wired from Division "8cb00f94-7bbb-49d9-8065-df2645a32790")
    // y_coordinate = -0.04 (wired from Division "a7dd54c8-0ce7-4884-913e-10ac0e1336b4")
    // z_coordinate = 0 (persistent_data, no sources)
    ConstructPointInput in = {
        .x = -2.5f,
        .y = -0.04f,
        .z = 0.0f
    };
    
    ConstructPointOutput out = {0};
    
    ConstructPoint_eval(&in, &out);
    
    float expected_point[3] = {-2.5f, -0.04f, 0.0f};
    for (int i = 0; i < 3; i++) {
        assert(float_eq(out.point[i], expected_point[i], 1e-5f));
    }
}

void run_ConstructPoint_tests(void) {
    test_ConstructPoint_case1();
    test_ConstructPoint_case2();
    test_ConstructPoint_case3();
    test_ConstructPoint_case4();
    test_ConstructPoint_case5();
    printf("ConstructPoint tests passed\n");
}

