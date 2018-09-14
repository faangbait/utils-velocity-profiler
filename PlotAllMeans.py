from tkinter import Tk, Label, Button, Entry
import PyGnuplot as gp
import numpy as np
import os
import glob


class PlotAllMeans:
    def __init__(self, master):
        self.master = master
        master.title("Plot All Means")
        
        self.descr = Label(master, text="These settings should match what was entered into the anemometer setup:")
        self.lblFan = Label(master, text="Fan Name:")
        self.fanname = Entry(master)
        self.lblPer = Label(master, text="Percentage:")
        self.percent = Entry(master)
        self.go_button = Button(master, text="Generate Plot", command=lambda: self.plot(self.fanname.get()+"_"+self.percent.get()+"per_*ft.csv"))
        self.descr.pack()
        self.lblFan.pack()
        self.fanname.pack()
        self.lblPer.pack()
        self.percent.pack()
        self.go_button.pack()
        
    def plot(self,fanargs):
        print(fanargs)
        files=glob.glob("/home/pi/anemometer/data/"+fanargs)
        os.system("rm /home/pi/anemometer/bigplot.tmp")


      #  gp.c('set term png size 1920,1080')
      #  gp.c('set output "/var/www/html/bigplot.png"')
        gp.c('set title "Plot All Means"')
        gp.c('set pointsize 1')
        gp.c('set datafile separator ","')
        #gp.c('set yrange [0:100]')
        #gp.c('set ytics 5 nomirror tc rgb "blue"')
        gp.c('set ylabel "Velocity (ft/min)" tc lt -1')
        gp.c('set key above right vertical box 3')
        gp.c('set print "/home/pi/anemometer/bigplot.tmp" append')

        for file in files:
                os.system("cat " + file + ">> /home/pi/anemometer/bigplot.csv")
                gp.c('stats "'+file+'" using 5:4 nooutput')
                gp.c('print STATS_mean_x,STATS_mean_y*196.8504,STATS_stddev_y*2*196.8504')


        gp.c('set datafile separator " "')
        gp.c('set style fill transparent solid 0.5 noborder')

        gp.c('plot "< sort -n /home/pi/anemometer/bigplot.tmp" u 1:($2+$3):($2-$3) "%lf %lf %lf" w filledcu lc rgb "forest-green", "< sort -n /home/pi/anemometer/bigplot.tmp" u 1:2 w lines lw 4')

        
root = Tk()
my_gui = PlotAllMeans(root)
root.mainloop()
