# Converter for 1st part of file
import time

f = open(r'C:\Users\mohr\Downloads\tankData.csv', 'r')
w = open(r'C:\Users\mohr\Downloads\newTankData.csv', 'w')

for line in f:
    l = line.split(',')
    if len(l) > 4:
        break

    tstruct = time.strptime(l[0] + l[1], '%d %b %Y %H:%M:%S')
    t = time.mktime(tstruct)
    l.insert(2, str(t))
    w.write(", ".join(l))

w.close()
f.close()