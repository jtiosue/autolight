import tkinter as tk
import time
from nava import play as playsound, stop as stopsound

__all__ = ("audioticks",)


class Window(tk.Tk):
    def __init__(self, filename=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filename = filename
        self.majorticks, self.minorticks = [0.0], [0.0]

        self.title("Audioticks")
        self.geometry("500x500")
        tk.Label(
            self,
            text="Press <q> for minor ticks, <p> for major ticks, <space> to toggle audio",
        ).pack()
        tk.Button(self, text="Close and print", command=self.destroy).pack()

        self.minor = tk.StringVar(self, "Minor: " + str(self.minorticks))
        self.major = tk.StringVar(self, "Major: " + str(self.majorticks))
        tk.Label(self, textvariable=self.minor, wraplength=350).pack()
        tk.Label(self, textvariable=self.major, wraplength=350).pack()

        self.t0, self.audio = None, None

        self.bind("<q>", lambda e: self.click(False))
        self.bind("<p>", lambda e: self.click(True))
        self.bind("<space>", lambda e: self.toggle_audio())

    def destroy(self, *args, **kwargs):
        print("minorticks", str(self.minorticks))
        print("majorticks", str(self.majorticks))
        super().destroy(*args, **kwargs)

    def click(self, major=False):
        ticks1 = self.majorticks if major else self.minorticks
        # ticks2 = self.minorticks if major else self.majorticks
        label1 = self.major if major else self.minor
        # label2 = self.minor if major else self.major
        string1 = "Major: " if major else "Minor: "
        # string2 = "Minor: " if major else "Major: "
        if self.t0 is None:
            self.toggle_audio()
        else:
            ticks1.append(round(time.time() - self.t0, 2))
            label1.set(string1 + str(ticks1))

    def toggle_audio(self):
        if self.filename:
            if self.audio is None:
                self.audio = playsound(self.filename, True)
            else:
                stopsound(self.audio)
                self.audio = None

        self.t0 = time.time() if self.t0 is None else None

    # def __call__(self):
    #     self.mainloop()


def audioticks(filename=None):
    Window(filename).mainloop()


if __name__ == "__main__":
    # audioticks()
    audioticks("/Users/jtiosue/Documents/Photos/audio/submarines.wav")
