import tkinter as tk
import time
from nava import play as playsound, stop as stopsound

__all__ = ("audioticks",)


class Window(tk.Tk):
    def __init__(self, filename=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filename = filename
        self.mustticks, self.majorticks, self.minorticks = [0.0], [0.0], [0.0]

        self.title("Audioticks")
        self.geometry("650x500")
        tk.Label(
            self,
            text="Press <w> for minor ticks, <e> for major ticks, <r> for must ticks, <space> to toggle audio",
        ).pack()
        tk.Button(self, text="Close and print", command=self.destroy).pack()

        self.minor = tk.StringVar(self, "Minor: " + str(self.minorticks))
        self.major = tk.StringVar(self, "Major: " + str(self.majorticks))
        self.must = tk.StringVar(self, "Must: " + str(self.mustticks))
        tk.Label(self, textvariable=self.minor, wraplength=350).pack()
        tk.Label(self, textvariable=self.major, wraplength=350).pack()
        tk.Label(self, textvariable=self.must, wraplength=350).pack()

        self.t0, self.audio = None, None

        self.bind("<r>", lambda e: self.click("must"))
        self.bind("<e>", lambda e: self.click("major"))
        self.bind("<w>", lambda e: self.click("minor"))
        self.bind("<space>", lambda e: self.toggle_audio())

    def destroy(self, *args, **kwargs):
        print("minorticks", str(self.minorticks))
        print("majorticks", str(self.majorticks))
        print("mustticks", str(self.mustticks))
        super().destroy(*args, **kwargs)

    def click(self, ticktype):
        match ticktype:
            case "minor":
                ticks1, label1, string1 = self.minorticks, self.minor, "Minor"
            case "major":
                ticks1, label1, string1 = self.majorticks, self.major, "Major"
            case "must":
                ticks1, label1, string1 = self.mustticks, self.must, "Must"
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
