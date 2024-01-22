from pre_processing.pro_class.complete import Interpolation


def test_complement_interpolation():
    his_frames = {
        "ab8756de": [
            {
                "id": "ab8756de",
                "secMark": 59900,
                "timeStamp": 59900,
                "ptcType": "motor",
                "x": 98,
                "y": 100,
                "speed": 500,
                "heading": 7200,
            },
            {
                "id": "ab8756de",
                "secMark": 100,
                "timeStamp": 60100,
                "ptcType": "motor",
                "x": 98.5,
                "y": 100,
                "speed": 500,
                "heading": 7200,
            },
            {
                "id": "ab8756de",
                "secMark": 300,
                "timeStamp": 60300,
                "ptcType": "motor",
                "x": 99.5,
                "y": 100,
                "speed": 500,
                "heading": 7200,
            },
        ],
        "ab8701de": [
            {
                "id": "ab8701de",
                "secMark": 59900,
                "timeStamp": 59900,
                "ptcType": "motor",
                "x": 46,
                "y": 100,
                "speed": 1000,
                "heading": 7200,
            },
            {
                "id": "ab8701de",
                "secMark": 100,
                "timeStamp": 60100,
                "ptcType": "motor",
                "x": 56,
                "y": 100,
                "speed": 1000,
                "heading": 7200,
            },
            {
                "id": "ab8701de",
                "secMark": 200,
                "timeStamp": 60200,
                "ptcType": "motor",
                "x": 66,
                "y": 100,
                "speed": 1000,
                "heading": 7200,
            },
            {
                "id": "ab8701de",
                "secMark": 300,
                "timeStamp": 60300,
                "ptcType": "motor",
                "x": 77,
                "y": 100,
                "speed": 1000,
                "heading": 7200,
            },
        ],
        "ab8756an": [
            {
                "id": "ab8756an",
                "secMark": 59900,
                "timeStamp": 59900,
                "ptcType": "motor",
                "x": 98,
                "y": 100,
                "speed": 500,
                "heading": 7200,
            },
            {
                "id": "ab8756an",
                "secMark": 100,
                "timeStamp": 60100,
                "ptcType": "motor",
                "x": 98.5,
                "y": 100,
                "speed": 500,
                "heading": 7200,
            },
            {
                "id": "ab8756an",
                "secMark": 300,
                "timeStamp": 60300,
                "ptcType": "motor",
                "x": 120,
                "y": 130,
                "speed": 500,
                "heading": 7200,
            },
        ],
    }
    latest_frame = {
        "ab8756de": {
            "id": "ab8756de",
            "ptcType": "motor",
            "secMark": 400,
            "x": 100,
            "y": 100,
            "speed": 500,
            "heading": 7200,
        },
        "ab8701de": {
            "id": "ab8701de",
            "secMark": 400,
            "ptcType": "motor",
            "x": 88,
            "y": 100,
            "speed": 1000,
            "heading": 7200,
        },
        "ab8756an": {
            "id": "ab8756an",
            "ptcType": "motor",
            "secMark": 400,
            "x": 100,
            "y": 100,
            "speed": 500,
            "heading": 7200,
        },
    }
    last_timestamp = 60300
    pred = Interpolation()
    pred.run(his_frames, latest_frame, last_timestamp)

    assert len(his_frames["ab8756de"]) == 5
    assert len(his_frames["ab8701de"]) == 5
    assert len(his_frames["ab8756an"]) == 4
    assert his_frames["ab8756de"][2]["x"] == 99.0
    assert his_frames["ab8756de"][2]["y"] == 100
    assert his_frames["ab8756de"][2]["secMark"] == 200


if __name__ == "__main__":
    test_complement_interpolation()