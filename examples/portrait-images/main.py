import autolight as al

options = dict(resolution=540, fps=15)
# options = dict(width=700, height=500)

video = al.VideoClips(
    [
        al.Clip(filename="portrait1.jpg", duration=2, portrait=True, **options),
        al.Clip(
            filename="portrait2.png", duration=2, portrait=True, pan="down", **options
        ),
        al.Clip(filename="panorama.png", duration=3, **options),
        al.Clip(filename="landscape.png", duration=2, **options),
        al.Clip(filename="panorama.png", duration=3, pan="left", **options),
        al.Clip(filename="video.MP4", end=1, **options),
    ]
)

audio = al.AudioClips([])

# print([x for x in video.iter_with_endpoints()])

al.generate_file_moviepy("main", audio, video)
