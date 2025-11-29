#include <stdio.h>
#include <math.h>
#include <assert.h>
#include <stdbool.h>
#include "../c_components/CalculateHOY.h"

static int float_eq(float a, float b, float eps) {
    return fabsf(a - b) <= eps;
}

static void test_CalculateHOY_case1(void) {
    // Inputs traced from components.json via source IDs
    // month = 8.0 (wired from slider "86379f02-2481-4a60-bc43-5e5c81ecc838")
    // day = 13.0 (wired from slider "8a457e4b-7089-459f-a9f8-bf07defdca0d")
    // hour = 11.0 (wired from slider "bf058e10-b0e8-4f60-b1c9-0bc02970dfa7")
    // minute = 0 (persistent_data, no sources)
    CalculateHOYInput in = {
        .month = 8,
        .day = 13,
        .hour = 11,
        .minute = 0
    };
    
    CalculateHOYOutput out = {0};
    
    CalculateHOY_eval(&in, &out);
    
    // Expected hoy = 5387 (from evaluation_results.json)
    assert(out.hoy == 5387);
}

void run_CalculateHOY_tests(void) {
    test_CalculateHOY_case1();
    printf("CalculateHOY tests passed\n");
}
