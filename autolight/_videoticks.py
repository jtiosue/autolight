import datetime
import tkinter as tk
from tkVideoPlayer import TkinterVideo


### modified from:
### https://github.com/PaulleDemon/tkVideoPlayer/blob/master/examples/sample_player.py


__all__ = ("videoticks",)


class Window(tk.Tk):
    def __init__(self, filename=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filename = filename
        self.ticks = []

        self.title("Videoticks")
        # self.geometry("1920x1080")
        tk.Label(
            self,
            text="Press <t> for ticks, <space> to toggle play/pause",
        ).pack()

        self.video_player = TkinterVideo(scaled=True, master=self)
        self.video_player.pack(expand=True, fill="both")
        self.video_player.load(filename)

        self.play_pause_btn = tk.Button(self, text="Play", command=self.play_pause)
        self.play_pause_btn.pack()

        self.video_player.bind("<<Duration>>", lambda e: self.update_duration())
        self.video_player.bind("<<SecondChanged>>", lambda e: self.update_scale())
        self.video_player.bind("<<Ended>>", lambda e: self.video_ended())

        self.progress_value = tk.IntVar(self)

        self.progress_slider = tk.Scale(
            self,
            variable=self.progress_value,
            from_=0,
            to=0,
            orient="horizontal",
            command=self.seek,
        )
        # progress_slider.bind("<ButtonRelease-1>", seek)
        # self.progress_slider.pack(side="left", fill="x", expand=True)
        self.progress_slider.pack(fill="x")

        self.end_time = tk.StringVar(
            self,
            "Duration: 0",
        )
        tk.Label(self, textvariable=self.end_time).pack()

        self.progress_slider.config(
            to=self.video_player.video_info()["duration"], from_=0
        )
        self.play_pause_btn["text"] = "Play"
        self.progress_value.set(0)

        self.ticks_label = tk.StringVar(self, "Ticks: " + str(self.ticks))
        tk.Label(self, textvariable=self.ticks_label, wraplength=650).pack()

        self.bind("<t>", lambda e: self.tick())
        self.bind("<space>", lambda e: self.play_pause())

    def destroy(self, *args, **kwargs):
        if len(self.ticks) % 2:
            self.ticks.append(-1)
        for i in range(0, len(self.ticks), 2):
            d = dict(filename=self.filename, start=self.ticks[i])
            if self.ticks[i + 1] != -1:
                d["end"] = self.ticks[i + 1]
            print(d, ",")
        super().destroy(*args, **kwargs)

    def seek(self, value):
        """used to seek a specific timeframe"""
        self.video_player.seek(int(value))

    def tick(self):
        self.ticks.append(round(self.video_player.current_duration(), 1))
        self.ticks_label.set("Ticks: " + str(self.ticks))

    def play_pause(self):
        if self.video_player.is_paused():
            self.video_player.play()
            self.play_pause_btn["text"] = "Pause"

        else:
            self.video_player.pause()
            self.play_pause_btn["text"] = "Play"

    def update_duration(self):
        """updates the duration after finding the duration"""
        duration = self.video_player.video_info()["duration"]
        # duration = self.video_player.current_duration()
        # self.start_time.set(str(datetime.timedelta(seconds=self.video_player.current_duration())))
        self.end_time.set(
            "Duration: " + str(datetime.timedelta(seconds=round(duration)))
        )
        # self.end_time["text"] = str(duration)
        self.progress_slider["to"] = duration

    def update_scale(self):
        """updates the scale value"""
        self.progress_value.set(self.video_player.current_duration())

    def video_ended(self):
        """handle video ended"""
        self.progress_slider.set(self.progress_slider["to"])
        self.play_pause_btn["text"] = "Play"
        self.progress_slider.set(0)


def videoticks(filename: str):
    Window(filename).mainloop()


if __name__ == "__main__":
    from tkinter import filedialog

    videoticks(filedialog.askopenfilename())
