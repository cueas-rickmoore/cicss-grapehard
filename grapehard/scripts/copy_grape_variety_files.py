#! /usr/bin/env python

import os, sys
import datetime

from atmosci.hdf5.dategrid import Hdf5DateGridFileManager

from frost.grape.grid import GrapeVarietyFileReader
from atmosci.seasonal.methods.paths import PathConstructionMethods


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

from frost.grape.config import VARIETIES
from grapehard.config import CONFIG


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class PathConstuctor(PathConstructionMethods):
    def __init__(self):
        self.config = CONFIG.copy()
        self.project = self.config.project

    def varietyToFilepath(self, variety):
        return self.normalizeFilepath(variety.name)

    def varietyToDirpath(self, variety):
        return self.normalizeDirpath(variety.name)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

from optparse import OptionParser
parser = OptionParser()
parser.add_option('-x', action='store_true', dest='replace_existing',
                  default=False)
options, args = parser.parse_args()


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

time_attrs = { 'period':'date', 'scope':'season', 'view':'tyx' }

if len(args) == 1: target_year = int(args[0])
else: target_year = datetime.date.today().year

path_finder = PathConstuctor()
source = CONFIG.sources[CONFIG.project.source]
region = CONFIG.regions[CONFIG.project.region]

forecast_template = CONFIG.filenames.build
template_args = { 'region': path_finder.regionToFilepath(region),
                  'source': path_finder.sourceToFilepath(source),
                  'year': target_year,
                }
root_dir = os.path.join(CONFIG.modes.build.dirpaths.build,
                        path_finder.regionToDirpath(region),
                        path_finder.sourceToDirpath(source))

# crops.grape.varieties.build has list of varieties currently being built
for variety_key in CONFIG.project.varieties:
    # get a frost grape file reader for the variety
    variety = VARIETIES[variety_key]
    reader = GrapeVarietyFileReader(target_year, variety)
    print 'Copying : ', reader.filepath

    # copied file destination
    template_args['variety'] = path_finder.normalizeFilepath(variety.name)
    variety_dirpath = \
        os.path.join(root_dir, path_finder.normalizeDirpath(variety.name))
    print 'variety_dirpath :', variety_dirpath
    variety_filename = forecast_template % template_args
    print 'variety_filename :', variety_filename
    variety_filepath = os.path.join(variety_dirpath, variety_filename)
    print 'variety_filepath :', variety_filepath
    if not(os.path.exists(variety_dirpath)): os.makedirs(variety_dirpath)
    elif os.path.exists(variety_filepath): os.remove(variety_filepath)
    manager = Hdf5DateGridFileManager(variety_filepath, mode='a')
    print 'TO : ', manager.filepath

    manager.setFileAttributes(**dict(reader.getFileAttributes()))
    manager.close()

    for name in reader.group_names:
        attrs = reader.getGroupAttributes(name)
        print "creating '%s' group" % name
        manager.open('a')
        manager.createGroup(name)
        manager.setGroupAttributes(name, **attrs)
        manager.close()

    for name in reader.dataset_names:
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

