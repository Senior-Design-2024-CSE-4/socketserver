import decimal
import random

def gen_rand_coor(lat, lon, num_rows):
    coordinates = []
    for i in range(num_rows):
        dec_lat = random.random() / 100
        dec_lon = random.random() / 100
        coordinates.append((lon + dec_lon, lat + dec_lat))

    return coordinates

latitude = float(decimal.Decimal(random.randrange(-10000, 10000)) / 100)
longitude = float(decimal.Decimal(random.randrange(-10000, 10000)) / 100)

numrows = random.randrange(1, 10)

coordinates = gen_rand_coor(latitude, longitude, numrows)
for coor in coordinates:
    print(f'longitude: {coor[0]:.6f}, latitude: {coor[1]:.6f}')