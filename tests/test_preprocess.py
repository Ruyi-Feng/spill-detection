from pre_processing.target_manager import TargetManager


def test_preprocess(test_data: list) -> list:
    p = TargetManager()
    for car in test_data:
        car = [car]  # 模拟传输来的1条信息
        car = p.run(car)
        print(car)
    assert type(car) == list


if __name__ == '__main__':
    test_data = [
        {'TargetId': 5087, 'XDecx': -2.55, 'YDecy': 259.7,
         'VDecVx': 0, 'VDecVy': -26.56, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -2.55, 'YDecy': 258.35,
         'VDecVx': 0, 'VDecVy': -26.56, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -2.55, 'YDecy': 257.05,
         'VDecVx': 0, 'VDecVy': -26.56, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -2.53, 'YDecy': 255.7,
         'VDecVx': 0, 'VDecVy': -26.56, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -2.49, 'YDecy': 254.4,
         'VDecVx': 0, 'VDecVy': -26.56, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -2.47, 'YDecy': 253.1,
         'VDecVx': 0, 'VDecVy': -26.56, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -2.45, 'YDecy': 251.8,
         'VDecVx': -0.03, 'VDecVy': -26.53, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -2.44, 'YDecy': 250.55,
         'VDecVx': -0.03, 'VDecVy': -26.53, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -2.42, 'YDecy': 249.2,
         'VDecVx': 0.06, 'VDecVy': -26.53, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -2.4, 'YDecy': 247.95,
         'VDecVx': 0.12, 'VDecVy': -26.56, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -2.38, 'YDecy': 246.7,
         'VDecVx': 0.12, 'VDecVy': -26.56, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -2.37, 'YDecy': 245.4,
         'VDecVx': 0.12, 'VDecVy': -26.56, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -2.32, 'YDecy': 244.2,
         'VDecVx': 0.48, 'VDecVy': -26.65, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -2.27, 'YDecy': 242.95,
         'VDecVx': 0.48, 'VDecVy': -26.65, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -2.21, 'YDecy': 241.7,
         'VDecVx': 0.48, 'VDecVy': -26.65, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -2.17, 'YDecy': 240.35,
         'VDecVx': 0.37, 'VDecVy': -26.75, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -2.13, 'YDecy': 238.95,
         'VDecVx': 0.38, 'VDecVy': -26.73, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -2.1, 'YDecy': 237.55,
         'VDecVx': 0.38, 'VDecVy': -26.73, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -2.06, 'YDecy': 236.2,
         'VDecVx': 0.49, 'VDecVy': -26.72, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -2.02, 'YDecy': 234.85,
         'VDecVx': 0.49, 'VDecVy': -26.72, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -2, 'YDecy': 233.5,
         'VDecVx': 0.49, 'VDecVy': -26.72, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -1.96, 'YDecy': 232.1,
         'VDecVx': 0.45, 'VDecVy': -26.56, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -1.92, 'YDecy': 230.65,
         'VDecVx': 0.45, 'VDecVy': -26.56, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -1.89, 'YDecy': 229.3,
         'VDecVx': 0.22, 'VDecVy': -26.37, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -1.88, 'YDecy': 227.95,
         'VDecVx': 0.14, 'VDecVy': -26.33, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -1.87, 'YDecy': 226.55,
         'VDecVx': 0.13, 'VDecVy': -26.18, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -1.87, 'YDecy': 225.1,
         'VDecVx': 0.13, 'VDecVy': -26.07, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -1.85, 'YDecy': 223.75,
         'VDecVx': 0.19, 'VDecVy': -25.99, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -1.82, 'YDecy': 222.4,
         'VDecVx': 0.23, 'VDecVy': -25.87, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -1.8, 'YDecy': 221.05,
         'VDecVx': 0.27, 'VDecVy': -25.73, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -1.76, 'YDecy': 219.75,
         'VDecVx': 0.35, 'VDecVy': -25.67, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -1.72, 'YDecy': 218.45,
         'VDecVx': 0.39, 'VDecVy': -25.54, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -1.67, 'YDecy': 217.25,
         'VDecVx': 0.45, 'VDecVy': -25.4, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -1.63, 'YDecy': 216,
         'VDecVx': 0.44, 'VDecVy': -25.28, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -1.59, 'YDecy': 214.8,
         'VDecVx': 0.44, 'VDecVy': -25.28, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -1.56, 'YDecy': 213.6,
         'VDecVx': 0.44, 'VDecVy': -25.28, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -1.52, 'YDecy': 212.4,
         'VDecVx': 0.4, 'VDecVy': -25, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -1.47, 'YDecy': 211.15,
         'VDecVx': 0.4, 'VDecVy': -25, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -1.44, 'YDecy': 209.95,
         'VDecVx': 0.4, 'VDecVy': -25, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -1.4, 'YDecy': 208.75,
         'VDecVx': 0.4, 'VDecVy': -25, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -1.33, 'YDecy': 207.55,
         'VDecVx': 0.4, 'VDecVy': -25, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -1.28, 'YDecy': 206.25,
         'VDecVx': 0.36, 'VDecVy': -24.39, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -1.24, 'YDecy': 205.05,
         'VDecVx': 0.33, 'VDecVy': -24.27, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -1.22, 'YDecy': 203.85,
         'VDecVx': 0.24, 'VDecVy': -24.19, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -1.21, 'YDecy': 202.6,
         'VDecVx': 0.12, 'VDecVy': -24.08, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -1.21, 'YDecy': 201.45,
         'VDecVx': 0.08, 'VDecVy': -23.94, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -1.2, 'YDecy': 200.25,
         'VDecVx': 0.11, 'VDecVy': -23.87, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -1.2, 'YDecy': 199.05,
         'VDecVx': 0.11, 'VDecVy': -23.87, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -1.19, 'YDecy': 197.95,
         'VDecVx': -0.03, 'VDecVy': -23.68, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -1.19, 'YDecy': 196.75,
         'VDecVx': -0.08, 'VDecVy': -23.61, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -1.2, 'YDecy': 195.55,
         'VDecVx': -0.12, 'VDecVy': -23.48, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -1.2, 'YDecy': 194.35,
         'VDecVx': -0.1, 'VDecVy': -23.42, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -1.2, 'YDecy': 193.2,
         'VDecVx': -0.1, 'VDecVy': -23.42, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -1.18, 'YDecy': 192.05,
         'VDecVx': -0.1, 'VDecVy': -23.42, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -1.17, 'YDecy': 190.9,
         'VDecVx': -0.1, 'VDecVy': -23.42, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -1.16, 'YDecy': 189.7,
         'VDecVx': -0.1, 'VDecVy': -23.42, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -1.17, 'YDecy': 188.55,
         'VDecVx': -0.1, 'VDecVy': -23.42, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -1.19, 'YDecy': 187.45,
         'VDecVx': -0.34, 'VDecVy': -22.97, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -1.2, 'YDecy': 186.3,
         'VDecVx': -0.34, 'VDecVy': -22.97, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -1.18, 'YDecy': 185.05,
         'VDecVx': -0.49, 'VDecVy': -22.85, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -1.18, 'YDecy': 183.9,
         'VDecVx': -0.54, 'VDecVy': -22.81, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -1.18, 'YDecy': 182.7,
         'VDecVx': -0.56, 'VDecVy': -22.78, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -1.17, 'YDecy': 181.6,
         'VDecVx': -0.51, 'VDecVy': -22.68, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -1.17, 'YDecy': 180.5,
         'VDecVx': -0.51, 'VDecVy': -22.68, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -1.18, 'YDecy': 179.4,
         'VDecVx': -0.51, 'VDecVy': -22.68, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -1.19, 'YDecy': 178.25,
         'VDecVx': -0.51, 'VDecVy': -22.68, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -1.17, 'YDecy': 177.1,
         'VDecVx': -0.23, 'VDecVy': -22.48, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -1.13, 'YDecy': 176.05,
         'VDecVx': -0.05, 'VDecVy': -22.4, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -1.1, 'YDecy': 174.95,
         'VDecVx': -0.05, 'VDecVy': -22.4, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -1.07, 'YDecy': 173.85,
         'VDecVx': -0.05, 'VDecVy': -22.4, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -1.05, 'YDecy': 172.75,
         'VDecVx': -0.05, 'VDecVy': -22.4, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -1.03, 'YDecy': 171.65,
         'VDecVx': -0.05, 'VDecVy': -22.4, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -1, 'YDecy': 170.6,
         'VDecVx': -0.05, 'VDecVy': -22.4, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -0.98, 'YDecy': 169.5,
         'VDecVx': -0.05, 'VDecVy': -22.4, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -0.98, 'YDecy': 168.5,
         'VDecVx': -0.19, 'VDecVy': -21.95, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -0.99, 'YDecy': 167.5,
         'VDecVx': -0.19, 'VDecVy': -21.95, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -1, 'YDecy': 166.5,
         'VDecVx': -0.19, 'VDecVy': -21.95, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -1.02, 'YDecy': 165.45,
         'VDecVx': -0.19, 'VDecVy': -21.95, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -1.02, 'YDecy': 164.35,
         'VDecVx': 0.02, 'VDecVy': -21.75, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -1.01, 'YDecy': 163.25,
         'VDecVx': 0.02, 'VDecVy': -21.75, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -0.96, 'YDecy': 162.05,
         'VDecVx': 0.16, 'VDecVy': -21.61, 'LineNum': 101},
        {'TargetId': 5087, 'XDecx': -0.91, 'YDecy': 160.9,
         'VDecVx': 0.21, 'VDecVy': -21.5, 'LineNum': 101},
        {'TargetId': 5087, 'XDecx': -0.85, 'YDecy': 159.85,
         'VDecVx': 0.3, 'VDecVy': -21.41, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -0.8, 'YDecy': 158.8,
         'VDecVx': 0.3, 'VDecVy': -21.41, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -0.76, 'YDecy': 157.75,
         'VDecVx': 0.3, 'VDecVy': -21.41, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -0.68, 'YDecy': 156.6,
         'VDecVx': 0.62, 'VDecVy': -21.18, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -0.59, 'YDecy': 155.45,
         'VDecVx': 0.79, 'VDecVy': -21.08, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -0.5, 'YDecy': 154.3,
         'VDecVx': 0.78, 'VDecVy': -21.04, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -0.43, 'YDecy': 153.25,
         'VDecVx': 0.73, 'VDecVy': -20.95, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -0.34, 'YDecy': 152.15,
         'VDecVx': 0.83, 'VDecVy': -20.86, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -0.26, 'YDecy': 151.1,
         'VDecVx': 0.84, 'VDecVy': -20.81, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -0.18, 'YDecy': 150.05,
         'VDecVx': 0.88, 'VDecVy': -20.73, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -0.1, 'YDecy': 148.95,
         'VDecVx': 0.93, 'VDecVy': -20.68, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': -0.01, 'YDecy': 147.9,
         'VDecVx': 0.96, 'VDecVy': -20.66, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 0.07, 'YDecy': 146.8,
         'VDecVx': 0.95, 'VDecVy': -20.62, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 0.14, 'YDecy': 145.75,
         'VDecVx': 0.95, 'VDecVy': -20.6, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 0.22, 'YDecy': 144.7,
         'VDecVx': 0.96, 'VDecVy': -20.55, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 0.29, 'YDecy': 143.7,
         'VDecVx': 0.93, 'VDecVy': -20.53, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 0.35, 'YDecy': 142.7,
         'VDecVx': 0.94, 'VDecVy': -20.49, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 0.42, 'YDecy': 141.6,
         'VDecVx': 0.94, 'VDecVy': -20.47, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 0.48, 'YDecy': 140.55,
         'VDecVx': 0.92, 'VDecVy': -20.42, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 0.53, 'YDecy': 139.5,
         'VDecVx': 0.84, 'VDecVy': -20.41, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 0.57, 'YDecy': 138.5,
         'VDecVx': 0.74, 'VDecVy': -20.41, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 0.6, 'YDecy': 137.45,
         'VDecVx': 0.68, 'VDecVy': -20.4, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 0.62, 'YDecy': 136.35,
         'VDecVx': 0.61, 'VDecVy': -20.35, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 0.63, 'YDecy': 135.4,
         'VDecVx': 0.48, 'VDecVy': -20.34, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 0.66, 'YDecy': 134.5,
         'VDecVx': 0.67, 'VDecVy': -20.29, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 0.69, 'YDecy': 133.5,
         'VDecVx': 0.68, 'VDecVy': -20.28, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 0.73, 'YDecy': 132.55,
         'VDecVx': 0.68, 'VDecVy': -20.28, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 0.76, 'YDecy': 131.6,
         'VDecVx': 0.69, 'VDecVy': -20.22, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 0.79, 'YDecy': 130.65,
         'VDecVx': 0.59, 'VDecVy': -20.22, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 0.81, 'YDecy': 129.7,
         'VDecVx': 0.63, 'VDecVy': -20.21, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 0.83, 'YDecy': 128.75,
         'VDecVx': 0.52, 'VDecVy': -20.15, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 0.85, 'YDecy': 127.85,
         'VDecVx': 0.52, 'VDecVy': -20.15, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 0.85, 'YDecy': 126.9,
         'VDecVx': 0.52, 'VDecVy': -20.15, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 0.88, 'YDecy': 125.95,
         'VDecVx': 0.74, 'VDecVy': -20.09, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 0.9, 'YDecy': 124.9,
         'VDecVx': 0.66, 'VDecVy': -20.08, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 0.93, 'YDecy': 123.8,
         'VDecVx': 0.73, 'VDecVy': -20.09, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 0.95, 'YDecy': 122.8,
         'VDecVx': 0.69, 'VDecVy': -20.02, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 0.97, 'YDecy': 121.7,
         'VDecVx': 0.7, 'VDecVy': -20.02, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.01, 'YDecy': 120.7,
         'VDecVx': 0.75, 'VDecVy': -19.96, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.04, 'YDecy': 119.65,
         'VDecVx': 0.79, 'VDecVy': -19.96, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.08, 'YDecy': 118.55,
         'VDecVx': 0.79, 'VDecVy': -19.95, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.13, 'YDecy': 117.5,
         'VDecVx': 0.87, 'VDecVy': -19.9, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.17, 'YDecy': 116.4,
         'VDecVx': 0.79, 'VDecVy': -19.89, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.2, 'YDecy': 115.3,
         'VDecVx': 0.76, 'VDecVy': -19.84, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.24, 'YDecy': 114.2,
         'VDecVx': 0.76, 'VDecVy': -19.82, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.26, 'YDecy': 113.1,
         'VDecVx': 0.7, 'VDecVy': -19.83, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.28, 'YDecy': 112.05,
         'VDecVx': 0.6, 'VDecVy': -19.76, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.29, 'YDecy': 111.1,
         'VDecVx': 0.48, 'VDecVy': -19.71, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.29, 'YDecy': 110.1,
         'VDecVx': 0.45, 'VDecVy': -19.75, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.29, 'YDecy': 109.05,
         'VDecVx': 0.44, 'VDecVy': -19.7, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.3, 'YDecy': 108.1,
         'VDecVx': 0.42, 'VDecVy': -19.69, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.3, 'YDecy': 107.05,
         'VDecVx': 0.37, 'VDecVy': -19.64, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.29, 'YDecy': 106.05,
         'VDecVx': 0.28, 'VDecVy': -19.62, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.28, 'YDecy': 105.05,
         'VDecVx': 0.25, 'VDecVy': -19.57, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.25, 'YDecy': 104.1,
         'VDecVx': 0.09, 'VDecVy': -19.55, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.23, 'YDecy': 103.1,
         'VDecVx': 0.13, 'VDecVy': -19.57, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.22, 'YDecy': 102.05,
         'VDecVx': 0.16, 'VDecVy': -19.55, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.23, 'YDecy': 101.05,
         'VDecVx': 0.33, 'VDecVy': -19.51, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.25, 'YDecy': 100,
         'VDecVx': 0.41, 'VDecVy': -19.49, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.27, 'YDecy': 99.05,
         'VDecVx': 0.42, 'VDecVy': -19.45, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.29, 'YDecy': 98,
         'VDecVx': 0.38, 'VDecVy': -19.48, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.31, 'YDecy': 96.95,
         'VDecVx': 0.46, 'VDecVy': -19.45, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.34, 'YDecy': 95.9,
         'VDecVx': 0.51, 'VDecVy': -19.43, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.38, 'YDecy': 94.95,
         'VDecVx': 0.58, 'VDecVy': -19.45, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.41, 'YDecy': 93.95,
         'VDecVx': 0.5, 'VDecVy': -19.43, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.44, 'YDecy': 93.05,
         'VDecVx': 0.53, 'VDecVy': -19.45, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.46, 'YDecy': 92.1,
         'VDecVx': 0.5, 'VDecVy': -19.43, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.48, 'YDecy': 91.15,
         'VDecVx': 0.4, 'VDecVy': -19.45, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.51, 'YDecy': 90.2,
         'VDecVx': 0.49, 'VDecVy': -19.49, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.51, 'YDecy': 89.3,
         'VDecVx': 0.27, 'VDecVy': -19.51, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.52, 'YDecy': 88.35,
         'VDecVx': 0.34, 'VDecVy': -19.55, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.52, 'YDecy': 87.35,
         'VDecVx': 0.21, 'VDecVy': -19.57, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.51, 'YDecy': 86.35,
         'VDecVx': 0.17, 'VDecVy': -19.55, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.5, 'YDecy': 85.35,
         'VDecVx': 0.13, 'VDecVy': -19.57, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.5, 'YDecy': 84.35,
         'VDecVx': 0.16, 'VDecVy': -19.62, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.47, 'YDecy': 83.35,
         'VDecVx': -0.04, 'VDecVy': -19.63, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.46, 'YDecy': 82.4,
         'VDecVx': 0.03, 'VDecVy': -19.68, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.45, 'YDecy': 81.4,
         'VDecVx': 0.09, 'VDecVy': -19.7, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.46, 'YDecy': 80.35,
         'VDecVx': 0.2, 'VDecVy': -19.69, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.45, 'YDecy': 79.35,
         'VDecVx': 0.1, 'VDecVy': -19.7, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.44, 'YDecy': 78.3,
         'VDecVx': -0.04, 'VDecVy': -19.75, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.42, 'YDecy': 77.3,
         'VDecVx': 0, 'VDecVy': -19.76, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.41, 'YDecy': 76.3,
         'VDecVx': -0.07, 'VDecVy': -19.81, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.37, 'YDecy': 75.3,
         'VDecVx': -0.23, 'VDecVy': -19.76, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.35, 'YDecy': 74.3,
         'VDecVx': -0.12, 'VDecVy': -19.81, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.34, 'YDecy': 73.35,
         'VDecVx': -0.03, 'VDecVy': -19.83, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.36, 'YDecy': 72.35,
         'VDecVx': 0.18, 'VDecVy': -19.82, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.37, 'YDecy': 71.4,
         'VDecVx': 0.21, 'VDecVy': -19.89, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.38, 'YDecy': 70.4,
         'VDecVx': 0.13, 'VDecVy': -19.89, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.36, 'YDecy': 69.5,
         'VDecVx': -0.12, 'VDecVy': -19.89, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.39, 'YDecy': 68.5,
         'VDecVx': 0.24, 'VDecVy': -19.89, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.38, 'YDecy': 67.6,
         'VDecVx': 0.03, 'VDecVy': -19.95, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.44, 'YDecy': 66.7,
         'VDecVx': 0.57, 'VDecVy': -19.96, 'LineNum': 101},
        {'TargetId': 5087, 'XDecx': 1.48, 'YDecy': 65.7,
         'VDecVx': 0.46, 'VDecVy': -19.97, 'LineNum': 101},
        {'TargetId': 5087, 'XDecx': 1.52, 'YDecy': 64.75,
         'VDecVx': 0.48, 'VDecVy': -19.97, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.54, 'YDecy': 63.7,
         'VDecVx': 0.22, 'VDecVy': -19.96, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.53, 'YDecy': 62.7,
         'VDecVx': 0.02, 'VDecVy': -20.01, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.53, 'YDecy': 61.7,
         'VDecVx': 0.07, 'VDecVy': -19.96, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.51, 'YDecy': 60.75,
         'VDecVx': -0.05, 'VDecVy': -19.95, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.5, 'YDecy': 59.75,
         'VDecVx': -0.05, 'VDecVy': -19.95, 'LineNum': 2},
        {'TargetId': 5087, 'XDecx': 1.48, 'YDecy': 58.8,
         'VDecVx': -0.05, 'VDecVy': -19.95, 'LineNum': 101},
        {'TargetId': 5087, 'XDecx': 1.45, 'YDecy': 57.8,
         'VDecVx': -0.05, 'VDecVy': -19.95, 'LineNum': 101},
        {'TargetId': 5087, 'XDecx': 1.44, 'YDecy': 56.9,
         'VDecVx': -0.16, 'VDecVy': -19.82, 'LineNum': 101},
        {'TargetId': 5087, 'XDecx': 1.41, 'YDecy': 56.05,
         'VDecVx': -0.32, 'VDecVy': -19.82, 'LineNum': 101},
        {'TargetId': 5087, 'XDecx': 1.39, 'YDecy': 55.15,
         'VDecVx': -0.32, 'VDecVy': -19.82, 'LineNum': 101},
        {'TargetId': 5087, 'XDecx': 1.35, 'YDecy': 54.3,
         'VDecVx': -0.32, 'VDecVy': -19.82, 'LineNum': 1},
        {'TargetId': 5087, 'XDecx': 1.39, 'YDecy': 53.4,
         'VDecVx': -0.23, 'VDecVy': -19.62, 'LineNum': 1},
        {'TargetId': 5087, 'XDecx': 1.42, 'YDecy': 52.5,
         'VDecVx': -0.23, 'VDecVy': -19.62, 'LineNum': 1},
        {'TargetId': 5087, 'XDecx': 1.43, 'YDecy': 51.55,
         'VDecVx': -0.23, 'VDecVy': -19.62, 'LineNum': 1},
        {'TargetId': 5087, 'XDecx': 1.44, 'YDecy': 50.65,
         'VDecVx': -0.23, 'VDecVy': -19.62, 'LineNum': 1},
        {'TargetId': 5087, 'XDecx': 1.48, 'YDecy': 49.75,
         'VDecVx': 0.13, 'VDecVy': -19.3, 'LineNum': 1},
        {'TargetId': 5087, 'XDecx': 1.52, 'YDecy': 48.85,
         'VDecVx': 0.13, 'VDecVy': -19.3, 'LineNum': 101},
        {'TargetId': 5087, 'XDecx': 1.55, 'YDecy': 47.95,
         'VDecVx': 0.13, 'VDecVy': -19.3, 'LineNum': 101},
        {'TargetId': 5087, 'XDecx': 1.56, 'YDecy': 47.05,
         'VDecVx': 0.13, 'VDecVy': -19.3, 'LineNum': 101},
        {'TargetId': 5087, 'XDecx': 1.57, 'YDecy': 46.1,
         'VDecVx': 0.13, 'VDecVy': -19.3, 'LineNum': 101},
        {'TargetId': 5087, 'XDecx': 1.6, 'YDecy': 45.2,
         'VDecVx': 0.13, 'VDecVy': -19.3, 'LineNum': 101},
        {'TargetId': 5087, 'XDecx': 1.61, 'YDecy': 44.25,
         'VDecVx': 0.13, 'VDecVy': -19.3, 'LineNum': 101},
        {'TargetId': 5087, 'XDecx': 1.62, 'YDecy': 43.35,
         'VDecVx': 0.13, 'VDecVy': -19.3, 'LineNum': 1},
        {'TargetId': 5087, 'XDecx': 1.65, 'YDecy': 42.4,
         'VDecVx': 0.13, 'VDecVy': -19.3, 'LineNum': 1},
        {'TargetId': 5087, 'XDecx': 1.7, 'YDecy': 41.45,
         'VDecVx': 0.13, 'VDecVy': -19.3, 'LineNum': 1},
        {'TargetId': 5087, 'XDecx': 1.74, 'YDecy': 40.55,
         'VDecVx': 0.13, 'VDecVy': -19.3, 'LineNum': 1},
        {'TargetId': 5087, 'XDecx': 1.77, 'YDecy': 39.6,
         'VDecVx': 0.13, 'VDecVy': -19.3, 'LineNum': 1},
        {'TargetId': 5087, 'XDecx': 1.78, 'YDecy': 38.65,
         'VDecVx': 0.13, 'VDecVy': -19.3, 'LineNum': 1},
        {'TargetId': 5087, 'XDecx': 1.82, 'YDecy': 37.7,
         'VDecVx': 0.13, 'VDecVy': -19.3, 'LineNum': 101},
        {'TargetId': 5087, 'XDecx': 1.84, 'YDecy': 36.75,
         'VDecVx': 0.13, 'VDecVy': -19.3, 'LineNum': 101},
        {'TargetId': 5087, 'XDecx': 1.86, 'YDecy': 35.8,
         'VDecVx': 0.13, 'VDecVy': -19.3, 'LineNum': 101},
        {'TargetId': 5087, 'XDecx': 1.87, 'YDecy': 34.85,
         'VDecVx': 0.13, 'VDecVy': -19.3, 'LineNum': 101},
        {'TargetId': 5087, 'XDecx': 1.89, 'YDecy': 33.9,
         'VDecVx': 0.13, 'VDecVy': -19.3, 'LineNum': 101},
        {'TargetId': 5087, 'XDecx': 1.91, 'YDecy': 32.95,
         'VDecVx': 0.13, 'VDecVy': -19.3, 'LineNum': 101},
        {'TargetId': 5087, 'XDecx': 1.92, 'YDecy': 32,
         'VDecVx': 0.13, 'VDecVy': -19.3, 'LineNum': 101},
        {'TargetId': 5087, 'XDecx': 1.95, 'YDecy': 31.05,
         'VDecVx': 0.13, 'VDecVy': -19.3, 'LineNum': 1},
        {'TargetId': 5087, 'XDecx': 2, 'YDecy': 30.1,
         'VDecVx': 0.13, 'VDecVy': -19.3, 'LineNum': 1},
        {'TargetId': 5087, 'XDecx': 2.04, 'YDecy': 29.1,
         'VDecVx': 0.13, 'VDecVy': -19.3, 'LineNum': 1},
        {'TargetId': 5087, 'XDecx': 2.06, 'YDecy': 28.15,
         'VDecVx': 0.13, 'VDecVy': -19.3, 'LineNum': 1},
        {'TargetId': 5087, 'XDecx': 2.08, 'YDecy': 27.2,
         'VDecVx': 0.13, 'VDecVy': -19.3, 'LineNum': 1},
        {'TargetId': 5087, 'XDecx': 2.12, 'YDecy': 26.25,
         'VDecVx': 0.13, 'VDecVy': -19.3, 'LineNum': 101},
        {'TargetId': 5087, 'XDecx': 2.14, 'YDecy': 25.3,
         'VDecVx': 0.13, 'VDecVy': -19.3, 'LineNum': 101},
        {'TargetId': 5087, 'XDecx': 2.16, 'YDecy': 24.3,
         'VDecVx': 0.13, 'VDecVy': -19.3, 'LineNum': 101},
        {'TargetId': 5087, 'XDecx': 2.17, 'YDecy': 23.35,
         'VDecVx': 0.13, 'VDecVy': -19.3, 'LineNum': 101},
        {'TargetId': 5087, 'XDecx': 2.19, 'YDecy': 22.4,
         'VDecVx': 0.13, 'VDecVy': -19.3, 'LineNum': 101},
        {'TargetId': 5087, 'XDecx': 2.21, 'YDecy': 21.45,
         'VDecVx': 0.13, 'VDecVy': -19.3, 'LineNum': 101},
        {'TargetId': 5087, 'XDecx': 2.22, 'YDecy': 20.45,
         'VDecVx': 0.13, 'VDecVy': -19.3, 'LineNum': 101},
        {'TargetId': 5087, 'XDecx': 2.22, 'YDecy': 19.5,
         'VDecVx': 0.13, 'VDecVy': -19.3, 'LineNum': 101},
        {'TargetId': 5087, 'XDecx': 2.27, 'YDecy': 18.55,
         'VDecVx': 0.13, 'VDecVy': -19.3, 'LineNum': 1},
        {'TargetId': 5087, 'XDecx': 2.31, 'YDecy': 17.6,
         'VDecVx': 0.13, 'VDecVy': -19.3, 'LineNum': 1},
        {'TargetId': 5087, 'XDecx': 2.34, 'YDecy': 16.6,
         'VDecVx': 0.13, 'VDecVy': -19.3, 'LineNum': 1},
        {'TargetId': 5087, 'XDecx': 2.36, 'YDecy': 15.65,
         'VDecVx': 0.13, 'VDecVy': -19.3, 'LineNum': 1},
        {'TargetId': 5087, 'XDecx': 2.4, 'YDecy': 14.7,
         'VDecVx': 0.13, 'VDecVy': -19.3, 'LineNum': 101},
        {'TargetId': 5087, 'XDecx': 2.43, 'YDecy': 13.75,
         'VDecVx': 0.13, 'VDecVy': -19.3, 'LineNum': 101},
        {'TargetId': 5087, 'XDecx': 2.44, 'YDecy': 12.75,
         'VDecVx': 0.13, 'VDecVy': -19.3, 'LineNum': 101},
        {'TargetId': 5087, 'XDecx': 2.45, 'YDecy': 11.8,
         'VDecVx': 0.13, 'VDecVy': -19.3, 'LineNum': 101},
        {'TargetId': 5087, 'XDecx': 2.48, 'YDecy': 10.85,
         'VDecVx': 0.13, 'VDecVy': -19.3, 'LineNum': 101},
        {'TargetId': 5087, 'XDecx': 2.5, 'YDecy': 9.9,
         'VDecVx': 0.13, 'VDecVy': -19.3, 'LineNum': 101},
        {'TargetId': 5087, 'XDecx': 2.51, 'YDecy': 8.9,
         'VDecVx': 0.13, 'VDecVy': -19.3, 'LineNum': 101},
        {'TargetId': 5087, 'XDecx': 2.51, 'YDecy': 7.95,
         'VDecVx': 0.13, 'VDecVy': -19.3, 'LineNum': 101},
        {'TargetId': 5087, 'XDecx': 2.57, 'YDecy': 7,
         'VDecVx': 0.13, 'VDecVy': -19.3, 'LineNum': 1},
        {'TargetId': 5087, 'XDecx': 2.61, 'YDecy': 6,
         'VDecVx': 0.13, 'VDecVy': -19.3, 'LineNum': 1},
        {'TargetId': 5087, 'XDecx': 2.64, 'YDecy': 5.05,
         'VDecVx': 0.13, 'VDecVy': -19.3, 'LineNum': 1},
        {'TargetId': 5087, 'XDecx': 2.66, 'YDecy': 4.1,
         'VDecVx': 0.13, 'VDecVy': -19.3, 'LineNum': 1},
        {'TargetId': 5087, 'XDecx': 2.69, 'YDecy': 3.15,
         'VDecVx': 0.13, 'VDecVy': -19.3, 'LineNum': 1},
        {'TargetId': 5086, 'XDecx': 2.72, 'YDecy': 2.15,
         'VDecVx': 0.13, 'VDecVy': -19.3, 'LineNum': 101},
        {'TargetId': 5087, 'XDecx': 2.74, 'YDecy': 1.2,
         'VDecVx': 0.13, 'VDecVy': -19.3, 'LineNum': 101},
        {'TargetId': 5087, 'XDecx': 2.75, 'YDecy': 0.25,
         'VDecVx': 0.13, 'VDecVy': -19.3, 'LineNum': 101}
    ]
    test_preprocess(test_data)
