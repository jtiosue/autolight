import tkinter as tk
import time
from playsound import playsound


def audioticks(filename=None):
    root = tk.Tk()
    root.title("Audioticks")
    root.geometry("500x500")
    tk.Label(root, text="Press <q> for minor ticks, <p> for major ticks").pack()

    def close():
        print("minorticks", str(minor_ticks))
        print("majorticks", str(major_ticks))
        root.destroy()

    tk.Button(root, text="Close and print", command=close).pack()

    minor_ticks, major_ticks = [], []
    minor = tk.StringVar(root, "Minor: " + str(minor_ticks))
    major = tk.StringVar(root, "Major: " + str(major_ticks))
    tk.Label(root, textvariable=minor, wraplength=350).pack()
    tk.Label(root, textvariable=major, wraplength=350).pack()

    t0 = []

    def minor_click():
        if not t0:
            if filename:
                playsound(filename, block=False)
            t0.append(time.time())
            major_ticks.append(0.0)
            major.set("Major: " + str(major_ticks))
        minor_ticks.append(round(time.time() - t0[0], 2))
        minor.set("Minor: " + str(minor_ticks))

    def major_click():
        if not t0:
            if filename:
                playsound(filename, block=False)
            t0.append(time.time())
            minor_ticks.append(0.0)
            minor.set("Minor: " + str(minor_ticks))
        major_ticks.append(round(time.time() - t0[0], 2))
        major.set("Major: " + str(major_ticks))

    root.bind("<q>", lambda e: minor_click())
    root.bind("<p>", lambda e: major_click())

    root.mainloop()
