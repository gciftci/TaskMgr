import tkinter as tk
from tkinter import ttk
from matplotlib import quiver
import psutil
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import time

USABLE_CORES = len(psutil.Process().cpu_affinity())
CPU_USAGE_DATA = {}
XARR = range(60)
REFRESH_RATE = 0.5

def update_core_usage(graph, core):
    while True:
        graph.clear()
        CPU_USAGE_DATA[core].append(psutil.cpu_percent(percpu=True, interval=0)[core-1])
        CPU_USAGE_DATA[core].pop(0)
        graph.set_xticks(np.arange(0, 60, 10))
        graph.set_yticks(np.arange(0, 100, 20))
        for tick in graph.xaxis.get_major_ticks():
            tick.tick1line.set_visible(False)
            tick.tick2line.set_visible(False)
            tick.label1.set_visible(False)
            tick.label2.set_visible(False)
        for tick in graph.yaxis.get_major_ticks():
            tick.tick1line.set_visible(False)
            tick.tick2line.set_visible(False)
            tick.label1.set_visible(False)
            tick.label2.set_visible(False)
        graph.grid(color='#d9eaf4', linestyle='-', linewidth=0.5)
        graph.set_ylim(0, 100)          # Set Y-Axis limits
        graph.set_xlim(0, 60)          # Set Y-Axis limits
        graph.plot(XARR, CPU_USAGE_DATA[core], color='#3c95c7')
        graph.fill_between(XARR, np.array(CPU_USAGE_DATA[core]), 0, where=np.array(CPU_USAGE_DATA[core])>=0, interpolate=True, color='#f1f6fa', alpha=1)
        time.sleep(REFRESH_RATE)

def print_thread_status():
    while True:
        for thread in threading.enumerate():
            if thread.name != 'Status-Thread':
                print(f"{thread.name}: {thread.is_alive()}")
                time.sleep(REFRESH_RATE)

def redraw(canvas):
    while True:
        if canvas:
            canvas.draw()
            time.sleep(REFRESH_RATE)

class CPUUsageGraph(tk.Tk):
    def __init__(self):
        super().__init__()
        print("test")
        self.title("CPU Usage Graph")
        self.geometry("1440x800")
        self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=8)
        self.rowconfigure(0, weight=4)
        self.rowconfigure(1, weight=6)
        self.rowconfigure(2, weight=2)

        # Threads
        self.core_threads = {'started': False}

        # LEFT
        self.left = tk.Frame(self, bg="green")
        self.left.grid(column=0, row=0, sticky=tk.NSEW, rowspan=3)

        # Right-TOP
        self.right_top = tk.Frame(self, bg="red")
        self.right_top.grid(column=1, row=0, sticky=tk.NSEW)

        # Right-middle
        self.right_middle = tk.Frame(self, bg="white")
        self.right_middle.grid(column=1, row=1, sticky=tk.NSEW)

        # Right-bottom
        self.right_right = tk.Frame(self, bg="red")
        self.right_right.grid(column=1, row=2, sticky=tk.NSEW)

        # Figure
        self.figure = plt.figure(figsize=(8,7))
        self.figure.subplots_adjust(left=0.1, right=0.9, bottom=0.1, top=0.9, wspace=0.1, hspace=0.2)
        # Plots:
        self.plots = {}

        j = 0
        for i in range(USABLE_CORES):
            q = i + 1
            CPU_USAGE_DATA[q] = [0] * 60
            self.plots[q] = plt.subplot(round(USABLE_CORES/2), 2, q)
            self.plots[q].spines["top"].set_color("#117dbb")
            self.plots[q].spines["left"].set_color("#117dbb")
            self.plots[q].spines["bottom"].set_color("#117dbb")
            self.plots[q].spines["right"].set_color("#117dbb")
            self.plots[q].spines["bottom"].set_linewidth(1)
            self.plots[q].set_xticks(np.arange(0, 60, 10))
            self.plots[q].set_yticks(np.arange(0, 100, 20))
            for tick in self.plots[q].xaxis.get_major_ticks():
                tick.tick1line.set_visible(False)
                tick.tick2line.set_visible(False)
                tick.label1.set_visible(False)
                tick.label2.set_visible(False)
            for tick in self.plots[q].yaxis.get_major_ticks():
                tick.tick1line.set_visible(False)
                tick.tick2line.set_visible(False)
                tick.label1.set_visible(False)
                tick.label2.set_visible(False)
            self.plots[q].grid(color='#d9eaf4', linestyle='-', linewidth=0.5)
            self.plots[q].set_ylim(0, 100)          # Set Y-Axis limits
            self.plots[q].set_xlim(0, 60)          # Set Y-Axis limits
            plt.plot(XARR, CPU_USAGE_DATA[q], color='#3c95c7')
            # if i < USABLE_CORES/2:
            #     print(f'1. i={q} -> col:{q} , row:1')
            #     self.plots[q] = plt.subplot(q, 1, i)
            #     plt.plot(self.xarr, self.cpu_usage_data, color='#3c95c7')
            # else:
            #     print(f'2. i={q} -> col:{j} , row:1')
            #     j += 1
            #     self.plots[q] = plt.subplot(j, 2, i)


        # Plot 1
        #self.figure, self.ax = plt.subplots()
        # self.ax = plt.subplot()
        # self.ax.spines["top"].set_color("#117dbb")
        # self.ax.spines["left"].set_color("#117dbb")
        # self.ax.spines["bottom"].set_color("#117dbb")
        # self.ax.spines["right"].set_color("#117dbb")
        # self.ax.spines["bottom"].set_linewidth(1)

        # Canvas
        self.canvas = FigureCanvasTkAgg(self.figure, self.right_middle)
        self.canvas.get_tk_widget().pack(expand=True)
        self.update_graph()
    #
    # EXPERIMENTAL
    #

    def start_thread(self, graph, i):  # sourcery skip: merge-dict-assign
        # start a new thread for each core
        self.core_threads = {}
        self.core_threads[graph] = threading.Thread(target=update_core_usage, args=(graph,i,), name=f'Core{i}-Thread')
        self.core_threads[graph].daemon = True
        self.core_threads[graph].start()

        # Start a new thread for thread-status
        self.status_thread = threading.Thread(target=print_thread_status, name='Status-Thread')
        self.status_thread.daemon = True
        self.status_thread.start()

        # Redraw-Thread
        # self.redraw_thread = threading.Thread(target=self.redraw, args=(canvas,), name='Redraw-Thread')
        # self.redraw_thread.daemon = True
        # self.redraw_thread.start()



    def update_graph(self):  # sourcery skip: extract-duplicate-method
        # Loop trough Plots
        #self.plots.clear()
        if self.core_threads['started'] == False:
            self.core_threads['started'] = True
            for i in self.plots:
                self.start_thread(self.plots[i], i)
        # Redraw-Thread
        redraw_thread = threading.Thread(target=redraw, args=(self.canvas,), name='Redraw-Thread')
        redraw_thread.daemon = True
        redraw_thread.start()

            #print(i, self.plots[i])
            # self.plots[i].clear()
            # print(self.xarr)
            # print(self.cpu_usage_data)
            # self.plots[i].plot(self.xarr, self.cpu_usage_data, color='#3c95c7')
            # self.plots[i].fill_between(self.xarr, np.array(self.cpu_usage_data), 0, where=np.array(self.cpu_usage_data)>=0, interpolate=True, color=draw_color, alpha=1)
        #self.after(REFRESH_RATE * 1000, self.update_graph)self.canvas.draw()

        # self.ax.clear()
        #self.ax.yaxis.set_ticklabels([])    # Remove Y-Axis Labels
        #self.ax.xaxis.set_ticklabels([])    # Remove X-Axis Labels
        #self.ax.set_xticks([])
        #self.ax.set_yticks([])





if __name__ == "__main__":
    app = CPUUsageGraph()
    app.mainloop()
