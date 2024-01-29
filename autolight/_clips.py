from . import get_file_info

__all__ = "Clip", "CompositeClip", "VideoClips", "AudioClips"


# TO DO: make this a subclass of dict? Or maybe don't do this.
class Clip:
    DEFAULTS = dict(
        start=0,
        speed=1,
        padding=0,
        fontsize=40,
        font="Courier",
        color="red",
        stroke_width=1,
        bg_color=b"transparent",
        trim="symmetric",
        rotate=0,
        portrait=False,
        resize=False,
        resolution=720,
        majorticks=[],
        minorticks=[],
        debug=False,
    )

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

        self._videostart = self.start

        if "duration" in self:
            self._videoduration = self.duration
        else:
            self._videoend = self.end
            self._videoduration = (self._videoend - self._videostart) / self.speed

        for ticks in ("majorticks", "minorticks"):
            if ticks in self:
                tickslist = getattr(self, ticks)
                offset = tickslist[0]
                for i in range(1, len(tickslist)):
                    tickslist[i] += offset
                tickslist[0] = 0

        if self.debug:
            if "fps" not in self:
                self.fps = 10
            if "resolution" not in self:
                self.resolution = 240

    def __contains__(self, element):
        return element in self.__dict__

    def __getattr__(self, name):
        if name in self:
            return super().__getattr__(name)
        match name:
            case "end":
                if "duration" in self:
                    return self.start + self.duration
                time = get_file_info(self.filename, "Duration")
                setattr(self, name, time)
                return time
            case "duration":
                return (self.end - self.start) / self.speed
            case "kind":
                if self.is_text():
                    return "text"
                elif self.is_audio():
                    return "audio"
                elif self.is_video():
                    return "video"
                elif self.is_image():
                    return "image"
                else:
                    return "unknown"
            case "info":
                if self.is_text():
                    return self.text + f"({self.duration})"
                elif "filename" in self:
                    return (
                        self.filename + f"({round(self.start, 2)},{round(self.end, 2)})"
                    )
                else:
                    return ""
            case _:
                return Clip.DEFAULTS[name]

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def copy(self):
        return Clip(**self.__dict__)

    def is_text(self):
        return "text" in self

    def is_image(self):
        extensions = {".jpg", ".png", ".heic"}
        return (
            not self.is_text()
            and "filename" in self
            and endswith_extensions(self.filename, extensions)
        )

    def is_audio(self):
        extensions = {".mp3", ".m4a"}
        return (
            not self.is_text()
            and "filename" in self
            and endswith_extensions(self.filename, extensions)
        )

    def is_video(self):
        extensions = {".mp4", ".mov"}
        return (
            not self.is_text()
            and "filename" in self
            and endswith_extensions(self.filename, extensions)
        )

    def trim_clip(self, new_duration):
        if not 0 <= new_duration <= self._videoduration:
            raise ValueError(
                f"Trimming {str(self)} to duration {new_duration} is not possible"
            )
        if "duration" in self:
            self.duration = new_duration
            return
        shave = (self.duration - new_duration) * self.speed
        match self.trim:
            case "start":
                self.start = max(self.start + shave, self._videostart)
                self.end = min(self.start + new_duration * self.speed, self._videoend)
            case "end":
                self.end = min(self.end - shave, self._videoend)
                self.start = max(self.end - new_duration * self.speed, self._videostart)
            case _:  # symmetric or none
                self.start = max(self.start + shave / 2, self._videostart)
                self.end = min(self.start + new_duration * self.speed, self._videoend)

    def __str__(self) -> str:
        # return f"{type(self).__name__}(**{str({k: v for k, v in self.__dict__.items() if k[0] != '_'})})"
        return str({k: v for k, v in self.__dict__.items() if k[0] != "_"})

    def __repr__(self) -> str:
        return str(self)

    def is_trimmable(self):
        return self.trim != "none"

    def items(self):
        yield from self.__dict__.items()


class CompositeClip(Clip):
    """
    The first clip is the main clip. The rest are just along for the ride.
    When trimming, we trim with respect to the first clip.
    The rest of the clips are either kept at the same duration or shrunk
    if they need to be.
    For the rest of the clips, "padding" is with respect to the previous clip.
    """

    def __init__(self, clips):
        super().__setattr__("_initialized", False)
        self.clips = clips
        if not clips:
            raise ValueError("No clips provided to CompositeClip")
        elif not (
            all(c.is_audio() for c in clips) or all(not c.is_audio() for c in clips)
        ):
            raise ValueError(
                "CompositeClip must have either all audio clips or all video/image/text clips"
            )

        for i in range(1, len(clips)):
            if clips[i].duration + clips[i].padding > clips[0].duration:
                raise ValueError(
                    f"In CompositeClip, the first clip should be the longest (compared to others with padding): {clips}"
                )
        super().__init__(**clips[0].__dict__)
        self._initialized = True

    def __getitem__(self, key):
        return self.clips[key]

    def __len__(self):
        return len(self.clips)

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if name == "clips":
            return
        setattr(self.clips[0], name, value)
        if self._initialized and name in ("start", "end", "duration"):
            for i in range(1, len(self.clips)):
                c = self.clips[i]
                c.trim_clip(min(c.duration, self.duration - c.padding))
        elif self._initialized:
            for i in range(1, len(self.clips)):
                c = self.clips[i]
                if not (c.is_text() and name in ("width", "height")):
                    setattr(c, name, value)

    def copy(self):
        return CompositeClip([c.copy() for c in self.clips])

    def __str__(self):
        # return type(self).__name__ + "([" + ", ".join([str(x) for x in self]) + "])"
        return str([x for x in self])

    def __iter__(self):
        for c in self.clips:
            yield c


class VideoClips(list):
    def __init__(self, clips):
        super().__init__(clips)
        if any(c.is_audio() for c in self):
            raise ValueError("VideoClips should not contain any pure audio")

    def append(self, item):
        if item.is_audio():
            raise ValueError("VideoClips should not contain any pure audio")
        super().append(item)

    def extend(self, items):
        if any(item.is_audio() for item in items):
            raise ValueError("VideoClips should not contain any pure audio")
        super().extend(items)

    def copy(self):
        return VideoClips([x for x in self])

    def deepcopy(self):
        return VideoClips([x.copy() for x in self])

    @property
    def duration(self):
        return sum(c.duration + c.padding for c in self)

    @property
    def trimmable_duration(self):
        return sum(c.duration + c.padding for c in self if c.is_trimmable())

    @property
    def nontrimmable_duration(self):
        return sum(c.duration + c.padding for c in self if not c.is_trimmable())

    @property
    def num_trimmable(self):
        return sum(1 if x.is_trimmable() else 0 for x in self)

    @property
    def num_nontrimmable(self):
        return sum(1 if not x.is_trimmable() else 0 for x in self)

    def iter_with_endpoints(self):
        prev = 0
        for c in self:
            prev += c.padding + c.duration
            yield c, prev


class AudioClips(list):
    def __init__(self, clips):
        super().__init__(clips)
        if any(not c.is_audio() for c in self):
            raise ValueError("AudioClips should not contain any videos")

        self.compute_ticks()

    def compute_ticks(self):
        self.majorticks, self.minorticks, prev = [], [], 0.0
        for c in self:
            prev += c.padding
            self.majorticks.extend([prev + x for x in c.majorticks])
            self.minorticks.extend([prev + x for x in c.minorticks])
            prev += c.duration
        self.duration = prev
        self.majorticks = list(sorted(set(self.majorticks)))
        self.minorticks = list(sorted(set(self.minorticks)))
        self.rounded_majorticks = set(round(x, 2) for x in self.majorticks)
        self.rounded_minorticks = set(round(x, 2) for x in self.minorticks)

    def append(self, item):
        if not item.is_audio():
            raise ValueError("AudioClips should not contain any videos")
        super().append(item)
        self.compute_ticks()

    def extend(self, items):
        if any(not item.is_audio() for item in items):
            raise ValueError("AudioClips should not contain any videos")
        super().extend(items)
        self.compute_ticks()

    def copy(self):
        return VideoClips([x for x in self])

    def deepcopy(self):
        return VideoClips([x.copy() for x in self])

    def iter_with_endpoints(self):
        prev = 0
        for c in self:
            prev += c.padding + c.duration
            yield c, prev

    def avg_tick_dist(self, start=0, end=None):
        if end is None:
            end = self.duration
        ticks = list(
            sorted(
                set(x for x in self.majorticks + self.minorticks if start <= x <= end)
            )
        )
        tick_diff = [ticks[i + 1] - ticks[i] for i in range(len(ticks) - 1)]
        if ticks[-1] < self.duration:
            tick_diff.append(self.duration - ticks[-1])
        return sum(tick_diff) / len(tick_diff)

    def tick_type(self, timestamp):
        """
        Returns "majortick" if timestamp is a major tick.
        "minortick" for a minor tick.
        and "" if it is neither
        """
        if (t := round(timestamp, 2)) in self.rounded_majorticks:
            return "majortick"
        elif t in self.rounded_minorticks:
            return "minortick"
        return ""


def endswith_extensions(filename, extensions):
    return any(filename.lower().endswith(ext) for ext in extensions)
