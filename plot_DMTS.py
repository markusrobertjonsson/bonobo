import csv
import matplotlib.pyplot as plt


files = ['teco_DMTS_master_oneDrive_d1_3_corrected.csv', 'kanzi_DMTS_master_oneDrive_d1_6_corrected.csv']

for file in files:
    fig, axs = plt.subplots(1, 1)
    tit = "kanzi" if file.startswith("kanzi") else "teco"
    axs.set_title(tit)
    freq = dict()
    with open(file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        first_row = True
        for row in csv_reader:
            if first_row:
                first_row = False
            else:
                delay_time = int(row[6])
                if delay_time in freq:
                    freq[delay_time].append(float(row[0]))
                else:
                    freq[delay_time] = [float(row[0])]
    for dt in freq:
        axs.plot(freq[dt], label=str(dt))
        plt.legend()
        plt.grid(True)

plt.show()
