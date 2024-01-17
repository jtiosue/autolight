import tkinter as tk
import time


def audioticks():
    root = tk.Tk()
    root.title("Audioticks")
    root.geometry("500x500")
    tk.Label(root, text="Press z").pack()

    def close():
        print(str(ticks))
        root.destroy()

    tk.Button(root, text="Close and print", command=close).pack()

    ticks = []
    v = tk.StringVar(root, str(ticks))
    ticks_label = tk.Label(root, textvariable=v, wraplength=350)
    ticks_label.pack()

    def click(t0=[]):
        if not t0:
            t0.append(time.time())
        ticks.append(round(time.time() - t0[0], 2))
        v.set(str(ticks))

    root.bind("<z>", lambda e: click())

    root.mainloop()
