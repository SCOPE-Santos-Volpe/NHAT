'''We used this file to try to work with the NEMSIS data. It turns out that the NEMSIS data doesn't include lat/lon because those are the identifiable data. It doesn't seem like we're allowed to have the raw lat/lon, only the anonymized version

'''



import glob
import os
import pandas as pd
import time

# df=pd.read_csv(filename,index_col=None, encoding_errors='ignore', low_memory=False)
# df=pd.read_csv('NEMSIS\\2021 ASCII\ComputedElements.txt',sep="~|~",index_col=None)
# base_file_path = 'NEMSIS\\2021 ASCII\ComputedElements.txt'
# update_file_path = 'NEMSIS\\2021 Cleaned\ComputedElements.txt'
# sep = '~|~'

# base_file = open(base_file_path, 'r')
# count = 0

# update_file = open(update_file_path, 'w')

# start_time = time.time()

# # https://www.geeksforgeeks.org/read-a-file-line-by-line-in-python/
# while True:
#     # count += 1
#     # if count % 1000000 == 0:
#     #     print("Lines Cleaned: " + str(count))


#     line = base_file.readline()
#     if not line:
#         break

#     update_file.writelines(line)

# end_time = time.time()

# print("Time Elapsed: " + str(end_time-start_time))

# base_file.close()
# update_file.close()

path='NEMSIS/2021 ASCII/'
newpath='NEMSIS/2021 Heads/'
all_filenames = glob.glob(os.path.join(path, "*.txt"))
print(all_filenames)

for fn in all_filenames:
    file = open(fn,'r')
    newfile = open(os.path.join(newpath, os.path.basename(fn)), "w")
    for i in range(1000):
        line = file.readline()
        newfile.writelines(line)
    file.close()
    newfile.close()