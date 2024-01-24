[
    Clip(
        **{
            "filename": "audio.mp3",
            "end": 50,
            "majorticks": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        }
    ),
    # 50.0
    Clip(**{"filename": "some filename in top directory", "end": 1}),
    # 1.0 majortick
    Clip(
        **{
            "filename": "folder1/filename in folder1",
            "start": 2,
            "end": 5,
            "someglobalkey": "value",
        }
    ),
    # 4.0 majortick
    CompositeClip(
        [
            Clip(
                **{
                    "filename": "folder1/folder2/filename in folder2",
                    "start": 5,
                    "end": 8,
                    "someglobalkey": "value",
                    "volume": 0,
                }
            ),
            Clip(
                **{
                    "text": "hello world",
                    "duration": 3,
                    "filename": "folder1/folder2/filename in folder2",
                    "someglobalkey": "value",
                    "volume": 0,
                }
            ),
        ]
    ),
    # 7.0 majortick
    Clip(
        **{
            "filename": "folder1/filename again in folder1",
            "trim": "none",
            "end": 2,
            "someglobalkey": "value",
        }
    ),
    # 9.0 majortick
]
