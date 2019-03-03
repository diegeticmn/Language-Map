#IMPORT LIBRARY
import urllib.request
import json
import ssl
import pandas as pd
from bokeh.plotting import figure,ColumnDataSource
from bokeh.models import HoverTool,WMTSTileSource,LinearColorMapper,LabelSet
from bokeh.palettes import RdYlBu11 as palette
from bokeh.server.server import Server
from bokeh.application import Application
from bokeh.tile_providers import CARTODBPOSITRON_RETINA
from bokeh.application.handlers.function import FunctionHandler
import numpy as np

ssl._create_default_https_context = ssl._create_unverified_context
opener = urllib.request.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0')]

# COORDINATE CONVERSION FUNCTION
def wgs84_to_web_mercator(df, lon="Lon", lat="Lat"):
    k = 6378137
    df["x"] = df[lon] * (k * np.pi/180.0)
    df["y"] = np.log(np.tan((90 + df[lat]) * np.pi/360.0)) * k
    return df

def plot_country(doc):
    country_source = ColumnDataSource({'Lat':[],'Lon':[],'Country':[],'Native':[], 'Lang':[], 'x':[], 'y':[]})

    country_df = pd.read_csv('countries.csv')
    country_df.columns = ['Lat', 'Lon', 'Country', 'Native', 'Lang']

    wgs84_to_web_mercator(country_df)

    n_roll=len(country_df.index)
    country_source.stream(country_df.to_dict(orient='list'),n_roll)

    x_range,y_range=([687604.14,537676.59], [4808266.66,8448058.87])
    p=figure(x_range=x_range,y_range=y_range,x_axis_type='mercator',y_axis_type='mercator',sizing_mode='scale_width',plot_height=300)
    my_hover=HoverTool()
    color_mapper = LinearColorMapper(palette=palette)
    my_hover.tooltips=[('Country','@Country'),('Native','@Native'),('Language', '@Lang')]
    p.add_tile(CARTODBPOSITRON_RETINA)
    p.circle('x','y',source=country_source,fill_color={'field': 'Native', 'transform': color_mapper},hover_color='yellow',size=10,fill_alpha=0.8,line_width=0.5)
    p.add_tools(my_hover)
    doc.title='Countries'
    doc.add_root(p)


apps = {'/': Application(FunctionHandler(plot_country))}
server = Server(apps, port=0) #define an unused port
server.start()
server.show('/')
from tornado.ioloop import IOLoop
loop = IOLoop.current()
loop.start()
server.stop()
