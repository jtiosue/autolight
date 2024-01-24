[
    Clip(
        **{
            "filename": "media/audio1.mp3",
            "fadein": 5,
            "majorticks": [
                0,
                6.3,
                12.3,
                18.3,
                24.3,
                30.3,
                36.3,
                42.3,
                48.3,
                54.3,
                60.3,
                66.3,
                72.3,
                78.3,
                84.3,
                90.3,
                96.3,
                102.3,
            ],
            "minorticks": [
                0,
                3.3,
                9.3,
                15.3,
                21.3,
                27.3,
                33.3,
                39.3,
                45.3,
                51.3,
                57.3,
                63.3,
                69.3,
                75.3,
                81.3,
                87.3,
                93.3,
                99.3,
                105.3,
            ],
            "end": 110.32,
        }
    ),
    # 110.32
    Clip(
        **{
            "filename": "media/hockey.mp4",
            "start": 0.34999999999999964,
            "end": 9.65,
            "fadein": 5,
            "volume": 0,
            "trim": "none",
        }
    ),
    # 9.3 minortick
    CompositeClip(
        [
            Clip(
                **{
                    "filename": "media/lacy.mp4",
                    "start": 1.0,
                    "end": 9.0,
                    "fadeout": 1.2,
                    "crossfadein": 2,
                    "padding": -2,
                }
            ),
            Clip(
                **{
                    "text": "hello world",
                    "color": "red",
                    "fontsize": 40,
                    "duration": 8,
                    "position": ("center", "center"),
                    "fadein": 5,
                    "filename": "media/lacy.mp4",
                }
            ),
        ]
    ),
    # 15.3 minortick
    Clip(**{"filename": "media/hockey.mp4", "start": 100.0, "end": 115.0}),
    # 30.3 majortick
    Clip(**{"filename": "media/hockey.mp4", "start": 1.0, "end": 18.999999999999996}),
    # 48.3 majortick
    Clip(
        **{
            "filename": "media/lacy.mp4",
            "start": 11.000000000000002,
            "end": 29.0,
            "trim": "symmetric",
        }
    ),
    # 66.3 majortick
    Clip(**{"filename": "media/lacy.mp4", "start": 30.0, "end": 36.0, "trim": "end"}),
    # 72.3 majortick
    Clip(**{"filename": "media/hockey.mp4", "start": 8.499999999999996, "end": 41.5}),
    # 105.3 minortick
    Clip(**{"filename": "media/lacy.mp4", "start": 0, "end": 5, "trim": "none"}),
    # 110.3
    CompositeClip(
        [
            Clip(
                **{
                    "filename": "media/photo.png",
                    "duration": 2.019999999999996,
                    "fadeout": 5,
                    "position": ("center", "center"),
                    "crossfadein": 2,
                    "padding": -2,
                }
            ),
            Clip(
                **{
                    "text": "goodbye",
                    "duration": 2.019999999999996,
                    "fadeout": 5,
                    "position": ("center", "center"),
                    "color": "purple",
                    "fontsize": 50,
                    "filename": "media/photo.png",
                }
            ),
        ]
    ),
    # 110.32
]
