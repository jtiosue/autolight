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

    def add_musttick(self, t, redraw=True):
        if self.get_tick_index(t, 0)[0]:
            return
        self.mustticks.append(
            (t, self.gui.ax.vlines(t, 0, 1, linestyle="-", color="k"))
        )
        if redraw:
            self.gui.redraw()

    def add_majortick(self, t, redraw=True):
        index = self.get_tick_index(t, 0)
        if index[0] or index[1]:
            return
        self.majorticks.append(
            (t, self.gui.ax.vlines(t, 0, 1, linestyle="--", color="k"))
        )
        if redraw:
            self.gui.redraw()

    def add_minortick(self, t, redraw=True):
        index = self.get_tick_index(t, 0)
        if index[0] or index[1] or index[2]:
            return
        self.minorticks.append(
            (t, self.gui.ax.vlines(t, 0, 1, linestyle=":", color="k"))
        )
        if redraw:
            self.gui.redraw()

    def clear_ticks(self):
        for _, l in self.majorticks:
            l.remove()
        for _, l in self.minorticks:
            l.remove()
        for _, l in self.mustticks:
            l.remove()
        self.mustticks, self.majorticks, self.minorticks = [], [], []

    def get_tick_index(self, t, eps=0):
        xlim = self.gui.ax.get_xlim()
        amount = (xlim[1] - xlim[0]) * eps
        index = [], [], []
        for i in range(len(self.mustticks)):
            if abs(self.mustticks[i][0] - t) < amount:
                index[0].append(i)
        for i in range(len(self.majorticks)):
            if abs(self.majorticks[i][0] - t) < amount:
                index[1].append(i)
        for i in range(len(self.minorticks)):
            if abs(self.minorticks[i][0] - t) < amount:
                index[2].append(i)
        return index

    def get_tickstamps(self):
        return (
            [x[0] for x in self.mustticks],
            [x[0] for x in self.majorticks],
            [x[0] for x in self.minorticks],
        )

    def find_ticks(self, redraw=False):
        gui = self.gui
        audio = gui.convolved_audio
        ts = gui.convolved_ts
        for i, t in enumerate(gui.convolved_ts):
            if t - gui.convolved_ts[0] > 0.05:
                break

        l = np.concatenate((np.linspace(0, 1, i // 4), np.linspace(1, 0, i // 4)))
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

    def toggle_tick(self, tick_index):
        if tick_index[0]:
            i = tick_index[0][0]
            self.majorticks.append(self.mustticks.pop(i))
            self.majorticks[-1][1].set(linestyle="--")
            new_index = [], [len(self.majorticks) - 1], []
        elif tick_index[1]:
            i = tick_index[1][0]
            self.minorticks.append(self.majorticks.pop(i))
            self.minorticks[-1][1].set(linestyle=":")
            new_index = [], [], [len(self.minorticks) - 1]
        else:
            i = tick_index[2][0]
            self.mustticks.append(self.minorticks.pop(i))
            self.mustticks[-1][1].set(linestyle="-")
            new_index = [len(self.mustticks) - 1], [], []

        return new_index

    def slide_tick(self, tick_index, direction):
        if tick_index[0]:
            i = tick_index[0][0]
            ticks = self.mustticks
        elif tick_index[1]:
            i = tick_index[1][0]
            ticks = self.majorticks
        else:
            i = tick_index[2][0]
            ticks = self.minorticks

        xlim = self.gui.ax.get_xlim()
        amount = (xlim[1] - xlim[0]) * direction * 0.01
        t, vline = ticks[i]
        t += amount
        linestyle = vline.get_linestyle()
        # need to fix this. Probalby make a single tick into a class of its own
        color = vline.get_color()
        vline.remove()
        ticks[i] = (t, self.gui.ax.vlines(t, 0, 1, linestyle=linestyle, color=color))

    def select_tick(self, tick_index, color):
        if tick_index[0]:
            i = tick_index[0][0]
            self.mustticks[i][1].set(color=color)
        elif tick_index[1]:
            i = tick_index[1][0]
            self.majorticks[i][1].set(color=color)
        else:
            i = tick_index[2][0]
            self.minorticks[i][1].set(color=color)

    def delete_tick(self, tick_index):
        if tick_index[0]:
            i = tick_index[0][0]
            ticks = self.mustticks
        elif tick_index[1]:
            i = tick_index[1][0]
            ticks = self.majorticks
        else:
            i = tick_index[2][0]
            ticks = self.minorticks

        vline = ticks.pop(i)[1]
        vline.remove()


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

        self.ticks = Ticks(self)

        self.t0, self.audio_process = None, None

        self.current_time = 0
        self.current_time_bar = self.ax.vlines(0, -1, 1, linestyle="-", color="orange")

        KeybindLogic(self)

        self.redraw()

    def update_xaxis(self):
        self.ax.set_xlim(
            self.current_center - self.time_window_half_size,
            self.current_center + self.time_window_half_size,
        )

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
            self.current_time, -1, 1, linestyle="-", color="orange"
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


class KeybindLogic:
    def __init__(self, gui):
        self.gui = gui
        self.ticks = self.gui.ticks

        # self.gui.fig.canvas.mpl_connect("key_press_event", self.key_event)
        self.gui.fig.canvas.mpl_connect("key_press_event", lambda e: self.key_event(e))
        # self.gui.fig.canvas.mpl_connect("button_press_event", self.click)
        self.gui.fig.canvas.mpl_connect("button_press_event", lambda e: self.click(e))
        # self.gui.fig.canvas.mpl_connect("button_release_event", self.unclick)
        # self.gui.fig.canvas.mpl_connect("motion_notify_event", self.motion)

        self.tick_selected_index = [], [], []
        self.is_tick_selected = False

    def click(self, event):
        # self.downclick_location = event.xdata
        # self.is_motion = False

        xlim = self.gui.ax.get_xlim()
        index = self.ticks.get_tick_index(event.xdata, 0.01)
        if index[0] or index[1] or index[2]:
            if self.is_tick_selected and index == self.tick_selected_index:
                self.tick_selected_index = self.ticks.toggle_tick(
                    self.tick_selected_index
                )
            else:
                if self.is_tick_selected:
                    self.ticks.select_tick(self.tick_selected_index, "black")
                self.tick_selected_index = index
                self.ticks.select_tick(index, "red")
                self.is_tick_selected = True
        elif self.is_tick_selected:
            self.ticks.select_tick(self.tick_selected_index, "black")
            self.is_tick_selected = False
        else:
            self.ticks.add_minortick(event.xdata)

        self.gui.redraw()

    # def unclick(self, event):
    #     if not self.is_motion:
    #         index = self.ticks.get_tick_index(event.xdata, 0)
    #     else:
    #         pass

    #     self.downclick_location = None
    #     self.is_motion = None

    # def motion(self, event):
    #     self.is_motion = True

    def key_event(self, event):
        if event.key == "right":
            if not self.is_tick_selected:
                self.gui.slide_xaxis(self.gui.time_window_half_size)
                self.gui.update_xaxis()
            else:
                self.ticks.slide_tick(self.tick_selected_index, 1)
        elif event.key == "left":
            if not self.is_tick_selected:
                self.gui.slide_xaxis(-self.gui.time_window_half_size)
                self.gui.update_xaxis()
            else:
                self.ticks.slide_tick(self.tick_selected_index, -1)
        elif event.key == "up":
            self.gui.time_window_half_size = max(
                self.gui.time_window_half_size / 2, 0.1
            )
            self.gui.slide_xaxis(0)
            self.gui.update_xaxis()
        elif event.key == "down":
            self.gui.time_window_half_size = min(
                self.gui.time_window_half_size * 2, self.gui.ts[-1] / 2
            )
            self.gui.slide_xaxis(0)
            self.gui.update_xaxis()
        elif event.key == " ":
            self.gui.toggle_audio()
        elif event.key == "r":
            if self.gui.audio_process is not None:
                self.ticks.add_musttick(time.time() - self.gui.t0)
        elif event.key == "e":
            if self.gui.audio_process is not None:
                self.ticks.add_majortick(time.time() - self.gui.t0)
        elif event.key == "w":
            if self.gui.audio_process is not None:
                self.ticks.add_minortick(time.time() - self.gui.t0)
        elif event.key == "a":
            self.gui.ticks.find_ticks()
        elif event.key == "backspace":
            if self.is_tick_selected:
                self.ticks.delete_tick(self.tick_selected_index)
                self.is_tick_selected = False
        elif event.key == "t":
            if self.is_tick_selected:
                self.tick_selected_index = self.ticks.toggle_tick(
                    self.tick_selected_index
                )

        self.gui.redraw()


if __name__ == "__main__":
    # filename = "/Users/jtiosue/Documents/Photos/audio/take-yours.wav"
    filename = "/Users/jtiosue/Documents/Photos/audio/submarines.wav"
    GUI(filename).show()
