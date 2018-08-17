#! /usr/bin/env python

import os, sys
import datetime
from dateutil.relativedelta import relativedelta
ONE_DAY = relativedelta(days=1)

from atmosci.hdf5.dategrid import Hdf5DateGridFileManager

from frost.functions import tempGridReader
from atmosci.seasonal.factory import SeasonalSourceFileFactory
from atmosci.seasonal.methods.paths import PathConstructionMethods


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

from frost.grape.config import VARIETIES
from grapehard.config import CONFIG


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class PathConstuctor(PathConstructionMethods):
    def __init__(self):
        self.config = CONFIG.copy()
        self.project = self.config.project

def seasonDates(date_or_year):
    end_day = CONFIG.project.end_day
    start_day = CONFIG.project.start_day
    if type(date_or_year) == int:
        year = date_or_year
    else: 
        if date_or_year.month > end_day[0]: year = date_or_year.year + 1
        else: year = date_or_year.year
    season = (year, datetime.date(year-1, *start_day), 
                    datetime.date(year, *end_day))
    return season

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

from optparse import OptionParser
parser = OptionParser()
parser.add_option('-q', action='store_true', dest='exit_guietly',
                  default=False)
options, args = parser.parse_args()


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

exit_guietly = options.exit_guietly

time_attrs = { 'period':'date', 'scope':'season', 'view':'tyx' }

factory = SeasonalSourceFileFactory()
today = datetime.date.today()

if len(args) == 1:
    target_year, season_start, season_end = seasonDates(int(args[0]))
else:
    target_year, season_start, season_end = seasonDates(today)
    if today < season_start or today > season_end:
        # quietly exit when outside season ... useful when in cron
        if exit_quitely: os.exit(0)
        errmsg = "Taday's date is not within season limits. Try passing the"
        errmsg += "%s target year as an argument on the command line."
        raise ValueError, errmsg

path_finder = PathConstuctor()
region = CONFIG.regions[CONFIG.project.region]
source = CONFIG.sources[CONFIG.project.source]

template = CONFIG.filenames.tempext
template_args = { 'region': path_finder.regionToFilepath(region),
                  'source': path_finder.sourceToFilepath(source),
                  'year': target_year,
                }
build_filename =  template % template_args
build_dirpath = os.path.join(CONFIG.modes.build.dirpaths.build,
                             path_finder.regionToDirpath(region),
                             path_finder.sourceToDirpath(source),
                             'temps')
build_filepath = os.path.join(build_dirpath, build_filename)
if not(os.path.exists(build_dirpath)): os.makedirs(build_dirpath)
elif os.path.exists(build_filepath): os.remove(build_filepath)

reader = tempGridReader(target_year)
print 'Copying : ', reader.filepath

manager = Hdf5DateGridFileManager(build_filepath, mode='a')
print 'To : ', manager.filepath

manager.setFileAttributes(**dict(reader.getFileAttributes()))
manager.close()

for name in reader.group_names:
    if name != 'forecast':
        attrs = reader.getGroupAttributes(name)
        print "creating '%s' group" % name
        manager.open('a')
        manager.createGroup(name)
        manager.setGroupAttributes(name, **attrs)
        manager.close()

for name in reader.dataset_names:
    if 'forecast' not in name:
        print "creating '%s' dataset" % name
        dataset = reader.getDataset(name)
        chunks = dataset.chunks
        attrs = dict(dataset.attrs)
        if 'last_valid_date' in attrs:
            attrs['last_obs_date'] = attrs['last_valid_date']
        manager.open('a')
        manager.createDataset(name, dataset, chunks=chunks)
        manager.close()
        manager.open('a')
        manager.setDatasetAttributes(name, **attrs)
        manager.close()
        manager.open('a')
        manager.setDatasetAttributes(name, **time_attrs)
        manager.close()

reader.close()
manager.open('a')
slice_start = \
    manager.dateAttribute('reported.maxt', 'last_valid_date') + ONE_DAY
manager.close()

# add forecast from temperature source file to the season's temperature file
reader = factory.sourceFileReader(source, target_year, region, 'temps')
print 'Temperature extremes file :', reader.filepath

last_obs = reader.dateAttribute('temps.maxt', 'last_obs_date')
if last_obs > season_end: last_obs = season_end
last_valid = reader.dateAttribute('temps.maxt', 'last_valid_date')
if last_valid > season_end: last_valid = season_end

attrs = { 'last_obs_date': last_obs.strftime('%Y-%m-%d'),
          'last_valid_date': last_valid.strftime('%Y-%m-%d'),
        }

fcast_start = reader.dateAttribute('temps.maxt','fcast_start_date',None)
if fcast_start is None:
    print('EXITING : temperature extremes file does not contain a forecast.')
elif fcast_start > season_end:
    print('EXITING : temperature forecast is beyond the end of the season.')
else:
    fcast_end = reader.dateAttribute('temps.maxt', 'fcast_end_date', None)
    if fcast_end > season_end: fcast_end = season_end
    attrs.update( { 'fcast_start_date': fcast_start.strftime('%Y-%m-%d'),
                    'fcast_end_date': fcast_end.strftime('%Y-%m-%d') } )

    print 'adding forecast to build file'
    for extreme in ('maxt','mint'):
        dataset_name = 'reported.%s' % extreme
        data = reader.dateSlice('temps.%s' % extreme, slice_start, fcast_end)
        manager.open('a')
        manager.insertByDate(dataset_name, data, slice_start)
        manager.setDatasetAttributes(dataset_name, **attrs)
        manager.close()

reader.close()

