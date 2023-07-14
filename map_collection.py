'''
    Create a map with picture locations.

    Pictures without GPS locations will appear to be on 
    "null island" - a non-existant island at longitude 0, latitude 0
'''
import gmplot
import os
import my_secrets
import webbrowser
  
# GoogleMapPlotter return Map object
# Pass the center latitude and
# center longitude
def plot_images(table):
    apikey = my_secrets.apikey # (your API key here)

    lat_lon_lst = []
    weights = []
    lat = 0
    lon = 0 
    cnt = 0
    for row in table:
        if len(row['img_lon'].strip()) > 0:
            lat_lon = (float(row['img_lat']),float(row['img_lon']))
            # lat_lon = get_gps(fn)
            lat += lat_lon[0]
            lon += lat_lon[1]
            cnt += 1
            try:
                idx = lat_lon_lst.index(lat_lon)
                weights[idx] = weights[idx] + 1
            except ValueError:
                lat_lon_lst.append(lat_lon)
                weights.append(1)
            
    # print(lat_lon_lst,weights)
    
    if cnt > 0:
        lat = lat / cnt
        lon = lon / cnt

        gmap1 = gmplot.GoogleMapPlotter(lat,lon,13,apikey=apikey)

        pts = zip(*lat_lon_lst)

        gmap1.heatmap(
            *pts,
            radius=40,
            weights=weights,
            # gradient=[(0, 0, 255, 0), (0, 255, 0, 0.9), (255, 0, 0, 1)]
        )

        # Pass the absolute path
        map_fn = os.getcwd() + "/" + "temp_map.html"
        gmap1.draw(map_fn)

        webbrowser.open_new_tab(map_fn)
    else:
        print("no coordinates found")
