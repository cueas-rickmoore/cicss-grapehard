
import os

import numpy as N

from atmosci.utils.config import ConfigObject, ConfigMap

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

SERVER_DIRPATH = os.path.split(os.path.abspath(__file__))[0]
PKG_DIRPATH = SERVER_DIRPATH[:SERVER_DIRPATH.rfind(os.sep)]
RESOURCE_PATH = os.path.join(SERVER_DIRPATH, 'resources')

PROJECT_END_DAY = (6,30)
PROJECT_START_DAY = (9,15)

SEASON_END_DAY = (6,30)
SEASON_START_DAY = (9,15)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# specialize the ConfigObject slightly
class ToolConfigObject(ConfigObject):

    def getFiletype(self, filetype_key):
        if '.' in filetype_key:
           filetype, other_key = filetype_key.split('.')
           return self[filetype][other_key]
        else: return self.filetypes[filetype_key]


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

CONFIG = ToolConfigObject('config', None)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# standard project, regions, sources, statis and view_map configurations are
# inherited from atmosci.seasonal.config
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
from atmosci.seasonal.config import CFGBASE
CFGBASE.project.copy('project', CONFIG)
CFGBASE.regions.copy('regions', CONFIG)
CFGBASE.sources.copy('sources', CONFIG)
CFGBASE.static.copy('static', CONFIG)
CFGBASE.view_map.copy('view_map', CONFIG)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Grape Hardiness tool datasets
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

CONFIG.newChild('datasets')
# use common seasonal lat/lon dataset configurations
CFGBASE.datasets.lat.copy('lat', CONFIG.datasets)
CFGBASE.datasets.lon.copy('lon', CONFIG.datasets)
del CFGBASE

CONFIG.datasets.compressed = { 'dtype':float,
                               'dtype_packed':float,
                               'end_day':PROJECT_END_DAY,
                               'compression':'gzip',
                               'chunks':('num_days',1,1),
                               'missing_data':N.nan,
                               'missing_packed':N.nan,
                               'period':'date',
                               'scope':'season',
                               'start_day':PROJECT_START_DAY,
                               'view':('time','lat','lon'),
                             }

CONFIG.datasets.compressed.copy('maxt', CONFIG.datasets)
CONFIG.datasets.maxt.description = 'Daily Minimum Temperature'
CONFIG.datasets.maxt.scope = 'season'
CONFIG.datasets.maxt.timespan = 'Season'
CONFIG.datasets.maxt.units = 'F'

CONFIG.datasets.maxt.copy('mint', CONFIG.datasets)
CONFIG.datasets.mint.description = 'Daily Minimum Temperature'

CONFIG.datasets.maxt.copy('hardtemp', CONFIG.datasets)
CONFIG.datasets.hardtemp.description = 'Daily Hardiness Temperature'

# historical record
CONFIG.datasets.hardtemp.copy('normal', CONFIG.datasets)
CONFIG.datasets.normal.path = 'normal'
CONFIG.datasets.normal.scope = 'normal'
CONFIG.datasets.normal.timespan = 'Climatological Normal'
CONFIG.datasets.normal.description = \
    '%(timespan)s - Average Hardiness Tempertature'

CONFIG.datasets.hardtemp.copy('recent', CONFIG.datasets)
CONFIG.datasets.recent.path = 'recent'
CONFIG.datasets.recent.scope = 'recent'
CONFIG.datasets.recent.timespan = 'Recent Record'
CONFIG.datasets.recent.description = \
    '%(timespan)s - Average Hardiness Tempertature'

# forecast temperatures for build
CONFIG.datasets.fcastmaxt = { 'dtype':float, 'dtype_packed':'<i2',
                              'chunks':('num_days','lat','lom'),
                              'compression':'gzip',
                              'end_day':PROJECT_END_DAY,
                              'missing_data':N.nan,
                              'missing_packed':-32768, 
                              'period':'date',
                              'scope':'season',
                              'start_day':PROJECT_START_DAY,
                              'view':('time','lat','lon'),
                            }
CONFIG.datasets.fcastmaxt.description = \
      'Daily Observed/Forecast Maximum Temperature'

CONFIG.datasets.fcastmaxt.copy('fcastmint', CONFIG.datasets) 
CONFIG.datasets.fcastmint.description = \
      'Daily Observed/Forecast Minimum Temperature'

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# paths to Grape Hardiness tool directories
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

CONFIG.dirpaths = { 'package':PKG_DIRPATH,     # Grape Hardiness tool package directory
                    'resources':RESOURCE_PATH, # Grape Hardiness tool resource directory
                    'server':SERVER_DIRPATH,   # Grape Hardiness tool server directory
                  }
# delete the directory path constants
del PKG_DIRPATH, RESOURCE_PATH, SERVER_DIRPATH

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# filename templates
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

CONFIG.filenames = { 'build':'%(year)d-%(variety)s-Hardiness-Forecast.h5',
                     'history':'%(year)d-%(variety)s-Hardiness-History.h5',
                     'season':'%(year)d-%(variety)s-Hardiness-Daily.h5',
                     'tempext':'%(year)d-%(source)s-%(region)s-Daily-Temps.h5',
                   }

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# tool filetypes
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

CONFIG.filetypes = { 'history' : { 'scope':'season', 'period':'date', 
                                   'groups':('por',),
                                   'datasets':('lat','lon','recent','normal'), 
                                   'start_day':PROJECT_START_DAY,
                                   'end_day':PROJECT_END_DAY,
                                   'description':'Historical Freeze Hardiness Data'
                                 },
                     'season' : { 'scope':'season', 'period':'date', 
                                  'datasets':('lat','lon','hardtemp'), 
                                  'start_day':PROJECT_START_DAY,
                                  'end_day':PROJECT_END_DAY,
                                  'description':'Freeze Hardiness for Season'
                                },
                     'tempext' : { 'scope':'season', 'period':'date', 
                                  'datasets':('lat','lon','mint','maxt'), 
                                  'start_day':PROJECT_START_DAY,
                                  'end_day':PROJECT_END_DAY,
                                  'description':'Temperature Extremes for Season'
                                },
                   }

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# history file data groups
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

CONFIG.newChild('groups')
CONFIG.groups.tempexts = { 'path':'temps',
                           'description':'Daily temperature extremes',
                           'datasets':('fcastmaxt','fcastmint')
                         }

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# mode-specific configurations
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

CONFIG.modes = { 'build': { 'dirpaths': {
                 'build'    :'/Volumes/data/app_data/grapehard/build',
                 'frost'    :'/Volumes/data/app_data/frost/grid',
                 'project'  :'/Volumes/data/app_data/grapehard',
                 'shared'   :'/Volumes/data/app_data/shared',
                 'static'   :'/Volumes/data/app_data/shared/grid/static',
                 'tooldata' :'/Volumes/data/app_data/grapehard',
                 'working'  :'/Volumes/data/app_data' } }
               }

CONFIG.modes.prod = {
       'dirpaths': { 'project'  :'/app_data/grapehard',
                     'resources':'/opt/tool_pkg/grapehard/resources',
                     'appdata'  :'/app_data/shared',
                     'static'   :'/app_data/shared/static',
                     'tooldata' :'/app_data/grapehard',
                     'working'  :'/app_data' },
       'server_address': 'http://tools.climatesmartfarming.org',
       'server_port': 20007,
       'server_url': 'http://tools.climatesmartfarming.org',
       'tool_url': 'http://tools.climatesmartfarming.org/grapehard',
       }

CONFIG.modes.dev = {
       'csftool_url': 'http://localhost:8082/csftool',
       'dirpaths': { 
            'build'    :'/Volumes/data/app_data/grapehard/build',
            'project'  :'/app_data/grapehard',
            'resources':'/Volumes/Transport/venvs/grape/tool_pkg/grapehard/dev-resources',
            'shared'   :'/Volumes/Transport/data/app_data/shared',
            'static'   :'/Volumes/Transport/data/app_data/static',
            'tooldata' :'/Volumes/Transport/data/app_data/grapehard',
            'working'  :'/Volumes/Transport/data/app_data' },
       'home': 'grapehard.html',
       'server_address': 'file://localhost',
       'server_port': 8082,
       'server_url': 'http://localhost:8082',
       'tool_url': 'http://localhost:8082/grapehard',
       }

CONFIG.modes.dev.copy('test', CONFIG.modes)
CONFIG.modes.test.update({
       'csftool_url': 'http://cyclone.nrcc.cornell.edu:8082/csftool',
       'home': 'grapehard.html',
       'server_address': 'http://cyclone.nrcc.cornell.edu',
       'server_url': 'http://cyclone.nrcc.cornell.edu:8082',
       'tool_url': 'http://cyclone.nrcc.cornell.edu:8082/grapehard',
       })
CONFIG.modes.test.dirpaths.resources = \
       '/Volumes/Transport/venvs/grape/tool_pkg/grapehard/resources'

CONFIG.modes.dev.copy('wpdev', CONFIG.modes)
CONFIG.modes.wpdev.home = 'wpdev-grapehard.html'

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# overrides to seasonal project config 
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

CONFIG.project.end_day = PROJECT_END_DAY
CONFIG.project.region = 'NE'
CONFIG.project.root = 'grapehard'
CONFIG.project.scopes = { 'normal':(1981,2010),
                          'por':(1981,9999),    # 9999 = year previous to target
                          'recent':(-15,9999) } # -n = number of years previous
CONFIG.project.shared_forecast = True
CONFIG.project.shared_source = True
CONFIG.project.start_day = PROJECT_START_DAY
CONFIG.project.source = 'acis'
CONFIG.project.varieties = ('cab_franc','concord','riesling')

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# config resources & paths to files
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

resource_map = { '/' : ('page', 'file', ('pages','grapehard.html')),
                 #'icons'   : ('icon',  'dir', 'icons'),
                 #'images'  : ('image', 'dir', 'images'),
                 'js'      : ('file',  'dir', 'js'),
                 'pages'   : ('page',  'dir', 'pages'),
                 'style'   : ('file',  'dir', 'style'),
                 'tool.js' : ('tool', 'dir', 'js'),
                 'toolinit.js' : ('tool', 'dir', 'js'),
                 'grapehard.html' : ('page',  'dir', 'pages'),
               }
CONFIG.resource_map = ConfigMap(resource_map)
del resource_map
# resources that require template validation
CONFIG.data_requests = ('daysInSeason', 'history', 'season', 'tempext')
CONFIG.templates = ( '/', '/grapehard.html', '/js/tool.js', '/js/toolinit.js',)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# default server configuration
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

CONFIG.server_address = 'http://cyclone.nrcc.cornell.edu'
CONFIG.server_port = 8082

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#  defaults necessary for tool initialization
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

CONFIG.tool = { 'toolname':'grapehard',     # name forwarding server knows
       'inherit_resources':'csftool',       # key to inherited set or resources
       'data_region_key':'NE',              # region covered by the server
       'data_source_key':'acis',            # source of model data
       'days_in_view':30,                   # default number of days in view
       'default_chart': 'trend',
       'default_doi':[2,25],                # default date of interest
       #        significant freeze event from 2/12 - 2/16/2016
       'default_variety': 'riesling',       # default grape variety
       #        variety most likely to exhibit freeze damage in any season
       'first_year':2016,                   # first season with data
       'season_description':'%(start_year)d-%(end_year)d Growing Season',
       'season_end_day':SEASON_END_DAY,     # last day required by tool
       'season_start_day':SEASON_START_DAY, # first day required by tool
       }

CONFIG.tool.button_labels = \
       '{"season":"Show Entire Season", "trend":"Show Recent Trend"}'
# must be a javascript associative array as a string
CONFIG.tool.chart_labels = \
       '{"season":"Season To Date", "trend":"Recent Trend"}'
       #'{"season":"Season Outlook", "trend":"Recent Trend"}'
# must be a simple javascript array as a string
CONFIG.tool.chart_types = '["season", "trend"]'

# default location for this tool
CONFIG.tool.default_location = 'Zappa'
CONFIG.tool.locations = { 'Amorici': {'lat':42.953968, 'lon':-73.531014,
       'address': '637 Colonel Burch Rd, Valley Falls, NY'},
       'Bully_Hill': {'lat':42.429607, 'lon':-77.209084, 'variety':'cab_franc',
       'address': '8843 Greyton H Taylor Memorial Dr, Hammondsport, NY'},
       'Johnson': {'lat':42.307151, 'lon':-79.606418, 'variety':'concord',
       'address':"Johnson Estate Winery, 8403 West Main St, Westfield, NY"},
       'Six_Mile': {'lat':42.417942, 'lon':-76.454511, 
       'address':'Six Mile Creek Vineyard, 1551 Slaterville Rd, Ithaca, NY' },
       'Stein': {'lat':43.014665, 'lon':-77.933032,
       'address': 'Stein Farm, 8343 Gully Rd, LeRoy, NY'},
       'Zappa': {'lat':45.450908, 'lon':-70.487016,
       'address':"Joe's Garage, MidlONoWhe, Somerset County, ME"},
       }

