#include <stdio.h>
#include <math.h>
#include <assert.h>
#include <stdbool.h>
#include "../c_components/Series.h"

static int float_eq(float a, float b, float eps) {
    return fabsf(a - b) <= eps;
}

static void test_Series_case1(void) {
    // Inputs traced from components.json via source IDs
    // Start = -3.8 (wired from Negative "f8fdffb7-41e7-43c7-93a7-44bdc965ed27")
    // Step = 0.07777777777777775 (wired from Division "20f5465a-8288-49ad-acd1-2eb24e1f8765")
    // Count = 10 (wired from slider "537142d8-e672-4d12-8254-46dbe1e3c7ef")
    SeriesInput in = {
        .start = -3.8f,
        .step = 0.07777777777777775f,
        .count = 10
    };
    
    SeriesOutput out = {0};
    
    Series_eval(&in, &out);
    
    assert(out.actual_count == 10);
    // Verify series values
    float expected_series[10] = {
        -3.8f,
        -3.722222222222222f,
        -3.6444444444444444f,
        -3.5666666666666664f,
        -3.488888888888889f,
        -3.411111111111111f,
        -3.3333333333333335f,
        -3.2555555555555555f,
        -3.177777777777778f,
        -3.1f
    };
    for (int i = 0; i < 10 && i < out.actual_count; i++) {
        assert(float_eq(out.series[i], expected_series[i], 1e-5f));
    }
}

static void test_Series_case2(void) {
    // Inputs traced from components.json via source IDs
    // Start = 0 (persistent_data, no sources)
    // Step = 0.3888888888888889 (wired from Division "133aa1b3-f899-4543-88d4-cde6da741d95")
    // Count = 10 (wired from slider "537142d8-e672-4d12-8254-46dbe1e3c7ef")
    SeriesInput in = {
        .start = 0.0f,
        .step = 0.3888888888888889f,
        .count = 10
    };
    
    SeriesOutput out = {0};
    
    Series_eval(&in, &out);
    
    assert(out.actual_count == 10);
    // Verify series values
    float expected_series[10] = {
        0.0f,
        0.3888888888888889f,
        0.7777777777777778f,
        1.1666666666666667f,
        1.5555555555555556f,
        1.9444444444444444f,
        2.3333333333333335f,
        2.7222222222222223f,
        3.111111111111111f,
        3.5f
    };
    for (int i = 0; i < 10 && i < out.actual_count; i++) {
        assert(float_eq(out.series[i], expected_series[i], 1e-5f));
    }
}

static void test_Series_case3(void) {
    // Inputs traced from components.json via source IDs
    // Start = -0.07 (wired from slider "507b14ee-692b-41df-973f-6bfef76514c2")
    // Step = 0 (wired from Negative "bdac63ee-60a4-4873-8860-06e887053c0e" which negates 0)
    // Count = 10 (wired from slider "537142d8-e672-4d12-8254-46dbe1e3c7ef")
    SeriesInput in = {
        .start = -0.07f,
        .step = 0.0f,
        .count = 10
    };
    
    SeriesOutput out = {0};
    
    Series_eval(&in, &out);
    
    assert(out.actual_count == 10);
    // Verify series values (all should be -0.07 since step is 0)
    float expected_series[10] = {
        -0.07f,
        -0.07f,
        -0.07f,
        -0.07f,
        -0.07f,
        -0.07f,
        -0.07f,
        -0.07f,
        -0.07f,
        -0.07f
    };
    for (int i = 0; i < 10 && i < out.actual_count; i++) {
        assert(float_eq(out.series[i], expected_series[i], 1e-5f));
    }
}

void run_Series_tests(void) {
    test_Series_case1();
    test_Series_case2();
    test_Series_case3();
    printf("Series tests passed\n");
}

