from pre_processing.pro_class.smooth import Exponential


def test_exp_smooth():
    # 数据包含了两种情况，正常平滑、两帧时间相距过远
    his_frames = {
        "ab8756de": [
            {
                "id": "ab8756de",
                "x": 20,
                "y": 60,
                "secMark": 50000,
                "timestamp": 50000,
            },
            {
                "id": "ab8756de",
                "x": 20,
                "y": 60,
                "secMark": 59100,
                "timestamp": 59100,
            },
            {
                "id": "ab8756de",
                "x": 30,
                "y": 65,
                "secMark": 59200,
                "timestamp": 59200,
            },
            {
                "id": "ab8756de",
                "x": 40,
                "y": 70,
                "secMark": 59300,
                "timestamp": 59300,
            },
            {
                "id": "ab8756de",
                "x": 50,
                "y": 75,
                "secMark": 59400,
                "timestamp": 59400,
            },
            {
                "id": "ab8756de",
                "x": 60,
                "y": 80,
                "secMark": 59500,
                "timestamp": 59500,
            },
            {
                "id": "ab8756de",
                "x": 70,
                "y": 85,
                "secMark": 59600,
                "timestamp": 59600,
            },
            {
                "id": "ab8756de",
                "x": 80,
                "y": 90,
                "secMark": 59700,
                "timestamp": 59700,
            },
            {
                "id": "ab8756de",
                "x": 90,
                "y": 95,
                "secMark": 59800,
                "timestamp": 59800,
            },
            {
                "id": "ab8756de",
                "x": 100,
                "y": 100,
                "secMark": 59900,
                "timestamp": 59900,
            },
        ],
        "ab8700de": [
            {
                "id": "ab8700de",
                "x": 100,
                "y": 100,
                "secMark": 56900,
                "timestamp": 56900,
            },
            {
                "id": "ab8700de",
                "x": 100,
                "y": 100,
                "secMark": 57000,
                "timestamp": 57000,
            },
        ],
    }

    current_frame = {
        "ab8756de": {
            "id": "ab8756de",
            "x": 130,
            "y": 110,
            "secMark": 100,
        },
        "ab8700de": {
            "id": "ab8700de",
            "x": 130,
            "y": 110,
            "secMark": 100,
        },
    }
    last_timestamp = 59900
    sexp = Exponential()
    new_current_frame, last_timestamp = sexp.run(
        his_frames, current_frame, last_timestamp
    )

    assert new_current_frame["ab8756de"]["x"] == 124
    assert new_current_frame["ab8756de"]["y"] == 108
    assert new_current_frame["ab8700de"]["x"] == 130
    assert new_current_frame["ab8700de"]["y"] == 110
    assert len(new_current_frame) == len(his_frames) == 2
