# > main.py
# > main.py -b:2018.01.01 - all data analysis from 01 january 2018
# > main.py -e:2018.05.01 - all data analysis to 01 may 2018
# > main.py -t:AUDUSD+AUDNZD+NZDUSD - data analysis of AUDUSD, AUDNZD and NZDUSD for all time
# > main.py -b:2015.01.01 -e:2018.10.01 -t:AUDNZD+AUDUSD+NZDUSD - data analysis from 2015.01.01 to 2018.10.01 of AUDNZD and AUDUSD and NZDUSD


# ==============================


import os
import datetime
import csv
from matplotlib import pyplot as plt
from dateutil import parser
import sys
# ==============================


DATADIR = "data"
OUTDIR = "out"
SMAperiod = 50
Kperiod = 50
# ==============================


class Bar:
    def __init__(self, initstr):
        # dd.MM.YYYY HH:mm:ss;1,13948;1,13956;1,13913;1,13956;17,0
        separated = initstr.replace("\n", "").replace(',', '.').split(';')
        self.date = separated[0].split(' ')[0]
        self.date = self.date[6:] + '.' + self.date[3:5] + '.' + self.date[:2]
        self.date = parser.parse(self.date)
        self.time = separated[0].split(' ')[1]
        self.dayofweek = self.date.weekday() # 0 - Monday, 6 - Sunday
        self.open = float(separated[1])
        self.high = float(separated[2])
        self.low = float(separated[3])
        self.close = float(separated[4])
        self.volume = float(separated[5])
# ==============================


def getDatafilesList(datadir):
    fileslist = []
    short = []
    currdir = os.getcwd()
    for (dirpath, dirnames, filenames) in os.walk(currdir + "\\" + datadir):
        for filename in filenames:
            if '.csv' in filename:
                fileslist.append(currdir + "\\" + datadir + "\\" + filename)
                short.append(filename[:6])
    return fileslist, short
# ------------------------------


def loadBars(barsfile, startdate, enddate):
    f = open(barsfile, 'r')
    bars = []
    line = f.readline()
    line = f.readline()
    while line != "":
        bar = Bar(line)
        if bar.date >= startdate and bar.date <= enddate:
                bars.append(bar)
        line = f.readline()
    return bars
# ------------------------------


def saveOutFile(ticker, data):
    outfile = os.getcwd() + "\\" + OUTDIR + "\\" + ticker + "_" + data[1][0] + "-" + data[-1][0] + ".csv"
    print("Save data to file", outfile)
    with open(outfile, 'w', newline = "") as writeFile:
        writer = csv.writer(writeFile, delimiter = ";")
        writer.writerows(data)
    writeFile.close()
# ------------------------------


def getSMA(data, period):
    out = []
    for idx in range(len(data)):
        minidx = max(0, idx - period + 1)
        out.append(sum(data[minidx:idx + 1]) / (idx - minidx + 1))
    return out
# ------------------------------


def saveChartToPDF(data, ticker):
    jpgfile = os.getcwd() + "\\" + OUTDIR + "\\" + ticker + "_" + data[0][0] + "-" + data[-1][0] + ".jpg"
    print("Saving graph to", jpgfile)
    date = [parser.parse(i[0]) for i in data]
    sumHL = [float(i[2]) for i in data]
    K = [float(i[4]) for i in data]
    sma = getSMA(sumHL, SMAperiod)
    Ksma = getSMA(K, Kperiod)

    fig, ax1 = plt.subplots()

    plt.title(ticker)

    ax1.plot(date, sumHL, 'b.')
    ax1.plot(date, sma, 'r-')
    ax1.set_ylabel('Sum HL intraday + SMA(' + str(SMAperiod) + ')', color='b')
    ax1.tick_params('y', colors='b')

    ax2 = ax1.twinx()
    ax2.plot(date, Ksma, 'g-')
    ax2.set_ylabel('SumHL / DayHL SMA(' + str(Kperiod) + ')', color='g')
    ax2.tick_params('y', colors='g')

    fig.tight_layout()

    plt.savefig(jpgfile)
    plt.close()
# ------------------------------


def go(startdate, enddate, tickers):
    # load filenames with data
    files, short = getDatafilesList(DATADIR)
    # for file in files of data:
    for i in range(len(files)):
        # is datafile with nesessary ticker
        needed = False
        if len(tickers) == 0:
            needed = True
        else:
            for ticker in tickers:
                if ticker == short[i]:
                    needed = True
        if needed:
            print("Working with file", short[i])
            # load bardata
            print("Loading bar data...")
            bars = loadBars(files[i], startdate, enddate)
            # outdata
            outdata = [["Date", "Day of week", "SumHL", "DayHL", "SumHL / DayHL"]]
            # temp intraday variables
            bar = bars[0]
            sumHL = bar.high - bar.low
            dayH = bar.high
            dayL = bar.low
            date = bar.date
            day = bar.dayofweek
            # for each bar in bardata:
            for idx in range(1, len(bars)):
                # if new day
                if bars[idx].date != date and bars[idx - 1] != 6:
                    # save day data to file
                    outdata.append([bars[idx - 1].date.strftime("%Y.%m.%d"), bars[idx - 1].dayofweek, "{0:.5f}".format(sumHL),
                                    "{0:.5f}".format(dayH - dayL), "{0:.5f}".format(sumHL / max(0.0001, (dayH - dayL)))])
                    sumHL = bars[idx].high - bars[idx].low
                    dayH = bars[idx].high
                    dayL = bars[idx].low
                    date = bars[idx].date
                    day = bars[idx].dayofweek
                else:
                    # calculate summ of each bar's HL of each day
                    sumHL += bars[idx].high - bars[idx].low
                    # calculate HL of the day
                    if bars[idx].high > dayH:
                        dayH = bars[idx].high
                    if bars[idx].low < dayL:
                        dayL = bars[idx].low
                    # update date and dayofweek (what if monday...)
                    date = bars[idx].date
                    day = bars[idx].dayofweek
            # save outfile
            saveOutFile(short[i], outdata)
            saveChartToPDF(outdata[1:], short[i])
        else:
            print(short[i], "is not needed...")


# ==============================
if __name__ == "__main__":
    params = sys.argv
    startdate = parser.parse("1970.01.01")
    enddate = datetime.datetime.now()
    tickers = []
    if len(params) > 1:
        for idx in range(1, len(params)):
            if params[idx][:2] == "-b":
                startdate = parser.parse(params[idx][3:])
            if params[idx][:2] == "-e":
                enddate = parser.parse(params[idx][3:])
            if params[idx][:2] == "-t":
                tickers = params[idx][3:].split("+")
    go(startdate, enddate, tickers)
