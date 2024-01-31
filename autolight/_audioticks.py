import tkinter as tk
import time
from playsound import playsound

__all__ = ("audioticks",)


class Window(tk.Tk):
    def __init__(self, filename=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filename = filename
        self.majorticks, self.minorticks = [], []

        self.title("Audioticks")
        self.geometry("500x500")
        tk.Label(self, text="Press <q> for minor ticks, <p> for major ticks").pack()
        tk.Button(self, text="Close and print", command=self.destroy).pack()

        self.minor = tk.StringVar(self, "Minor: " + str(self.minorticks))
        self.major = tk.StringVar(self, "Major: " + str(self.majorticks))
        tk.Label(self, textvariable=self.minor, wraplength=350).pack()
        tk.Label(self, textvariable=self.major, wraplength=350).pack()

        self.t0 = None

        self.bind("<q>", lambda e: self.click(False))
        self.bind("<p>", lambda e: self.click(True))

    def destroy(self, *args, **kwargs):
        print("minorticks", str(self.minorticks))
        print("majorticks", str(self.majorticks))
        super().destroy(*args, **kwargs)

    def click(self, major=False):
        ticks1 = self.majorticks if major else self.minorticks
        ticks2 = self.minorticks if major else self.majorticks
        label1 = self.major if major else self.minor
        label2 = self.minor if major else self.major
        string1 = "Major: " if major else "Minor: "
        string2 = "Minor: " if major else "Major: "
        if not self.t0:
            if self.filename:
                playsound(self.filename, block=False)
            self.t0 = time.time()
            ticks2.append(0.0)
            label2.set(string2 + str(ticks2))
        ticks1.append(round(time.time() - self.t0, 2))
        label1.set(string1 + str(ticks1))


def audioticks(filename=None):
    root = Window(filename)
    root.mainloop()


if __name__ == "__main__":
    audioticks()
