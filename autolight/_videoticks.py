import cv2 as cv

__all__ = ("videoticks",)


class Window:
    def __init__(self, filename=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filename = filename
        self.ticks = []

        self.frame_num = 0
        self.video = cv.VideoCapture(filename)
        self.fps = int(round(self.video.get(cv.CAP_PROP_FPS)))
        self.framecount = self.video.get(cv.CAP_PROP_FRAME_COUNT)
        self.duration = self.framecount / self.fps

        self.trackbar_name = f"Time / {self.duration}:"

        cv.namedWindow("Frame")
        cv.createTrackbar(
            self.trackbar_name,
            "Frame",
            0,
            int(round(self.duration)),
            lambda e: 0,
        )

        self.speed = 2
        self.start_tick = 0

        self.start_video()

    def destroy(self):
        self.paused = True
        for start, end in self.ticks:
            print(dict(filename=self.filename, start=start, end=end), ",")
        if self.start_tick is not None:
            print(dict(filename=self.filename, start=self.start_tick), ",")
        self.video.release()
        cv.destroyAllWindows()

    def end_tick(self):
        end = round(self.frame_num / self.fps, 1)
        if self.start_tick is not None:
            self.ticks.append((self.start_tick, end))
        self.start_tick = None

    def start_video(self):
        while self.video.isOpened():
            for _ in range(self.speed):
                ret, frame = self.video.read()
                self.frame_num += 1

            # if frame is read correctly ret is True
            if not ret:
                self.destroy()
                break

            cv.imshow("Frame", frame)
            cv.setTrackbarPos(
                self.trackbar_name, "Frame", int(round(self.frame_num / self.fps))
            )
            k = cv.waitKey(25)
            if k == ord("q"):
                self.destroy()
            elif k == ord("e"):
                self.end_tick()
            elif k == ord("s"):
                self.start_tick = round(self.frame_num / self.fps, 1)
            elif k == 0:  # up arrow
                self.speed += 1
            elif k == 1:  # down arrow
                self.speed = max(self.speed - 1, 1)
            elif k == ord(" "):
                # pause
                k = cv.waitKey()
                if k == ord("q"):
                    self.destroy()


def videoticks(filename: str):
    Window(filename)


if __name__ == "__main__":
    from tkinter import filedialog

    videoticks(filedialog.askopenfilename())
