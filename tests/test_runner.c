#include <stdio.h>

// Forward declarations of per-component test runners
void run_Angle_tests(void);
void run_Area_tests(void);
void run_Box2Pt_tests(void);
void run_CalculateHOY_tests(void);
void run_Circle_tests(void);
void run_ConstructPlane_tests(void);
void run_ConstructPoint_tests(void);
void run_CurveCurve_tests(void);
void run_Degrees_tests(void);
void run_Division_tests(void);
void run_DownloadWeather_tests(void);
void run_ExplodeTree_tests(void);
void run_ImportEPW_tests(void);
void run_Line_tests(void);
void run_ListItem_tests(void);
void run_Move_tests(void);
void run_Negative_tests(void);
void run_PlaneNormal_tests(void);
void run_PolyLine_tests(void);
void run_Project_tests(void);
void run_Rectangle2Pt_tests(void);
void run_Rotate_tests(void);
void run_Series_tests(void);
void run_Subtraction_tests(void);
void run_SunPath_tests(void);
void run_UnitY_tests(void);
void run_UnitZ_tests(void);
void run_Vector2Pt_tests(void);
void run_YZPlane_tests(void);

int main(void) {
    printf("Running component tests...\n");
    printf("========================\n\n");

    run_Angle_tests();
    run_Area_tests();
    run_Box2Pt_tests();
    run_CalculateHOY_tests();
    run_Circle_tests();
    run_ConstructPlane_tests();
    run_ConstructPoint_tests();
    run_CurveCurve_tests();
    run_Degrees_tests();
    run_Division_tests();
    run_DownloadWeather_tests();
    run_ExplodeTree_tests();
    run_ImportEPW_tests();
    run_Line_tests();
    run_ListItem_tests();
    run_Move_tests();
    run_Negative_tests();
    run_PlaneNormal_tests();
    run_PolyLine_tests();
    run_Project_tests();
    run_Rectangle2Pt_tests();
    run_Rotate_tests();
    run_Series_tests();
    run_Subtraction_tests();
    run_SunPath_tests();
    run_UnitY_tests();
    run_UnitZ_tests();
    run_Vector2Pt_tests();
    run_YZPlane_tests();

    printf("\n========================\n");
    printf("All tests completed.\n");
    return 0;
}
