"""
Shapefile sources
    China provinces:
        https://www.gadm.org/
    Rivers (1820):
        https://geodata.lib.berkeley.edu/?utf8=%E2%9C%93&f%5Bdc_format_s%5D%5B%5D=Shapefile&f%5Bdct_spatial_sm%5D%5B%5D=China&search_field=all_fields&q=river
    Rivers:
        http://worldmap.harvard.edu/data/geonode:River_basin_num2
    Dataverse:
        https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/T27RQO
    Cities/Hydrography/Water Bodies:
        https://tapiquen-sig.jimdofree.com/english-version/free-downloads/china/

"""

import os
os.environ['PROJ_LIB'] = r'D:\Programs\Anaconda3\Library\share\basemap'

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from matplotlib.path import Path
from matplotlib.collections import LineCollection, PathCollection
from matplotlib.font_manager import FontProperties
import matplotlib.patheffects as PathEffects
from matplotlib import cm
import shapefile as sp

plt.style.use('default')

zorders = {
    'ocean': -1,
    'continent': 0,
    'countries': 10,
    'provinces': 20,
    'rivers': 30,
    'par/med': 40,
    'cities': 50,
    'text': 100
}
provinces_file = 'data/china/gadm36_CHN_1'
colors_provinces = [
    'peachpuff', 'palegreen', 'plum', 'olivedrab', 'salmon'
]
provinces_info = {
    'Anhui':            ((0, 31.0), 2),
    'Beijing':          ((0, 40.5), -1),
    'Chongqing':        ((0, 29.0), -1),
    'Fujian':           ((118.0, 26.0), 2),
    'Gansu':            (( 96.5, 40.5), 3),
    'Guangdong':        ((114.2, 24.2), 3),
    'Guangxi':          ((110.0, 24.5), 1),
    'Guizhou':          ((107.0, 26.0), 3),
    'Hainan':           ((0, 19), 1),
    'Hebei':            ((116.5, 41.4), 2),
    'Heilongjiang':     ((128.0, 47.0), 1),
    'Henan':            ((0, 33.5), 1),
    'Hubei':            ((0, 0), 0),
    'Hunan':            ((0, 0), 2),
    'Jiangsu':          ((122.0, 32.7), 1),
    'Jiangxi':          ((115.5, 27.0), 1),
    'Jilin':            ((127.0, 42.8), 2),
    'Liaoning':         ((122.4, 41.1), 1),
    'Nei Mongol':       ((118.0, 44.0), 0),
    'Ningxia Hui':      ((0, 0), 1),
    'Qinghai':          (( 95.0, 36.0), 2),
    'Shaanxi':          ((109.0, 36.0), 2),
    'Shandong':         ((120.0, 37.0), 3),
    'Shanghai':         ((123.7, 31.0), -1),
    'Shanxi':           ((0, 39.5), 3),
    'Sichuan':          ((102.0, 29.5), 0),
    'Tianjin':          ((119.0, 39.0), -1),
    'Xinjiang Uygur':   (( 87.0, 37.0), 0),
    'Xizang':           (( 85.0, 32.0), 1),
    'Yunnan':           ((102.0, 24.0), 2),
    'Zhejiang':         ((0, 28.5), 3),
}
rivers_file = 'data/china_basins/River_basin_num2'
rivers_info = np.array([
    ['Amur\nHeiLong', '黑龙江',                     (132.0, 49.5), 1],
    ['Songhua', '松花江',                           (125.0, 45.0), 2],
    ['Liao', '辽河',                                (124.5, 43.0), 2],
    ['Wei', '卫河',                                 (113.5, 36.0), 2],
    ['Yellow\nHuang He', '黄河',                    (105.0, 42.0), 1],
    ['Huai', '淮河',                                (113.0, 32.5), 2],
    ['Yangtze', '长江',                             ( 89.0, 34.0), 1],
    ['Han', '汉江',                                 (110.5, 32.5), 2],
    ['Jialing', '嘉陵江',                           (106.5, 32.0), 2],
    ['Min', '岷江',                                 (103.5, 32.0), 2],
    ['Yalong', '雅砻江',                            (100.0, 32.0), 2],
    ['Pearl\nZhu', '珠江',                          (114.0, 21.0), 1],
    ['Red\nYuan', '元江',                           (104.0, 22.0), 2],
    ['Brahmaputra\nYarlung Tsangpo', '雅鲁藏布江',  ( 92.0, 28.0), 2],
    ['Tarim', '塔里木盆地',                         ( 82.0, 40.5), 2],
    ['Irtysh', '额尔齐斯河',                        ( 87.0, 47.0), 2],
    ['Mekong\nLancang', '湄公河',                   (101.0, 21.0), 1],
    ['Salween\nNu', '怒江',                         ( 98.0, 23.0), 2],
    ['Indus\nSênggê Zangbo', '獅泉河',              ( 77.5, 33.5), 2],
    # Luan river (beijing and tianjin)
    # Wei river (yellow basin, west of luoyang, passes by Xi'an)
    # Xiang river (yangtze basin, passes by nanchang)
    # Bei river (pearl basin)
    # Grand canal
], dtype=object)


def extract_polygons_from_shapefile(shp_reader, basemap):
    """
    How to add country data:
    https://www.geophysique.be/2013/02/12/matplotlib-basemap-tutorial-10-shapefiles-unleached-continued/
    """

    shapes = shp_reader.shapes()
    records = shp_reader.records()

    records_lines = []

    for record, shape in zip(records,shapes):
        try:
            lons,lats = zip(*shape.points)
        except ValueError:
            continue
        data = np.array(basemap(lons, lats)).T

        is_point = False
        if len(shape.parts) == 0:   # Point
            segs = data
            is_point = True
        elif len(shape.parts) == 1: # Line or Polygon
            segs = [data,]
        else:                       # Line or Polygon
            segs = []
            for i in range(1,len(shape.parts)):
                index = shape.parts[i-1]
                index2 = shape.parts[i]
                segs.append(data[index:index2])
            segs.append(data[index2:])

        if is_point:
            lines = segs
        else:
            lines = LineCollection(segs,antialiaseds=(1,))
        records_lines.append((record, shape, lines))

    return records_lines


def draw_provinces(ax, basemap):
    china_data_reader = sp.Reader(provinces_file)
    china_data_line_dict = extract_polygons_from_shapefile(china_data_reader, basemap)
    for record, shape, lines in china_data_line_dict:
        reg_name = record['NAME_1']
        # reg_type = record['ENGTYPE_1']

        bbox = shape.bbox
        # center_lon = np.mean(bbox[::2])
        # center_lat = np.mean(bbox[1::2])
        center_lon, center_lat = np.mean(np.reshape(bbox, (2,2)), axis=0)

        (lon, lat), color_code = provinces_info[reg_name]
        facecolor = colors_provinces[color_code]

        if lon == 0:
            lon = center_lon
        if lat == 0:
            lat = center_lat

        if color_code == -1:
            foreground = 'orangered'
        else:
            foreground = 'w'

        lines.set_linewidth(0.)
        lines.set_edgecolors('k')
        lines.set_facecolors(facecolor)
        lines.set_zorder(zorders['provinces'])

        ax.add_collection(lines)


def draw_rivers(ax, basemap):
    rivers_data_reader = sp.Reader(rivers_file)
    rivers_data_line_dict = extract_polygons_from_shapefile(rivers_data_reader, basemap)
    for record, shape, lines in rivers_data_line_dict:
        level_river = record['LEVEL_RIVE']
        river_name = record['NAME']
        river_name = river_name.split('(')[0]

        show_river = (
            (level_river in [1, 2, 3, 9])
            # or (river_name in rivers_info[:, 1])
            or True
        )

        if not show_river:
            continue

        bbox = shape.bbox
        center_lon, center_lat = np.mean(np.reshape(bbox, (2,2)), axis=0)

        # font = FontProperties('SimSun')
        # plt.annotate(record['NAME'], xy=basemap(center_lon, center_lat),
        #              fontproperties=font,
        #              zorder=zorders['text'])

        # (lon, lat), color_code = provinces_info[reg_name]
        # facecolor = colors_provinces[color_code]

        # if lon == 0:
        #     lon = center_lon
        # if lat == 0:
        #     lat = center_lat

        # lines.set_linewidth(3 / level_river)
        lines.set_linewidth(max(3 / level_river, 1))
        colors = [
            'black', 'blue', 'teal',
            'cyan', 'white', 'red',
            'red', 'red', 'red'
        ]
        # lines.set_edgecolors('blue')
        lines.set_edgecolors(colors[level_river-1])
        # lines.set_facecolors('aqua')
        lines.set_zorder(zorders['rivers'])

        ax.add_collection(lines)

    # font = FontProperties('SimSun')
    # for name, chinese, (lon, lat), code in rivers_info:
    #     if code < 0:
    #         continue

    #     txt = plt.annotate(
    #         # f'{name}\n{chinese}',
    #         name,
    #         color='w',
    #         xy=basemap(lon, lat), xycoords='data',
    #         ha='center', va='center',
    #         zorder=zorders['text'],
    #         fontsize=9,
    #         # fontproperties=font
    #     )
    #     txt.set_path_effects([
    #         PathEffects.withStroke(linewidth=3, foreground='blue')
    #     ])


plt.figure(figsize=(10,8))
ax = plt.subplot(111)

# China
# Latitude from 18.24306 to 52.33333
# longitude from 75.98951 to 134.28917
m = Basemap(
    width=5_000_000,
    height=4_250_000,
    projection='lcc',
    resolution='c', # c (crude), l (low), i (intermediate), h (high), f (full)
    # lat_1=45.,
    # lat_2=55,
    lat_0=36.5,
    lon_0=102.
)
# m.drawcoastlines()

# draw a boundary around the map, fill the background.
# this background will end up being the ocean color, since
# the continents will be drawn on top.
m.drawmapboundary(fill_color='lightblue', zorder=zorders['ocean'])

# fill continents, set lake color same as ocean color.
m.fillcontinents(color='lightgrey', lake_color='lightblue', zorder=zorders['continent'])

m.drawcountries(color='w', zorder=zorders['countries'])

# parallels = np.arange(20, 51, 5)
# m.drawparallels(parallels, zorder=zorders['par/med'], labels=[True]*len(parallels))
# meridians = np.arange(75, 136, 5)
# m.drawmeridians(meridians, zorder=zorders['par/med'], labels=[True]*len(meridians))

# draw_provinces(ax, m)
draw_rivers(ax, m)

plt.tight_layout()

plt.savefig('maps/china_rivers.png', dpi=300)
plt.close()
