import os
import datetime
import csv
from matplotlib import pyplot as plt
from dateutil import parser
# ==============================


DATADIR = "data"
OUTDIR = "out"
SMAperiod = 50
# ==============================


class Bar:
    def __init__(self, initstr):
        # dd.MM.YYYY HH:mm:ss;1,13948;1,13956;1,13913;1,13956;17,0
        separated = initstr.replace("\n", "").replace(',', '.').split(';')
        self.date = separated[0].split(' ')[0]
        self.date = self.date[6:] + '.' + self.date[3:5] + '.' + self.date[:2]
        self.time = separated[0].split(' ')[1]
        year, month, day = (int(x) for x in self.date.split('.'))
        self.dayofweek = datetime.date(year, month, day).weekday() # 0 - Monday, 6 - Sunday
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
                short.append(filename)
    return fileslist, short
# ------------------------------


def loadBars(barsfile):
    f = open(barsfile, 'r')
    bars = []
    line = f.readline()
    line = f.readline()
    while line != "":
        bars.append(Bar(line))
        line = f.readline()
    return bars
# ------------------------------


def saveOutFile(file, data):
    outfile = file.replace(DATADIR, OUTDIR)
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


def saveChartToPDF(data, filename, short):
    jpgfile = filename.replace(DATADIR, OUTDIR).replace('csv', 'jpg')
    print("Saving graph to", jpgfile)
    date = [parser.parse(i[0]) for i in data]
    sumHL = [float(i[2]) for i in data]
    K = [float(i[4]) for i in data]
    sma = getSMA(sumHL, SMAperiod)
    Ksma = getSMA(K, SMAperiod)

    fig, ax1 = plt.subplots()

    plt.title(short[:6])

    ax1.plot(date, sumHL, 'b.')
    ax1.plot(date, sma, 'r-')
    ax1.set_ylabel('Sum HL intraday + SMA(' + str(SMAperiod) + ')', color='b')
    ax1.tick_params('y', colors='b')

    ax2 = ax1.twinx()
    ax2.plot(date, Ksma, 'y-')
    ax2.set_ylabel('SumHL / DayHL SMA(' + str(SMAperiod) + ')', color='g')
    ax2.tick_params('y', colors='g')

    fig.tight_layout()

    plt.savefig(jpgfile)
    plt.close()
# ------------------------------


def go():
    # load filenames with data
    files, short = getDatafilesList(DATADIR)
    # for file in files of data:
    for i in range(len(files)):
        # load bardata
        bars = loadBars(files[i])
        print("Working with file", files[i])
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
                outdata.append([bars[idx - 1].date, bars[idx - 1].dayofweek, "{0:.5f}".format(sumHL),
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
        saveOutFile(files[i], outdata)
        saveChartToPDF(outdata[1:], files[i], short[i])


# ==============================
# if "__name__" == "__main__":
go()
