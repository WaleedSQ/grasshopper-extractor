# Rotatingslats Evaluation Results

## Evaluation Chain (Topological Order)

Components evaluated in dependency order, from early inputs to final outputs.

| # | Component GUID | Type | Name/NickName | Output |
|---|----------------|------|---------------|--------|
| 1 | `9822511c...` | Line | `In Ray.Line` | `[{'start': [11.327429598006665, -27.346834162334087, 7.6], 'end': [11.327429598006665, -22.846834...` |
| 2 | `49f55226...` | Construct Point | `Target point.Point` | `[0.0, -4.5, 4.0]` |
| 3 | `34529a8c...` | Area | `Area.Centroid` | `[11.327429598006665, -27.846834162334087, 2.0]` |
| 4 | `456d176f...` | Number Slider | `Slats height (top)` | `{'Value': 3.8}` |
| 5 | `3d373d1a...` | Move | `Box to project.Geometry` | `{'type': 'box', 'corner1': [11.327429598006665, -25.346834162334087, 7.0], 'corner2': [11.3274295...` |
| 6 | `dd0f4d1f...` | Move | `New Sun.Geometry` | `[[33231.164658598005, -61191.867850162336, 71808.32272200001], [33231.164658598005, -61191.867850...` |
| 7 | `81565b66...` | Unit Y | `Unit Y.Unit vector` | `[[0.0, -0.07, 0.0], [0.0, -0.07, 0.0], [0.0, -0.07, 0.0], [0.0, -0.07, 0.0], [0.0, -0.07, 0.0], [...` |
| 8 | `65a37667...` | PolyLine | `PolyLine.Polyline` | `None` |
| 9 | `ea2c7d7f...` | Number Slider | `Slats height (threshold)` | `{'Value': 3.1}` |
| 10 | `f78fb52e...` | List Item | `List Item.i` | `None` |
| 11 | `6bb3071b...` | Unit Y | `Unit Y.Unit vector` | `[[0.0, 0.0, 0.0], [0.0, 0.3888888888888889, 0.0], [0.0, 0.7777777777777778, 0.0], [0.0, 1.1666666...` |
| 12 | `e8c7faf9...` | List Item | `LI.i` | `None` |
| 13 | `1c0dfd0d...` | Subtraction | `-.Result` | `0.6999999999999997` |
| 14 | `50d6fc68...` | Area | `Area.Centroid` | `[0.0, 0.0, 0.0]` |
| 15 | `2587762a...` | Move | `Targets.Geometry` | `[[0.0, -4.5, 4.0], [0.0, -4.111111111111111, 4.0], [0.0, -3.7222222222222223, 4.0], [0.0, -3.3333...` |
| 16 | `a72418c4...` | List Item | `LI.i` | `None` |
| 17 | `04a32494...` | Series | `Series.Series` | `[0.0, 0.3888888888888889, 0.7777777777777778, 1.1666666666666667, 1.5555555555555556, 1.944444444...` |
| 18 | `f8fdffb7...` | Negative | `-.Result` | `-3.8` |
| 19 | `24f7f310...` | List Item | `LI.i` | `None` |
| 20 | `6ce8bcba...` | Point On Curve | `Point On Curve` | `{'Point': [1.14805029709527, -2.77163859753386, 0.0]}` |
| 21 | `aeedb946...` | Project | `Project.Curve` | `[{'start': [11.327429598006665, -27.346834162334087, 7.6], 'end': [33231.164658598005, -61191.867...` |
| 22 | `b94e42e9...` | Polygon | `Polygon.Polygon` | `{'polygon': 'polygon_geometry', 'vertices': [[3.0, 0.0, 0.0], [2.121320343559643, 2.1213203435596...` |
| 23 | `bd24b9c6...` | Number Slider | `Targets Height` | `{'Value': 4.0}` |
| 24 | `80fd9f48...` | Move | `Targets.Geometry` | `[[11.327429598006665, -22.846834162334087, 4.0], [11.327429598006665, -23.235723051222976, 4.0], ...` |
| 25 | `95282afd...` | Negative | `-.Result` | `-4.5` |
| 26 | `4b0092c3...` | Plane Normal | `Plane Normal.Plane` | `{'origin': [[11.327429598006665, -27.346834162334087, 7.6], [11.327429598006665, -27.346834162334...` |
| 27 | `2cc32a65...` | Construct Point | `p1.Point` | `[0.0, 3.0, -3.0]` |
| 28 | `4fa54506...` | Unit Z | `Unit Z.Unit vector` | `[[0.0, 0.0, 3.8], [0.0, 0.0, 3.722222222222222], [0.0, 0.0, 3.6444444444444444], [0.0, 0.0, 3.566...` |
| 29 | `8cb00f94...` | Subtraction | `-.Result` | `3.5` |
| 30 | `f12438b5...` | Box 2Pt | `Box 2Pt.Box` | `{'type': 'box', 'corner1': [0.0, -2.0, 7.0], 'corner2': [0.0, 3.0, -3.0], 'vertices': [[0.0, -2.0...` |
| 31 | `3560b89d...` | Rotate | `Rotate.Geometry` | `{'polygon': 'polygon_geometry', 'vertices': [[1.1480502970952695, 2.77163859753386, 0.0], [-1.148...` |
| 32 | `bdac63ee...` | Negative | `-.Result` | `-0.0` |
| 33 | `ac0efd11...` | Divide Length | `DL.Points` | `[[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [2.0, 0.0, 0.0]]` |
| 34 | `ef17623c...` | Construct Point | `CP.Point` | `[-2.5, -0.04, 0.0]` |
| 35 | `577ce3f3...` | Construct Point | `p1` | `{'Point': [0.0, -2.0, 7.0]}` |
| 36 | `c8dfe19f...` | Number Slider | `Slat width` | `{'Value': 0.08}` |
| 37 | `4d5670e5...` | Degrees | `Degrees.Degrees` | `0.0` |
| 38 | `4c2fdd4e...` | Division | `/.Result` | `2.5` |
| 39 | `00d89d35...` | Polar Array | `Polar Array.Geometry` | `[{'type': 'box', 'corner1': [0.0, -2.0, 7.0], 'corner2': [0.0, 3.0, 7.0], 'vertices': [[0.0, -2.0...` |
| 40 | `0460d28c...` | Divide Length | `DL.Points` | `[[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [2.0, 0.0, 0.0]]` |
| 41 | `73455c39...` | Line | `Between.Line` | `{'start': [1.0, 0.0, 0.0], 'end': [1.0, 0.0, 0.0], 'direction': [0.0, 0.0, 0.0], 'length': 0.0}` |
| 42 | `01fd4f89...` | Area | `Area.Centroid` | `[[11.327429598006665, -27.346834162334087, 7.6], [11.327429598006665, -27.346834162334087, 7.4444...` |
| 43 | `8a96679d...` | Negative | `-.Result` | `-2.5` |
| 44 | `a7dd54c8...` | Subtraction | `-.Result` | `9.0` |
| 45 | `47af807c...` | Move | `Slats original.Geometry` | `[{'type': 'rectangle', 'plane': {'origin': [0.0, 0.0, 0.0], 'x_axis': [1.0, 0.0, 0.0], 'y_axis': ...` |
| 46 | `0fb443ce...` | Construct Point | `p1.Point` | `[0.0, -2.0, 7.0]` |
| 47 | `6b94f6c4...` | List Item | `List Item.i` | `None` |
| 48 | `507b14ee...` | Number Slider | `Distance from window` | `{'Value': -0.07}` |
| 49 | `c0f3d527...` | List Item | `LI.i` | `None` |
| 50 | `a6b98c27...` | Construct Point | `p1` | `{'Point': [0.0, 3.0, -3.0]}` |
| 51 | `9bf9263c...` | Construct Plane | `Construct Plane.Plane` | `{'origin': [[11.327429598006665, -27.346834162334087, 7.6], [11.327429598006665, -27.346834162334...` |
| 52 | `160dcd76...` | Series | `Series.Series` | `[-3.8, -3.722222222222222, -3.6444444444444444, -3.5666666666666664, -3.488888888888889, -3.41111...` |
| 53 | `07dcee6c...` | Vector 2Pt | `Vector 2Pt.Vector` | `[[0.0, 0.07, 3.8], [0.0, 0.07, 3.722222222222222], [0.0, 0.07, 3.6444444444444444], [0.0, 0.07, 3...` |
| 54 | `23900bd5...` | Angle | `Angle.Angle` | `0.0` |
| 55 | `eedce522...` | Division | `/.Result` | `0.04` |
| 56 | `84214afe...` | Vector 2Pt | `Vector 2Pt.Vector` | `[1.14805029709527, -2.77163859753386, 0.0]` |
| 57 | `7de8f856...` | List Item | `LI.i` | `None` |
| 58 | `d0668a07...` | Amplitude | `Amplitude.Vector` | `[11.327429598006665, -27.346834162334087, 0.0]` |
| 59 | `cf5fed0c...` | Plane Normal | `PN.Plane` | `{'origin': [11.327429598006665, -27.846834162334087, 2.0], 'normal': [-1.0, 0.0, 1.0], 'z_axis': ...` |
| 60 | `6c807a4e...` | Subtraction | `-.Result` | `9.0` |
| 61 | `3a96e7fa...` | Negative | `-.Result` | `[3.8, 3.722222222222222, 3.6444444444444444, 3.5666666666666664, 3.488888888888889, 3.41111111111...` |
| 62 | `e5d1f3af...` | Value List | `Orientations` | `{'Values': [4.0]}` |
| 63 | `e41d5eba...` | Evaluate Surface | `Evaluate Surface.Normal` | `[-1.0, 0.0, 0.0]` |
| 64 | `db399c50...` | Mirror | `Mirror.Geometry` | `{'polygon': 'polygon_geometry', 'vertices': [[-1.1480502970952695, 2.77163859753386, 0.0], [1.148...` |
| 65 | `638a56be...` | Plane Normal | `Plane Normal.Plane` | `{'origin': [11.327429598006665, -27.346834162334087, 7.6], 'normal': {'origin': [[11.327429598006...` |
| 66 | `133aa1b3...` | Division | `/.Result` | `0.3888888888888889` |
| 67 | `e81f2ba2...` | Number Slider | `1st targets from slats` | `{'Value': 1.0}` |
| 68 | `08edbcda...` | Number Slider | `Horizontal shift between slats` | `{'Value': 0.0}` |
| 69 | `1a00d7ad...` | Polar Array | `Polar Array.Geometry` | `[[{'type': 'rectangle', 'plane': {'origin': [0.0, 0.0, 0.0], 'x_axis': [1.0, 0.0, 0.0], 'y_axis':...` |
| 70 | `125e7c20...` | Number Slider | `Last target from slats` | `{'Value': 4.5}` |
| 71 | `dac68df4...` | Number Slider | `Room - Distance from origen` | `{'Value': 29.6}` |
| 72 | `e7683176...` | Polar Array | `PA.Geometry` | `[[[0.0, -4.5, 4.0], [0.0, -4.111111111111111, 4.0], [0.0, -3.7222222222222223, 4.0], [0.0, -3.333...` |
| 73 | `20f5465a...` | Division | `/.Result` | `0.07777777777777775` |
| 74 | `def742ff...` | PolyLine | `PolyLine.Polyline` | `None` |
| 75 | `902866aa...` | Construct Point | `CP.Point` | `[2.5, 0.04, 0.0]` |
| 76 | `c4c92669...` | MD Slider | `MD Slider` | `{'Value': 0.5, 'Point': [0.5, 0.5, 0.5]}` |
| 77 | `4218a4e5...` | Move | `Slats original.Geometry` | `[{'type': 'rectangle', 'plane': {'origin': [0.0, 0.0, 0.0], 'x_axis': [1.0, 0.0, 0.0], 'y_axis': ...` |
| 78 | `a7d2817a...` | Number Slider | `room width` | `{'Value': 5.0}` |
| 79 | `dbc236d4...` | Rectangle 2Pt | `Rectangle 2Pt.Rectangle` | `{'type': 'rectangle', 'plane': {'origin': [0.0, 0.0, 0.0], 'x_axis': [1.0, 0.0, 0.0], 'y_axis': [...` |
| 80 | `370f6ae5...` | Negative | `-.Result` | `-0.04` |
| 81 | `537142d8...` | Number Slider | `Number of slats` | `{'Value': 10.0}` |
| 82 | `e898f4cb...` | Line | `Out Ray.Line` | `[{'start': [11.327429598006665, -27.346834162334087, 7.6], 'end': [33231.164658598005, -61191.867...` |
| 83 | `71c9ab9c...` | Number Slider | `Number of orientations` | `{'Value': 8.0}` |
| 84 | `306c324a...` | Series | `Series.Series` | `[-0.07, -0.07, -0.07, -0.07, -0.07, -0.07, -0.07, -0.07, -0.07, -0.07]` |
| 85 | `a7644f3e...` | Subtraction | `-` | `{'Result': 3.5}` |
| 86 | `e11dd9b3...` | Subtraction | `-` | `{'Result': 9.0}` |
| 87 | `a2151ddb...` | Polygon | `Polygon` | `{'Polygon': {'polygon': 'polygon_geometry', 'vertices': [[3.0, 0.0, 0.0], [2.121320343559643, 2.1...` |
| 88 | `b908d823...` | Box 2Pt | `Box 2Pt` | `{'Box': {'type': 'box', 'corner1': [0.0, -2.0, 7.0], 'corner2': [0.0, 3.0, -3.0], 'vertices': [[0...` |
| 89 | `32cc502c...` | Division | `/` | `{'Result': 2.5}` |
| 90 | `b3c71890...` | Negative | `-` | `{'Result': -3.8}` |
| 91 | `d055df7d...` | Subtraction | `-` | `{'Result': 0.6999999999999997}` |
| 92 | `e2671ced...` | Subtraction | `-` | `{'Result': 9.0}` |
| 93 | `a69d2e4a...` | Negative | `-` | `{'Result': -0.0}` |
| 94 | `b9102ff3...` | Division | `/` | `{'Result': 0.04}` |
| 95 | `003162a4...` | Negative | `-` | `{'Result': -4.5}` |
| 96 | `d63be87d...` | Negative | `-` | `{'Result': -0.04}` |
| 97 | `680b290d...` | Series | `Series` | `{'Series': [-0.07, -0.07, -0.07, -0.07, -0.07, -0.07, -0.07, -0.07, -0.07, -0.07]}` |
| 98 | `be907c11...` | Construct Point | `CP` | `{'Point': [2.5, 0.04, 0.0]}` |
| 99 | `f9a68fee...` | Division | `/` | `{'Result': 0.07777777777777775}` |
| 100 | `d8f9c0ae...` | Polar Array | `Polar Array` | `{'Geometry': [{'type': 'box', 'corner1': [0.0, -2.0, 7.0], 'corner2': [0.0, 3.0, 7.0], 'vertices'...` |
| 101 | `57648120...` | Construct Point | `Target point` | `{'Point': [0.0, -4.5, 4.0]}` |
| 102 | `835d042f...` | Negative | `-` | `{'Result': -2.5}` |
| 103 | `524ba570...` | Division | `/` | `{'Result': 0.3888888888888889}` |
| 104 | `5a77f108...` | Rotate | `Rotate` | `{'Geometry': {'polygon': 'polygon_geometry', 'vertices': [[1.1480502970952695, 2.77163859753386, ...` |
| 105 | `474a94bf...` | Series | `Series` | `{'Series': [0.0, 0.3888888888888889, 0.7777777777777778, 1.1666666666666667, 1.5555555555555556, ...` |
| 106 | `67b3eb53...` | Construct Point | `CP` | `{'Point': [-2.5, -0.04, 0.0]}` |
| 107 | `47650d42...` | Mirror | `Mirror` | `{'Geometry': {'polygon': 'polygon_geometry', 'vertices': [[-1.1480502970952695, 2.77163859753386,...` |
| 108 | `268410b9...` | Unit Y | `Unit Y` | `{'Vector': [[0.0, -0.07, 0.0], [0.0, -0.07, 0.0], [0.0, -0.07, 0.0], [0.0, -0.07, 0.0], [0.0, -0....` |
| 109 | `e5850abb...` | List Item | `LI` | `{'Item': {'type': 'box', 'corner1': [2.4492935982947064e-16, 2.0, 7.0], 'corner2': [-3.6739403974...` |
| 110 | `b785e424...` | Series | `Series` | `{'Series': [-3.8, -3.722222222222222, -3.6444444444444444, -3.5666666666666664, -3.48888888888888...` |
| 111 | `4775d3bf...` | Negative | `-` | `{'Result': [3.8, 3.722222222222222, 3.6444444444444444, 3.5666666666666664, 3.488888888888889, 3....` |
| 112 | `16022012...` | Area | `Area` | `{'Area': 0.0, 'Centroid': [0.0, 0.0, 0.0]}` |
| 113 | `a3eb185f...` | Rectangle 2Pt | `Rectangle 2Pt` | `{'Rectangle': {'type': 'rectangle', 'plane': {'origin': [0.0, 0.0, 0.0], 'x_axis': [1.0, 0.0, 0.0...` |
| 114 | `c78ea9c5...` | Deconstruct Brep | `DB` | `{'Faces': [], 'Edges': [{'type': 'edge', 'index': 0, 'start': [-1.1480502970952695, 2.77163859753...` |
| 115 | `0402692e...` | Unit Y | `Unit Y` | `{'Vector': [[0.0, 0.0, 0.0], [0.0, 0.3888888888888889, 0.0], [0.0, 0.7777777777777778, 0.0], [0.0...` |
| 116 | `1f794702...` | Vector 2Pt | `Vector 2Pt` | `{'Vector': [1.14805029709527, -2.77163859753386, 0.0], 'Length': 3.0}` |
| 117 | `3732df33...` | Unit Z | `Unit Z` | `{'Vector': [[0.0, 0.0, 3.8], [0.0, 0.0, 3.722222222222222], [0.0, 0.0, 3.6444444444444444], [0.0,...` |
| 118 | `9f3f4672...` | Move | `Targets` | `{'Geometry': [[0.0, -4.5, 4.0], [0.0, -4.111111111111111, 4.0], [0.0, -3.7222222222222223, 4.0], ...` |
| 119 | `d89d47e0...` | List Item | `List Item` | `{'Item': {'type': 'edge', 'index': 4, 'start': [1.14805029709527, -2.77163859753386, 0.0], 'end':...` |
| 120 | `f54babb4...` | Amplitude | `Amplitude` | `{'Vector': [11.327429598006665, -27.346834162334087, 0.0]}` |
| 121 | `ea032caa...` | Vector 2Pt | `Vector 2Pt` | `{'Vector': [[0.0, 0.07, 3.8], [0.0, 0.07, 3.722222222222222], [0.0, 0.07, 3.6444444444444444], [0...` |
| 122 | `b4a4862a...` | Polar Array | `PA` | `{'Geometry': [[[0.0, -4.5, 4.0], [0.0, -4.111111111111111, 4.0], [0.0, -3.7222222222222223, 4.0],...` |
| 123 | `f03b9ab7...` | List Item | `LI` | `{'Item': [[5.51091059616309e-16, 4.5, 4.0], [5.034659063161341e-16, 4.111111111111111, 4.0], [4.5...` |
| 124 | `ddb9e6ae...` | Move | `Slats original` | `{'Geometry': [{'type': 'rectangle', 'plane': {'origin': [0.0, 0.0, 0.0], 'x_axis': [1.0, 0.0, 0.0...` |
| 125 | `dfbbd4a2...` | Move | `Box to project` | `{'Geometry': {'type': 'box', 'corner1': [11.327429598006665, -25.346834162334087, 7.0], 'corner2'...` |
| 126 | `d8de94de...` | Evaluate Surface | `Evaluate Surface` | `{'Point': [11.327429598006665, -27.846834162334087, 2.0], 'Normal': [-1.0, 0.0, 0.0], 'Frame': None}` |
| 127 | `b38a38f1...` | Move | `Targets` | `{'Geometry': [[11.327429598006665, -22.846834162334087, 4.0], [11.327429598006665, -23.2357230512...` |
| 128 | `77f7eddb...` | Area | `Area` | `{'Area': 100.0, 'Centroid': [11.327429598006665, -27.846834162334087, 2.0]}` |
| 129 | `7ad636cc...` | Polar Array | `Polar Array` | `{'Geometry': [[{'type': 'rectangle', 'plane': {'origin': [0.0, 0.0, 0.0], 'x_axis': [1.0, 0.0, 0....` |
| 130 | `09db66ec...` | Plane Normal | `PN` | `{'Normal': [-1.0, 0.0, 1.0], 'Plane': {'origin': [11.327429598006665, -27.846834162334087, 2.0], ...` |
| 131 | `ef803855...` | PolyLine | `PolyLine` | `{'PolyLine': {'points': [[11.327429598006665, -22.846834162334087, 4.0], [11.327429598006665, -23...` |
| 132 | `27933633...` | List Item | `LI` | `{'Item': [{'type': 'rectangle', 'plane': {'origin': [0.0, 0.0, 0.0], 'x_axis': [1.0, 0.0, 0.0], '...` |
| 133 | `0532cbdf...` | Move | `Slats original` | `{'Geometry': [{'type': 'rectangle', 'plane': {'origin': [0.0, 0.0, 0.0], 'x_axis': [1.0, 0.0, 0.0...` |
| 134 | `3bd2c1d3...` | Area | `Area` | `{'Area': [0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4], 'Centroid': [[11.327429598006665, -2...` |
| 135 | `9ff79870...` | List Item | `List Item` | `{'Item': [11.327429598006665, -27.346834162334087, 7.6]}` |
| 136 | `326da981...` | Plane Normal | `Plane Normal` | `{'Normal': {'points': [[11.327429598006665, -22.846834162334087, 4.0], [11.327429598006665, -23.2...` |
| 137 | `910c335c...` | PolyLine | `PolyLine` | `{'PolyLine': {'points': [[11.327429598006665, -27.346834162334087, 7.6], [11.327429598006665, -27...` |
| 138 | `0f529988...` | Move | `New Sun` | `{'Geometry': [[33231.164658598005, -61191.867850162336, 71808.32272200001], [33231.164658598005, ...` |
| 139 | `c7dba531...` | Line | `In Ray` | `{'Line': [{'start': [11.327429598006665, -27.346834162334087, 7.6], 'end': [11.327429598006665, -...` |
| 140 | `157c48b5...` | List Item | `List Item` | `{'Item': {'origin': [[11.327429598006665, -27.346834162334087, 7.6], [11.327429598006665, -27.346...` |
| 141 | `9a33273a...` | Line | `Out Ray` | `{'Line': [{'start': [11.327429598006665, -27.346834162334087, 7.6], 'end': [33231.164658598005, -...` |
| 142 | `c7b8773d...` | Divide Length | `DL` | `{'Points': [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [2.0, 0.0, 0.0]], 'Parameters': []}` |
| 143 | `30f76ec5...` | Construct Plane | `Construct Plane` | `{'Plane': {'origin': [[11.327429598006665, -27.346834162334087, 7.6], [11.327429598006665, -27.34...` |
| 144 | `9cd053c9...` | Project | `Project` | `{'Curve': [{'start': [11.327429598006665, -27.346834162334087, 7.6], 'end': [33231.164658598005, ...` |
| 145 | `011398ea...` | Plane Normal | `Plane Normal` | `{'Normal': {'origin': [[11.327429598006665, -27.346834162334087, 7.6], [11.327429598006665, -27.3...` |
| 146 | `ed4878fc...` | List Item | `LI` | `{'Item': [1.0, 0.0, 0.0]}` |
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