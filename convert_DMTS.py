import csv

# files = ['teco_DMTS_master_oneDrive_d1_3.csv', 'kanzi_DMTS_master_oneDrive_d1_6.csv']
files = ['teco_DMTS_2019-02-19.csv']

for file in files:
    rows = []
    success_list = dict()
    success_frequency = dict()
    with open(file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        first_row = True
        for row in csv_reader:
            if first_row:
                rows.append(row)
                first_row = False
            else:
                delay_time = int(row[6])
                is_correct = (row[11] == 'True')
                if delay_time in success_list:
                    success_list[delay_time].append(is_correct)
                else:
                    success_list[delay_time] = [is_correct]
                if len(success_list) > 20:
                    success_list[delay_time].pop(0)

                success_frequency[delay_time] = sum(success_list[delay_time]) / len(success_list[delay_time])
                success_frequency[delay_time] = round(success_frequency[delay_time], 3)
                row_corrected = list(row)
                row_corrected[0] = success_frequency[delay_time]
                rows.append(row_corrected)

    out_filename = file + '_corrected'
    out_file = open(out_filename, 'a', newline='')
    with out_file as csvfile:
        w = csv.writer(csvfile, quotechar='"', quoting=csv.QUOTE_MINIMAL, escapechar=None)
        for row in rows:
            w.writerow(row)
