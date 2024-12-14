import matplotlib.pyplot as plt
from scipy.io.wavfile import read as read_wav
import numpy as np
import os, time
from playsound import playsound
import multiprocessing


def hl_envelopes_idx(s, dmin=1, dmax=1, split=False):
    # from https://stackoverflow.com/questions/34235530/how-to-get-high-and-low-envelope-of-a-signal
    """
    Input :
    s: 1d-array, data signal from which to extract high and low envelopes
    dmin, dmax: int, optional, size of chunks, use this if the size of the input signal is too big
    split: bool, optional, if True, split the signal in half along its mean, might help to generate the envelope in some cases
    Output :
    lmin,lmax : high/low envelope idx of input signal s
    """

    # locals min
    lmin = (np.diff(np.sign(np.diff(s))) > 0).nonzero()[0] + 1
    # locals max
    lmax = (np.diff(np.sign(np.diff(s))) < 0).nonzero()[0] + 1

    if split:
        # s_mid is zero if s centered around x-axis or more generally mean of signal
        s_mid = np.mean(s)
        # pre-sorting of locals min based on relative position with respect to s_mid
        lmin = lmin[s[lmin] < s_mid]
        # pre-sorting of local max based on relative position with respect to s_mid
        lmax = lmax[s[lmax] > s_mid]

    # global min of dmin-chunks of locals min
    lmin = lmin[
        [i + np.argmin(s[lmin[i : i + dmin]]) for i in range(0, len(lmin), dmin)]
    ]
    # global max of dmax-chunks of locals max
    lmax = lmax[
        [i + np.argmax(s[lmax[i : i + dmax]]) for i in range(0, len(lmax), dmax)]
    ]

    return lmin, lmax


class Ticks:
    def __init__(self, gui):
        self.mustticks, self.majorticks, self.minorticks = [], [], []
        self.mustticks_lines, self.majorticks_lines, self.minorticks_lines = [], [], []
        self.gui = gui

        gui.fig.canvas.mpl_connect("button_press_event", self.click)
        gui.fig.canvas.mpl_connect("button_release_event", self.unclick)
        # gui.fig.canvas.mpl_connect("motion_notify_event", self.motion)

    def add_musttick(self, time, redraw=True):
        self.mustticks_lines.append(
            self.gui.ax.vlines(time, -1, 1, linestyle="-", color="k")
        )
        self.mustticks.append(time)
        if redraw:
            self.gui.redraw()

    def add_majortick(self, time, redraw=True):
        self.majorticks_lines.append(
            self.gui.ax.vlines(time, -1, 1, linestyle="--", color="k")
        )
        self.majorticks.append(time)
        if redraw:
            self.gui.redraw()

    def add_minortick(self, time, redraw=True):
        self.minorticks_lines.append(
            self.gui.ax.vlines(time, -1, 1, linestyle=":", color="k")
        )
        self.minorticks.append(time)
        if redraw:
            self.gui.redraw()

    def clear_ticks(self):
        for l in self.majorticks_lines:
            l.remove()
        for l in self.minorticks_lines:
            l.remove()
        for l in self.mustticks_lines:
            l.remove()
        self.mustticks, self.majorticks, self.minorticks = [], [], []
        self.mustticks_lines, self.majorticks_lines, self.minorticks_lines = [], [], []

    def find_ticks(self, redraw=True):
        self.clear_ticks()
        gui = self.gui
        audio = gui.convolved_audio
        ts = gui.convolved_ts
        for i, t in enumerate(gui.convolved_ts):
            if t - gui.convolved_ts[0] > 0.05:
                break

        l = np.linspace(0.1, 1, i // 2)
        caudio = np.convolve(audio, l / np.sum(l))[: -len(l) + 1]

        dt = (ts[1] - ts[0]) / 2.0

        last_t_minor, last_t_major, last_t_must = 0, 0, 0
        for i, t in enumerate(ts):
            if audio[i] > 2 * caudio[i]:
                mean = np.mean(audio[max(0, i - 10) : i]) if i else 0
                if (
                    audio[i] > 7 * mean
                    and audio[i] > 7 * caudio[i]
                    and t - last_t_must > 0.2
                ):
                    last_t_must = t
                    last_t_major = t
                    last_t_minor = t
                    self.add_musttick(t - dt, False)
                elif (
                    audio[i] > 5 * mean
                    and audio[i] > 5 * caudio[i]
                    and t - last_t_major > 0.2
                ):
                    last_t_major = t
                    last_t_minor = t
                    self.add_majortick(t - dt, False)
                elif t - last_t_minor > 0.2:
                    last_t_minor = t
                    self.add_minortick(t - dt, False)
        if redraw:
            self.gui.redraw()

    def click(self, event):
        x = event.xdata
        if self.majorticks and abs(x - self.majorticks[-1]) < 0.01:
            # do something with it
            pass
        else:
            self.add_majortick(x)

    def unclick(self, event):
        pass


class GUI:
    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.N, audio = read_wav(filename)
        self.audio = audio[:, 0]
        self.ts = self.index_to_second(np.arange(len(self.audio)))
        self.audio = self.audio / np.max(np.abs(self.audio))

        self.fig = plt.figure()
        # plt.plot(self.ts, self.audio)
        # self.ax = self.fig.get_axes()[0]

        lmin, lmax = hl_envelopes_idx(self.audio, dmin=10, dmax=10, split=True)
        # plt.plot(self.ts[lmax], self.audio[lmax], "orange")
        # plt.plot(self.ts[lmin], self.audio[lmin], "b")
        l = np.array([10, 9, 5, 4, 3, 2, 1])
        self.convolved_audio = np.convolve(self.audio[lmax], l / np.sum(l))[
            : -len(l) + 1
        ]
        self.convolved_audio = self.convolved_audio / np.max(self.convolved_audio)
        self.convolved_ts = self.ts[lmax]

        self.convolved_audio = self.audio[lmax]
        self.convolved_ts = self.ts[lmax]

        plt.plot(self.convolved_ts, self.convolved_audio, "b")
        # plt.plot(
        #     self.ts[lmin],
        #     np.convolve(self.audio[lmin], l / np.sum(l))[: -len(l) + 1],
        #     "b",
        # )
        self.ax = self.fig.get_axes()[0]

        self.ax.set_ylabel("Amplitude")
        self.ax.set_xlabel("Time (seconds)")
        self.ax.set_title(os.path.basename(self.filename))

        self.ax.set_yticks([])
        self.ax.set_ylim(0, 1)

        self.time_window_half_size = 4
        self.current_center = 4
        self.update_xaxis()

        self.fig.canvas.mpl_connect("key_press_event", self.key_event)

        self.ticks = Ticks(self)

        self.t0, self.audio_process = None, None

        self.current_time = 0
        self.current_time_bar = self.ax.vlines(0, -1, 1, linestyle="-", color="r")

    def update_xaxis(self):
        self.ax.set_xlim(
            self.current_center - self.time_window_half_size,
            self.current_center + self.time_window_half_size,
        )
        self.redraw()

    def slide_xaxis(self, increment=0):
        self.current_center = max(
            min(
                self.current_center + increment,
                self.ts[-1] - self.time_window_half_size,
            ),
            self.time_window_half_size,
        )

    def update_current_time(self):
        self.current_time_bar.remove()
        self.current_time_bar = self.ax.vlines(
            self.current_time, -1, 1, linestyle="-", color="r"
        )
        self.current_center = self.current_time

    def index_to_second(self, index):
        return index / self.N

    def second_to_index(self, second):
        return round(self.N * second)

    def show(self):
        plt.show()

    def redraw(self):
        plt.draw()

    def toggle_audio(self):
        if self.audio_process is None:
            self.audio_process = multiprocessing.Process(
                target=playsound, args=(self.filename,)
            )
            self.audio_process.start()
            self.t0 = time.time() + 1.3
            while self.audio_process is not None:
                plt.pause(1 / 20.0)
                self.current_time = time.time() - self.t0
                self.update_current_time()
                self.slide_xaxis()
                self.update_xaxis()
        else:
            self.audio_process.terminate()
            self.audio_process = None

    def key_event(self, event):
        if event.key == "right":
            self.slide_xaxis(self.time_window_half_size)
            self.update_xaxis()
        elif event.key == "left":
            self.slide_xaxis(-self.time_window_half_size)
            self.update_xaxis()
        elif event.key == "up":
            self.time_window_half_size = max(self.time_window_half_size / 2, 0.1)
            self.slide_xaxis(0)
            self.update_xaxis()
        elif event.key == "down":
            self.time_window_half_size = min(
                self.time_window_half_size * 2, self.ts[-1] / 2
            )
            self.slide_xaxis(0)
            self.update_xaxis()
        elif event.key == "backspace":
            line = self.tick_lines.pop()
            self.ticks.pop()
            line.remove()
            self.redraw()
        elif event.key == " ":
            self.toggle_audio()
        elif event.key == "o":
            if self.audio_process is not None:
                self.add_tick(time.time() - self.t0, True)
        elif event.key == "w":
            if self.audio_process is not None:
                self.add_tick(time.time() - self.t0, False)
        elif event.key == "t":
            self.ticks.find_ticks()


if __name__ == "__main__":
    filename = "/Users/jtiosue/Documents/Photos/audio/take-yours.wav"
    # filename = "/Users/jtiosue/Documents/Photos/audio/submarines.wav"
    GUI(filename).show()
