import matplotlib.pyplot as plt
from scipy.io.wavfile import read as read_wav
import numpy as np
import os, time

# from playsound import playsound
# import multiprocessing
from nava import play as playsound, stop as stopsound

plt.rcParams["keymap.back"].remove("backspace")

# import tkinter as tk
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def convolve_audio(audio, filter):
    return np.convolve(audio, filter, mode="same")  # [: -len(filter) + 1]


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


class Tick:
    must = "must"
    major = "major"
    minor = "minor"
    type_to_linestyle = dict(must="-", major="--", minor=":")
    toggle_type_order = dict(minor="major", major="must", must="minor")

    def __init__(self, tick_time, tick_type, ax):
        self.tick_type = tick_type
        self.ax = ax
        self.tick_time = tick_time
        self.color = "black"
        self.vline = None
        self.plot()

    def plot(self):
        self.vline = self.ax.axvline(
            self.tick_time,
            linestyle=Tick.type_to_linestyle[self.tick_type],
            color=self.color,
        )

    def toggle_type(self):
        self.tick_type = Tick.toggle_type_order[self.tick_type]
        self.vline.set_linestyle(Tick.type_to_linestyle[self.tick_type])

    def remove(self):
        self.vline.remove()

    def set_color(self, color):
        self.color = color
        self.vline.set_color(color)

    def set_time(self, tick_time):
        self.tick_time = tick_time
        self.remove()
        self.plot()

    def shift(self, direction, amount=0.01):
        xlim = self.ax.get_xlim()
        self.set_time(self.tick_time + (xlim[1] - xlim[0]) * direction * amount)

    def __lt__(self, other):
        if isinstance(other, Tick):
            return self.tick_time < other.tick_time
        return self.tick_time < other

    def __le__(self, other):
        if isinstance(other, Tick):
            return self.tick_time <= other.tick_time
        return self.tick_time <= other

    def __gt__(self, other):
        if isinstance(other, Tick):
            return self.tick_time > other.tick_time
        return self.tick_time > other

    def __ge__(self, other):
        if isinstance(other, Tick):
            return self.tick_time >= other.tick_time
        return self.tick_time >= other

    def __repr__(self):
        return f"Tick({self.tick_time}, {self.tick_type})"


class Ticks(list):

    def __init__(self, ax):
        self.ax = ax
        super().__init__()

    def pretty_str(self):
        must = [0] + list(
            sorted(round(x.tick_time, 2) for x in self if x.tick_type == Tick.must)
        )
        major = [0] + list(
            sorted(round(x.tick_time, 2) for x in self if x.tick_type == Tick.major)
        )
        minor = [0] + list(
            sorted(round(x.tick_time, 2) for x in self if x.tick_type == Tick.minor)
        )
        return f"must={must}\nmajor={major}\nminor={minor}"

    def pop(self, index=-1):
        tick = super().pop(index)
        tick.remove()
        return tick

    def index(self, tick, eps=0):
        # return closest tick
        xlim = self.ax.get_xlim()
        eps *= xlim[1] - xlim[0]
        tick_time = tick.tick_time if isinstance(tick, Tick) else tick

        index = min(range(len(self)), key=lambda x: abs(self[x].tick_time - tick_time))

        if abs(self[index].tick_time - tick_time) <= eps:
            return index

        raise ValueError("Tick time not found")

    def remove(self, tick, eps=0):
        i = self.index(tick, eps)
        self.pop(i)

    def clear_ticks(self):
        while self:
            self.pop()

    def add_tick(self, tick_time, tick_type):
        self.append(Tick(tick_time, tick_type, self.ax))

    def find_ticks(self, ts, audio):
        for i, t in enumerate(ts):
            if t - ts[0] > 0.05:
                break

        # l = np.concatenate((np.linspace(0, 1, i // 4), np.linspace(1, 0, i // 4)))
        l = [0, 0, 0, 0, 0, 1, 1, 1, 1]
        caudio = convolve_audio(audio, l / np.sum(l))
        # self.ax.plot(ts, caudio, "-", color="red")

        dt = (ts[1] - ts[0]) / 2.0

        last_t_minor, last_t_major, last_t_must = 0, 0, 0
        for i, t in enumerate(ts):
            if audio[i] > 2 * caudio[i]:
                mean = np.mean(audio[max(0, i - 10) : i]) if i else 0
                if (
                    # audio[i] > 7 * mean
                    # and
                    audio[i]
                    > 7 * caudio[i]
                    # and t - last_t_must > 0.2
                ):
                    last_t_must = t
                    last_t_major = t
                    last_t_minor = t
                    self.add_tick(t - dt, Tick.must)
                elif (
                    # audio[i] > 5 * mean
                    # and
                    audio[i]
                    > 5 * caudio[i]
                    # and t - last_t_major > 0.2
                ):
                    last_t_major = t
                    last_t_minor = t
                    self.add_tick(t - dt, Tick.major)
                # elif t - last_t_minor > 0.2:
                else:
                    last_t_minor = t
                    self.add_tick(t - dt, Tick.minor)


class AudioPlot:
    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.N, audio = read_wav(filename)
        self.audio = audio[:, 0]
        self.ts = self.index_to_second(np.arange(len(self.audio)))
        # self.audio = self.audio / np.max(np.abs(self.audio))

        lmin, lmax = hl_envelopes_idx(self.audio, dmin=10, dmax=10, split=True)

        self.audio = self.audio[lmax]
        # l = np.concatenate((np.linspace(0, 1, 5), np.linspace(1, 0, 5)))
        l = np.concatenate((np.geomspace(0.1, 1, 5), np.geomspace(1, 0.1, 5)))
        # l = [1 / 2, 1, 1 / 2]
        self.audio = convolve_audio(self.audio, l / np.sum(l))

        self.audio = self.audio / np.max(self.audio)
        self.ts = self.ts[lmax]

        self.fig = plt.figure()
        self.fig.set_size_inches(12, 10)
        plt.plot(self.ts, self.audio, "b")
        # plt.plot(
        #     self.ts[lmin],
        # convolve(self.audio[lmin], l / np.sum(l))
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

        self.t0, self.audio_process = None, None

        self.current_time = 0
        self.current_time_bar = Tick(-1, Tick.must, self.ax)
        self.current_time_bar.set_color("orange")

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
        self.current_time_bar.set_time(self.current_time)
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
            # self.audio_process = multiprocessing.Process(
            #     target=playsound, args=(self.filename,)
            # )
            # self.audio_process.start()
            self.audio_process = playsound(self.filename, True)
            # playsound(self.filename, False)
            self.t0 = time.time() + 0.37
            while self.audio_process is not None:
                plt.pause(1 / 30.0)
                self.current_time = time.time() - self.t0
                self.update_current_time()
                self.slide_xaxis()
                self.update_xaxis()
        else:
            self.stop_audio()

    def stop_audio(self):
        if self.audio_process is not None:
            stopsound(self.audio_process)
            self.audio_process = None


class GUI:
    def __init__(self, filename):
        self.audioplot = AudioPlot(filename)
        self.ticks = Ticks(self.audioplot.ax)

        # self.audioplot.fig.canvas.mpl_connect("key_press_event", self.key_event)
        self.audioplot.fig.canvas.mpl_connect(
            "key_press_event", lambda e: self.key_event(e)
        )
        # self.audioplot.fig.canvas.mpl_connect("button_press_event", self.click)
        self.audioplot.fig.canvas.mpl_connect(
            "button_press_event", lambda e: self.click(e)
        )
        # self.audioplot.fig.canvas.mpl_connect("button_release_event", self.unclick)
        # self.audioplot.fig.canvas.mpl_connect("motion_notify_event", self.motion)

        self.tick_selected_index = None
        self.panning = False

    def click(self, event):
        # self.downclick_location = event.xdata
        # self.is_motion = False
        if self.panning:
            return

        try:
            index = self.ticks.index(event.xdata, 0.01)
        except ValueError:
            index = None

        selected_tick = (
            self.ticks[self.tick_selected_index]
            if self.tick_selected_index is not None
            else None
        )
        tick = self.ticks[index] if index is not None else None

        if tick is not None:
            if index == self.tick_selected_index:
                tick.toggle_type()
            else:
                if selected_tick is not None:
                    selected_tick.set_color("black")
                self.tick_selected_index = index
                tick.set_color("red")
        elif selected_tick is not None:
            selected_tick.set_color("black")
            self.tick_selected_index = None
        else:
            self.ticks.add_tick(event.xdata, Tick.minor)

        self.audioplot.redraw()

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
        selected_tick = (
            self.ticks[self.tick_selected_index]
            if self.tick_selected_index is not None
            else None
        )

        if event.key == "right":
            if selected_tick is None:
                self.audioplot.slide_xaxis(self.audioplot.time_window_half_size)
                self.audioplot.update_xaxis()
            else:
                selected_tick.shift(1)
        elif event.key == "left":
            if selected_tick is None:
                self.audioplot.slide_xaxis(-self.audioplot.time_window_half_size)
                self.audioplot.update_xaxis()
            else:
                selected_tick.shift(-1)
        elif event.key == "up":
            self.audioplot.time_window_half_size = max(
                self.audioplot.time_window_half_size / 2, 0.1
            )
            self.audioplot.slide_xaxis(0)
            self.audioplot.update_xaxis()
        elif event.key == "down":
            self.audioplot.time_window_half_size = min(
                self.audioplot.time_window_half_size * 2, self.audioplot.ts[-1] / 2
            )
            self.audioplot.slide_xaxis(0)
            self.audioplot.update_xaxis()
        elif event.key == " ":
            self.audioplot.toggle_audio()
        elif event.key == "r":
            if self.audioplot.audio_process is not None:
                self.ticks.add_tick(time.time() - self.audioplot.t0, Tick.must)
        elif event.key == "e":
            if self.audioplot.audio_process is not None:
                self.ticks.add_tick(time.time() - self.audioplot.t0, Tick.major)
        elif event.key == "w":
            if self.audioplot.audio_process is not None:
                self.ticks.add_tick(time.time() - self.audioplot.t0, Tick.minor)
        elif event.key == "a":
            self.ticks.find_ticks(self.audioplot.ts, self.audioplot.audio)
        elif event.key == "backspace":
            if selected_tick is not None:
                self.ticks.pop(self.tick_selected_index)
                self.tick_selected_index = None
        elif event.key == "t":
            if selected_tick is not None:
                selected_tick.toggle_type()
        elif event.key == "p":
            self.panning = not self.panning

        self.redraw()

    def redraw(self):
        self.audioplot.redraw()

    def mainloop(self):
        self.audioplot.show()
        # self.audioplot.stop_audio()
        print(self.ticks.pretty_str())


# class TkGUI(tk.Tk):
#     def __init__(self, filename, *args, **kwargs):

#         self.filename = filename
#         super().__init__(*args, **kwargs)
#         # width = kwargs.get("width", 600)
#         # height = kwargs.get("height", 25)
#         self.title("Autolight audioticks")

#         self.gui = GUI(filename)

#         FigureCanvasTkAgg(self.gui.fig, master=self).get_tk_widget().pack()

#         tk.Label(self, text="helo world").pack()

#     def destroy(self):
#         """destroy.

#         Override the existing ``destroy`` function to include ``quit``. There
#         is a weird bug upon closing sometimes if you don't do this.

#         """
#         self.quit()
#         super().destroy()


if __name__ == "__main__":
    # filename = "/Users/jtiosue/Documents/Photos/audio/take-yours.wav"
    filename = "/Users/jtiosue/Documents/Photos/audio/submarines.wav"
    # filename = "/Users/jtiosue/Documents/Photos/audio/christmas-lights.wav"
    GUI(filename).mainloop()
    # make it so ticks can be read in.
