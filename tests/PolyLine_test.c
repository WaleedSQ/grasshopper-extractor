#include <stdio.h>
#include <math.h>
#include <assert.h>
#include <stdbool.h>
#include "../c_components/PolyLine.h"

static int float_eq(float a, float b, float eps) {
    return fabsf(a - b) <= eps;
}

static void test_PolyLine_case1(void) {
    // Inputs traced from components.json via source IDs
    // vertices = 10 points from Series "0b4bf936-2e3a-417f-aaf0-61220fcefd66"
    // closed = False (persistent_data)
    PolyLineInput in = {0};
    in.vertex_count = 10;
    in.closed = false;
    
    // Vertices from evaluation_results.json output
    float vertices[10][3] = {
        {0.0f, 4.5f, 4.0f},
        {0.0f, 4.111111111111111f, 4.0f},
        {0.0f, 3.7222222222222223f, 4.0f},
        {0.0f, 3.333333333333333f, 4.0f},
        {0.0f, 2.9444444444444446f, 4.0f},
        {0.0f, 2.5555555555555554f, 4.0f},
        {0.0f, 2.1666666666666665f, 4.0f},
        {0.0f, 1.7777777777777777f, 4.0f},
        {0.0f, 1.3888888888888888f, 4.0f},
        {0.0f, 1.0f, 4.0f}
    };
    
    for (int i = 0; i < 10; i++) {
        in.vertices[i][0] = vertices[i][0];
        in.vertices[i][1] = vertices[i][1];
        in.vertices[i][2] = vertices[i][2];
    }
    
    PolyLineOutput out = {0};
    
    PolyLine_eval(&in, &out);
    
    // Verify output matches input (PolyLine just copies)
    assert(out.vertex_count == 10);
    assert(out.closed == false);
    for (int i = 0; i < 10; i++) {
        assert(float_eq(out.vertices[i][0], vertices[i][0], 1e-5f));
        assert(float_eq(out.vertices[i][1], vertices[i][1], 1e-5f));
        assert(float_eq(out.vertices[i][2], vertices[i][2], 1e-5f));
    }
}

static void test_PolyLine_case2(void) {
    // Inputs traced from components.json via source IDs
    // vertices = 10 points from Series
    // closed = False (persistent_data)
    PolyLineInput in = {0};
    in.vertex_count = 10;
    in.closed = false;
    
    // Vertices from evaluation_results.json output
    float vertices[10][3] = {
        {0.0f, 0.07000000000000002f, 3.1f},
        {0.0f, 0.07000000000000002f, 3.177777777777778f},
        {0.0f, 0.07000000000000002f, 3.2555555555555555f},
        {0.0f, 0.07000000000000002f, 3.3333333333333335f},
        {0.0f, 0.07000000000000002f, 3.411111111111111f},
        {0.0f, 0.07000000000000002f, 3.488888888888889f},
        {0.0f, 0.07000000000000002f, 3.5666666666666664f},
        {0.0f, 0.07000000000000002f, 3.6444444444444444f},
        {0.0f, 0.07000000000000002f, 3.722222222222222f},
        {0.0f, 0.07000000000000002f, 3.8f}
    };
    
    for (int i = 0; i < 10; i++) {
        in.vertices[i][0] = vertices[i][0];
        in.vertices[i][1] = vertices[i][1];
        in.vertices[i][2] = vertices[i][2];
    }
    
    PolyLineOutput out = {0};
    
    PolyLine_eval(&in, &out);
    
    // Verify output matches input (PolyLine just copies)
    assert(out.vertex_count == 10);
    assert(out.closed == false);
    for (int i = 0; i < 10; i++) {
        assert(float_eq(out.vertices[i][0], vertices[i][0], 1e-5f));
        assert(float_eq(out.vertices[i][1], vertices[i][1], 1e-5f));
        assert(float_eq(out.vertices[i][2], vertices[i][2], 1e-5f));
    }
}

void run_PolyLine_tests(void) {
    test_PolyLine_case1();
    test_PolyLine_case2();
    printf("PolyLine tests passed\n");
}
