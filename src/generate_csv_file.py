from pandas import read_csv

data = read_csv("res/finished_map2px.csv", header=None)
data = data.replace(
    {173258: 1, 243192: 1, 128393: 2, 155496: 0, 2684467986: 1, 113426: 3}
)
data.to_csv("src/map_data.csv", index=False, header=False)
