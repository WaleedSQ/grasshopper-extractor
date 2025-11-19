# Rotatingslats Evaluation Results

## Evaluation Chain (Topological Order)

Components evaluated in dependency order, from early inputs to final outputs.

| # | Component GUID | Type | Name/NickName | Output |
|---|----------------|------|---------------|--------|
| 1 | `4fa54506...` | Unit Z | `Unit Z.Unit vector` | `[[0.0, 0.0, 3.8], [0.0, 0.0, 3.722222222222222], [0.0, 0.0, 3.6444444444444444], [0.0, 0.0, 3.566...` |
| 2 | `6b94f6c4...` | List Item | `List Item.i` | `None` |
| 3 | `0460d28c...` | Divide Length | `DL.Points` | `[[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [2.0, 0.0, 0.0]]` |
| 4 | `1a00d7ad...` | Polar Array | `Polar Array.Geometry` | `[{'type': 'rectangle', 'plane': {'origin': [0, 0, 0], 'x_axis': [1, 0, 0], 'y_axis': [0, 1, 0], '...` |
| 5 | `b94e42e9...` | Polygon | `Polygon.Polygon` | `{'polygon': 'polygon_geometry', 'vertices': [[3.0, 0.0, 0.0], [2.121320343559643, 2.1213203435596...` |
| 6 | `c8dfe19f...` | Number Slider | `Slat width` | `{'Value': 0.08}` |
| 7 | `80fd9f48...` | Move | `Targets.Geometry` | `[[11.327429598006665, -31.846834162334087, 4.0], [11.327429598006665, -31.457945273445198, 4.0], ...` |
| 8 | `84214afe...` | Vector 2Pt | `Vector 2Pt.Vector` | `[1.14805029709527, -2.77163859753386, 0.0]` |
| 9 | `8a96679d...` | Negative | `-.Result` | `-2.5` |
| 10 | `95282afd...` | Negative | `-.Result` | `-4.5` |
| 11 | `c4c92669...` | MD Slider | `MD Slider` | `{'Value': 0.5}` |
| 12 | `f78fb52e...` | List Item | `List Item.i` | `None` |
| 13 | `dbc236d4...` | Rectangle 2Pt | `Rectangle 2Pt.Rectangle` | `{'type': 'rectangle', 'plane': {'origin': [0, 0, 0], 'x_axis': [1, 0, 0], 'y_axis': [0, 1, 0], 'z...` |
| 14 | `23900bd5...` | Angle | `Angle.Angle` | `0.0` |
| 15 | `71c9ab9c...` | Number Slider | `Number of orientations` | `{'Value': 8.0}` |
| 16 | `638a56be...` | Plane Normal | `Plane Normal.Plane` | `{'origin': 0.0, 'normal': {'origin': [0.0, 0.0, 0.0], 'x_axis': [1.0, 0.0, 0.0], 'y_axis': [0.0, ...` |
| 17 | `e898f4cb...` | Line | `Out Ray.Line` | `{'start': [0.0, 0.0, 0.0], 'end': [33219.837229, -61164.521016, 71800.722722], 'direction': [3321...` |
| 18 | `6ce8bcba...` | Point On Curve | `Point On Curve` | `{'Point': [1.14805029709527, -2.77163859753386, 0.0]}` |
| 19 | `902866aa...` | Construct Point | `CP.Point` | `[2.5, 0.04, 0.0]` |
| 20 | `2587762a...` | Move | `Targets.Geometry` | `[[0.0, -4.5, 4.0], [0.0, -4.111111111111111, 4.0], [0.0, -3.7222222222222223, 4.0], [0.0, -3.3333...` |
| 21 | `ea2c7d7f...` | Number Slider | `Slats height (threshold)` | `{'Value': 3.1}` |
| 22 | `577ce3f3...` | Construct Point | `p1` | `{'Point': [0.0, -2.0, 7.0]}` |
| 23 | `6c807a4e...` | Subtraction | `-.Result` | `9.0` |
| 24 | `eedce522...` | Division | `/.Result` | `0.04` |
| 25 | `7de8f856...` | List Item | `LI.i` | `None` |
| 26 | `125e7c20...` | Number Slider | `Last target from slats` | `{'Value': 4.5}` |
| 27 | `dac68df4...` | Number Slider | `Room - Distance from origen` | `{'Value': 29.6}` |
| 28 | `3a96e7fa...` | Negative | `-.Result` | `[3.8, 3.722222222222222, 3.6444444444444444, 3.5666666666666664, 3.488888888888889, 3.41111111111...` |
| 29 | `e8c7faf9...` | List Item | `LI.i` | `None` |
| 30 | `01fd4f89...` | Area | `Area.Centroid` | `[0.0, 0.0, 0.0]` |
| 31 | `4218a4e5...` | Move | `Slats original.Geometry` | `{'type': 'rectangle', 'plane': {'origin': [0, 0, 0], 'x_axis': [1, 0, 0], 'y_axis': [0, 1, 0], 'z...` |
| 32 | `e41d5eba...` | Evaluate Surface | `Evaluate Surface.Normal` | `[0.0, 0.0, 1.0]` |
| 33 | `4d5670e5...` | Degrees | `Degrees.Degrees` | `0.0` |
| 34 | `507b14ee...` | Number Slider | `Distance from window` | `{'Value': -0.07}` |
| 35 | `306c324a...` | Series | `Series.Series` | `[-0.07, -0.07, -0.07, -0.07, -0.07, -0.07, -0.07, -0.07, -0.07, -0.07]` |
| 36 | `24f7f310...` | List Item | `LI.i` | `None` |
| 37 | `0fb443ce...` | Construct Point | `p1.Point` | `[0.0, -2.0, 7.0]` |
| 38 | `2cc32a65...` | Construct Point | `p1.Point` | `[0.0, 3.0, -3.0]` |
| 39 | `65a37667...` | PolyLine | `PolyLine.Polyline` | `None` |
| 40 | `370f6ae5...` | Negative | `-.Result` | `-0.04` |
| 41 | `e7683176...` | Polar Array | `PA.Geometry` | `[[[0.0, -4.5, 4.0], [0.0, -4.111111111111111, 4.0], [0.0, -3.7222222222222223, 4.0], [0.0, -3.333...` |
| 42 | `ef17623c...` | Construct Point | `CP.Point` | `[-2.5, -0.04, 0.0]` |
| 43 | `bd24b9c6...` | Number Slider | `Targets Height` | `{'Value': 4.0}` |
| 44 | `08edbcda...` | Number Slider | `Horizontal shift between slats` | `{'Value': 0.0}` |
| 45 | `d0668a07...` | Amplitude | `Amplitude.Vector` | `[11.327429598006665, -27.346834162334087, 0.0]` |
| 46 | `4b0092c3...` | Plane Normal | `Plane Normal.Plane` | `{'origin': [0.0, 0.0, 0.0], 'normal': {'points': [[11.327429598006665, -31.846834162334087, 4.0],...` |
| 47 | `160dcd76...` | Series | `Series.Series` | `[-3.8, -3.722222222222222, -3.6444444444444444, -3.5666666666666664, -3.488888888888889, -3.41111...` |
| 48 | `34529a8c...` | Area | `Area.Centroid` | `[0.0, 0.0, 0.0]` |
| 49 | `def742ff...` | PolyLine | `PolyLine.Polyline` | `None` |
| 50 | `bdac63ee...` | Negative | `-.Result` | `-0.0` |
| 51 | `db399c50...` | Mirror | `Mirror.Geometry` | `{'polygon': 'polygon_geometry', 'vertices': [[-1.1480502970952695, 2.77163859753386, 0.0], [1.148...` |
| 52 | `07dcee6c...` | Vector 2Pt | `Vector 2Pt.Vector` | `[[0.0, 0.07, 3.8], [0.0, 0.07, 3.722222222222222], [0.0, 0.07, 3.6444444444444444], [0.0, 0.07, 3...` |
| 53 | `a7d2817a...` | Number Slider | `room width` | `{'Value': 5.0}` |
| 54 | `49f55226...` | Construct Point | `Target point.Point` | `[0.0, -4.5, 4.0]` |
| 55 | `a6b98c27...` | Construct Point | `p1` | `{'Point': [0.0, 3.0, -3.0]}` |
| 56 | `133aa1b3...` | Division | `/.Result` | `0.3888888888888889` |
| 57 | `47af807c...` | Move | `Slats original.Geometry` | `{'type': 'rectangle', 'plane': {'origin': [0, 0, 0], 'x_axis': [1, 0, 0], 'y_axis': [0, 1, 0], 'z...` |
| 58 | `cf5fed0c...` | Plane Normal | `PN.Plane` | `{'origin': [0.0, 0.0, 0.0], 'normal': [0.0, 0.0, 1.0], 'z_axis': [0.0, 0.0, 1.0]}` |
| 59 | `73455c39...` | Line | `Between.Line` | `{'start': [1.0, 0.0, 0.0], 'end': [1.0, 0.0, 0.0], 'direction': [0.0, 0.0, 0.0], 'length': 0.0}` |
| 60 | `50d6fc68...` | Area | `Area.Centroid` | `[0.0, 0.0, 0.0]` |
| 61 | `04a32494...` | Series | `Series.Series` | `[0.0, 0.3888888888888889, 0.7777777777777778, 1.1666666666666667, 1.5555555555555556, 1.944444444...` |
| 62 | `e81f2ba2...` | Number Slider | `1st targets from slats` | `{'Value': 1.0}` |
| 63 | `f8fdffb7...` | Negative | `-.Result` | `-3.8` |
| 64 | `9822511c...` | Line | `In Ray.Line` | `[{'start': [0.0, 0.0, 0.0], 'end': [11.327429598006665, -31.846834162334087, 4.0], 'direction': [...` |
| 65 | `e5d1f3af...` | Value List | `Orientations` | `{'Values': [4.0]}` |
| 66 | `ac0efd11...` | Divide Length | `DL.Points` | `[[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [2.0, 0.0, 0.0]]` |
| 67 | `1c0dfd0d...` | Subtraction | `-.Result` | `0.6999999999999997` |
| 68 | `dd0f4d1f...` | Move | `New Sun.Geometry` | `[33219.837229, -61164.521016, 71800.722722]` |
| 69 | `a7dd54c8...` | Subtraction | `-.Result` | `9.0` |
| 70 | `9bf9263c...` | Construct Plane | `Construct Plane.Plane` | `{'origin': [0.0, 0.0, 0.0], 'x_axis': [1.0, 0.0, 0.0], 'y_axis': [0.0, 1.0, 0.0], 'z_axis': [0.0,...` |
| 71 | `81565b66...` | Unit Y | `Unit Y.Unit vector` | `[[0.0, -0.07, 0.0], [0.0, -0.07, 0.0], [0.0, -0.07, 0.0], [0.0, -0.07, 0.0], [0.0, -0.07, 0.0], [...` |
| 72 | `6bb3071b...` | Unit Y | `Unit Y.Unit vector` | `[[0.0, 0.0, 0.0], [0.0, 0.3888888888888889, 0.0], [0.0, 0.7777777777777778, 0.0], [0.0, 1.1666666...` |
| 73 | `3560b89d...` | Rotate | `Rotate.Geometry` | `{'polygon': 'polygon_geometry', 'vertices': [[1.1480502970952695, 2.77163859753386, 0.0], [-1.148...` |
| 74 | `8cb00f94...` | Subtraction | `-.Result` | `3.5` |
| 75 | `c0f3d527...` | List Item | `LI.i` | `None` |
| 76 | `537142d8...` | Number Slider | `Number of slats` | `{'Value': 10.0}` |
| 77 | `20f5465a...` | Division | `/.Result` | `0.07777777777777775` |
| 78 | `aeedb946...` | Project | `Project.Curve` | `{'start': [0.0, 0.0, 0.0], 'end': [33219.837229, -61164.521016, 71800.722722], 'direction': [3321...` |
| 79 | `456d176f...` | Number Slider | `Slats height (top)` | `{'Value': 3.8}` |
| 80 | `a72418c4...` | List Item | `LI.i` | `None` |
| 81 | `3d373d1a...` | Move | `Box to project.Geometry` | `{'corner1': [0.0, -2.0, 7.0], 'corner2': [0.0, 3.0, -3.0]}` |
| 82 | `4c2fdd4e...` | Division | `/.Result` | `2.5` |
| 83 | `f12438b5...` | Box 2Pt | `Box 2Pt.Box` | `{'corner1': [0.0, -2.0, 7.0], 'corner2': [0.0, 3.0, -3.0]}` |
| 84 | `00d89d35...` | Polar Array | `Polar Array.Geometry` | `[{'corner1': [0.0, -2.0, 7.0], 'corner2': [0.0, 3.0, -3.0]}, {'corner1': [0.0, -2.0, 7.0], 'corne...` |
| 85 | `d055df7d...` | Subtraction | `-` | `{'Result': 0.6999999999999997}` |
| 86 | `a69d2e4a...` | Negative | `-` | `{'Result': -0.0}` |
| 87 | `a7644f3e...` | Subtraction | `-` | `{'Result': 3.5}` |
| 88 | `003162a4...` | Negative | `-` | `{'Result': -4.5}` |
| 89 | `a2151ddb...` | Polygon | `Polygon` | `{'Polygon': {'polygon': 'polygon_geometry', 'vertices': [[3.0, 0.0, 0.0], [2.121320343559643, 2.1...` |
| 90 | `b9102ff3...` | Division | `/` | `{'Result': 0.04}` |
| 91 | `e2671ced...` | Subtraction | `-` | `{'Result': 9.0}` |
| 92 | `b3c71890...` | Negative | `-` | `{'Result': -3.8}` |
| 93 | `e11dd9b3...` | Subtraction | `-` | `{'Result': 9.0}` |
| 94 | `b908d823...` | Box 2Pt | `Box 2Pt` | `{'Box': {'corner1': [0.0, -2.0, 7.0], 'corner2': [0.0, 3.0, -3.0]}}` |
| 95 | `32cc502c...` | Division | `/` | `{'Result': 2.5}` |
| 96 | `be907c11...` | Construct Point | `CP` | `{'Point': [2.5, 0.04, 0.0]}` |
| 97 | `680b290d...` | Series | `Series` | `{'Series': [-0.07, -0.07, -0.07, -0.07, -0.07, -0.07, -0.07, -0.07, -0.07, -0.07]}` |
| 98 | `524ba570...` | Division | `/` | `{'Result': 0.3888888888888889}` |
| 99 | `d63be87d...` | Negative | `-` | `{'Result': -0.04}` |
| 100 | `f9a68fee...` | Division | `/` | `{'Result': 0.07777777777777775}` |
| 101 | `5a77f108...` | Rotate | `Rotate` | `{'Geometry': {'polygon': 'polygon_geometry', 'vertices': [[1.1480502970952695, 2.77163859753386, ...` |
| 102 | `57648120...` | Construct Point | `Target point` | `{'Point': [0.0, -4.5, 4.0]}` |
| 103 | `d8f9c0ae...` | Polar Array | `Polar Array` | `{'Geometry': [{'corner1': [0.0, -2.0, 7.0], 'corner2': [0.0, 3.0, -3.0]}, {'corner1': [0.0, -2.0,...` |
| 104 | `835d042f...` | Negative | `-` | `{'Result': -2.5}` |
| 105 | `47650d42...` | Mirror | `Mirror` | `{'Geometry': {'polygon': 'polygon_geometry', 'vertices': [[-1.1480502970952695, 2.77163859753386,...` |
| 106 | `474a94bf...` | Series | `Series` | `{'Series': [0.0, 0.3888888888888889, 0.7777777777777778, 1.1666666666666667, 1.5555555555555556, ...` |
| 107 | `b785e424...` | Series | `Series` | `{'Series': [-3.8, -3.722222222222222, -3.6444444444444444, -3.5666666666666664, -3.48888888888888...` |
| 108 | `e5850abb...` | List Item | `LI` | `{'Item': {'corner1': [0.0, -2.0, 7.0], 'corner2': [0.0, 3.0, -3.0]}}` |
| 109 | `67b3eb53...` | Construct Point | `CP` | `{'Point': [-2.5, -0.04, 0.0]}` |
| 110 | `268410b9...` | Unit Y | `Unit Y` | `{'Vector': [[0.0, -0.07, 0.0], [0.0, -0.07, 0.0], [0.0, -0.07, 0.0], [0.0, -0.07, 0.0], [0.0, -0....` |
| 111 | `4775d3bf...` | Negative | `-` | `{'Result': [3.8, 3.722222222222222, 3.6444444444444444, 3.5666666666666664, 3.488888888888889, 3....` |
| 112 | `16022012...` | Area | `Area` | `{'Area': 0.0, 'Centroid': [0.0, 0.0, 0.0]}` |
| 113 | `0402692e...` | Unit Y | `Unit Y` | `{'Vector': [[0.0, 0.0, 0.0], [0.0, 0.3888888888888889, 0.0], [0.0, 0.7777777777777778, 0.0], [0.0...` |
| 114 | `c78ea9c5...` | Deconstruct Brep | `DB` | `{'Faces': [], 'Edges': [{'type': 'edge', 'index': 0, 'start': [-1.1480502970952695, 2.77163859753...` |
| 115 | `a3eb185f...` | Rectangle 2Pt | `Rectangle 2Pt` | `{'Rectangle': {'type': 'rectangle', 'plane': {'origin': [0, 0, 0], 'x_axis': [1, 0, 0], 'y_axis':...` |
| 116 | `d89d47e0...` | List Item | `List Item` | `{'Item': {'type': 'edge', 'index': 4, 'start': [1.14805029709527, -2.77163859753386, 0.0], 'end':...` |
| 117 | `3732df33...` | Unit Z | `Unit Z` | `{'Vector': [[0.0, 0.0, 3.8], [0.0, 0.0, 3.722222222222222], [0.0, 0.0, 3.6444444444444444], [0.0,...` |
| 118 | `1f794702...` | Vector 2Pt | `Vector 2Pt` | `{'Vector': [1.14805029709527, -2.77163859753386, 0.0], 'Length': 3.0}` |
| 119 | `9f3f4672...` | Move | `Targets` | `{'Geometry': [[0.0, -4.5, 4.0], [0.0, -4.111111111111111, 4.0], [0.0, -3.7222222222222223, 4.0], ...` |
| 120 | `ea032caa...` | Vector 2Pt | `Vector 2Pt` | `{'Vector': [[0.0, 0.07, 3.8], [0.0, 0.07, 3.722222222222222], [0.0, 0.07, 3.6444444444444444], [0...` |
| 121 | `f54babb4...` | Amplitude | `Amplitude` | `{'Vector': [11.327429598006665, -27.346834162334087, 0.0]}` |
| 122 | `b4a4862a...` | Polar Array | `PA` | `{'Geometry': [[[0.0, -4.5, 4.0], [0.0, -4.111111111111111, 4.0], [0.0, -3.7222222222222223, 4.0],...` |
| 123 | `ddb9e6ae...` | Move | `Slats original` | `{'Geometry': {'type': 'rectangle', 'plane': {'origin': [0, 0, 0], 'x_axis': [1, 0, 0], 'y_axis': ...` |
| 124 | `dfbbd4a2...` | Move | `Box to project` | `{'Geometry': {'corner1': [0.0, -2.0, 7.0], 'corner2': [0.0, 3.0, -3.0]}, 'Transform': {'type': 't...` |
| 125 | `f03b9ab7...` | List Item | `LI` | `{'Item': [[0.0, -4.5, 4.0], [0.0, -4.111111111111111, 4.0], [0.0, -3.7222222222222223, 4.0], [0.0...` |
| 126 | `d8de94de...` | Evaluate Surface | `Evaluate Surface` | `{'Point': [0.5, 0.5, 0.0], 'Normal': [0.0, 0.0, 1.0], 'Frame': None}` |
| 127 | `7ad636cc...` | Polar Array | `Polar Array` | `{'Geometry': [{'type': 'rectangle', 'plane': {'origin': [0, 0, 0], 'x_axis': [1, 0, 0], 'y_axis':...` |
| 128 | `b38a38f1...` | Move | `Targets` | `{'Geometry': [[11.327429598006665, -31.846834162334087, 4.0], [11.327429598006665, -31.4579452734...` |
| 129 | `77f7eddb...` | Area | `Area` | `{'Area': 0.0, 'Centroid': [0.0, 0.0, 0.0]}` |
| 130 | `09db66ec...` | Plane Normal | `PN` | `{'Normal': [0.0, 0.0, 1.0], 'Plane': {'origin': [0.0, 0.0, 0.0], 'normal': [0.0, 0.0, 1.0], 'z_ax...` |
| 131 | `27933633...` | List Item | `LI` | `{'Item': {'type': 'rectangle', 'plane': {'origin': [0, 0, 0], 'x_axis': [1, 0, 0], 'y_axis': [0, ...` |
| 132 | `ef803855...` | PolyLine | `PolyLine` | `{'PolyLine': {'points': [[11.327429598006665, -31.846834162334087, 4.0], [11.327429598006665, -31...` |
| 133 | `0532cbdf...` | Move | `Slats original` | `{'Geometry': {'type': 'rectangle', 'plane': {'origin': [0, 0, 0], 'x_axis': [1, 0, 0], 'y_axis': ...` |
| 134 | `3bd2c1d3...` | Area | `Area` | `{'Area': 0.4, 'Centroid': [0.0, 0.0, 0.0]}` |
| 135 | `c7dba531...` | Line | `In Ray` | `{'Line': [{'start': [0.0, 0.0, 0.0], 'end': [11.327429598006665, -31.846834162334087, 4.0], 'dire...` |
| 136 | `910c335c...` | PolyLine | `PolyLine` | `{'PolyLine': {'points': [0.0, 0.0, 0.0], 'closed': 'false'}}` |
| 137 | `326da981...` | Plane Normal | `Plane Normal` | `{'Normal': {'points': [[11.327429598006665, -31.846834162334087, 4.0], [11.327429598006665, -31.4...` |
| 138 | `9ff79870...` | List Item | `List Item` | `{'Item': 0.0}` |
| 139 | `0f529988...` | Move | `New Sun` | `{'Geometry': [33219.837229, -61164.521016, 71800.722722], 'Transform': {'type': 'translation', 'm...` |
| 140 | `30f76ec5...` | Construct Plane | `Construct Plane` | `{'Plane': {'origin': [0.0, 0.0, 0.0], 'x_axis': [1.0, 0.0, 0.0], 'y_axis': [0.0, 1.0, 0.0], 'z_ax...` |
| 141 | `c7b8773d...` | Divide Length | `DL` | `{'Points': [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [2.0, 0.0, 0.0]], 'Parameters': []}` |
| 142 | `157c48b5...` | List Item | `List Item` | `{'Item': {'origin': [0.0, 0.0, 0.0], 'normal': {'points': [[11.327429598006665, -31.8468341623340...` |
| 143 | `9a33273a...` | Line | `Out Ray` | `{'Line': {'start': [0.0, 0.0, 0.0], 'end': [33219.837229, -61164.521016, 71800.722722], 'directio...` |
| 144 | `011398ea...` | Plane Normal | `Plane Normal` | `{'Normal': {'origin': [0.0, 0.0, 0.0], 'x_axis': [1.0, 0.0, 0.0], 'y_axis': [0.0, 1.0, 0.0], 'z_a...` |
| 145 | `ed4878fc...` | List Item | `LI` | `{'Item': [1.0, 0.0, 0.0]}` |
| 146 | `9cd053c9...` | Project | `Project` | `{'Curve': {'start': [0.0, 0.0, 0.0], 'end': [33219.837229, -61164.521016, 71800.722722], 'directi...` |
| 147 | `1e2231f7...` | Divide Length | `DL` | `{'Points': [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [2.0, 0.0, 0.0]], 'Parameters': []}` |
| 148 | `3f21b46a...` | List Item | `LI` | `{'Item': [1.0, 0.0, 0.0]}` |
| 149 | `a518331f...` | Line | `Between` | `{'Line': {'start': [1.0, 0.0, 0.0], 'end': [1.0, 0.0, 0.0], 'direction': [0.0, 0.0, 0.0], 'length...` |
| 150 | `0d695e6b...` | Angle | `Angle` | `{'Angle': 0.0, 'Reflex': 0.0}` |
| 151 | `fa0ba5a6...` | Degrees | `Degrees` | `{'Degrees': 0.0}` |

## Final Output

**Degrees Output** (`4d5670e5...`)

- **Parent Component**: `fa0ba5a6...` (Degrees) 'Degrees'
- **Output Parameter**: `Degrees`
- **Value**: `0.0`