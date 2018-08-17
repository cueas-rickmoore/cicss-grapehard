
import os, sys
import datetime

from atmosci.seasonal.factory import BasicSeasonalProjectFactory
from atmosci.utils.config import ConfigObject

from grapehard.grid import GrapeHardinessFileReader
from grapehard.grid import GrapeHardinessFileManager
from grapehard.grid import GrapeTemperatureFileReader
from grapehard.grid import GrapeTemperatureFileManager

"""
DIRECTORY AND FILE PATHS

ROOTDIR = /Volumes/Transport/data/app_data or /Volumes/data/App_data

SOURCE DIRECTORIES & FILES
--------------------------
CHILL DIR = frost/grid/?YEAR?/?CROP?/chill
CHILL FILE = ?YEAR?-Frost-Apple-Chill.h5

FROST DIR = frost/grid/?YEAR?/?CROP?/?VARIETY?
FROST FILE = ?YEAR?-Frost-?CROP?-?VARIETY?.h5

FROST TEMPS = frost/grid/?YEAR?/temp/?YEAR?_temperature.h5

FORECAST = shared/forecast/ndfd/?YYYYMMDD?/001-003-maxt.grib
                                           001-003-mint.grib
                                           004-007-maxt.grib
                                           004-007-mint.grib

ACIS TEMPS = shared/grid/?REGION?/?SOURCE?/temps/?YEAR?-?SOURCE?-NE-Daily.h5
                              /acis_hires/          -ACIS-HiRes-


TOOL DIRECTORIES & FILES
------------------------
WORKING COPY DIR = 

GRAPE TOOL DIR = grapehard/?REGION?/?SOURCE?/?VARIETY?/?DATATYPE?
GRAPE TOOL FILE = ?YEAR?-Grape-?VARIETY?-Hardiness.h5
GRAPE TOOL TEMP = grapehard/?REGION?/?SOURCE?/temp/?YEAR?_temperature.h5
"""

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

from grapehard.config import CONFIG


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class GrapeHardinessFactoryMethods:

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def appDateFormat(self, date):
        return date.strftime('%Y-%m-%d')

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def fileAccessorClass(self, klass, access_type):
        return self.AccessClasses[klass][access_type]
    getFileAccessorClass = fileAccessorClass

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def filenameTemplate(self, filetype, default=None):
        return self.config.filenames.get(filetype, default)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def gridFileManager(self, filepath, filetype, target_year=None, 
                              variety=None, mode='r', **kwargs):
        Class = self.fileAccessorClass(filetype, 'manage')
        if filetype == 'tempext': return Class(filepath, mode=mode)
        else: return Class(filepath, target_year, variety, mode=mode, **kwargs)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def gridFileReader(self, filepath, filetype, target_year=None,
                             variety=None):
        Class = self.fileAccessorClass(filetype, 'read')
        if filetype == 'tempext': return Class(filepath)
        else: return Class(filepath, target_year, variety)
 
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def projectRootDir(self, root='project'):
        root_dir = self.config.dirpaths.get(root, None)
        if root_dir is None:
            root = self.project.get('root', None)
            if root is None: return self.workingDir()
            root_dir = os.path.join(self.workingDir(),
                                    self.normalizeDirpath(root))
        if not os.path.exists(root_dir): os.makedirs(root_dir)
        return root_dir

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def seasonDates(self, year_or_date):
        if isinstance(year_or_date, (datetime.date, datetime.datetime)):
            year = self.targetYear(date)
        else: year = year_or_date
        season = (year, datetime.date(year-1, *self.project.start_day), 
                        datetime.date(year, *self.project.end_day))
        return season
    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def setDirpaths(self, dirpaths):
        if isinstance(dirpaths, basestring):
            # test whether dirpaths is actually a test/production mode name
            if dirpaths in self.config.modes:
                attrs = self.config.modes[dirpaths].dirpaths.attrs
                self.config.dirpaths.update(attrs)
            else:
                raise ValueError, "'%s' is not a valid mode key" % dirpaths
        else: self.config.dirpaths.update(dirpaths.attrs)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def sourceDirpath(self, source, region, root='project'):
        return os.path.join(self.projectRootDir(root),
                            self.regionToDirpath(region),
                            self.sourceToDirpath(source))
        self._verifyDirpath(dirpath)
        return dirpath

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def targetYear(self, date):
        season_start = datetime.date(date.year, *self.project.start_day)
        if date >= season_start:
            target_year = date.year+1
        else: 
            season_start = datetime.date(date.year-1, *self.project.start_day)
            target_year = date.year
        season_end = datetime.date(target_year, *self.project.end_day)
        if date <= season_end: return target_year
        else: return None

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def templateArgs(self, target_year, source=None, region=None,
                           variety=None):
        template_args =  { 'year' : target_year, }
        if source is not None:
             template_args['source'] = self.sourceToFilepath(source)
        if region is not None:
            template_args['region'] = self.regionToFilepath(region)
        if variety is not None:
            template_args['variety'] = self.varietyToFilepath(variety)
        return template_args

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #  temperature file names
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def tempextFilename(self, target_year, source, region):
        template = self.filenameTemplate('tempext')
        template_args = self.templateArgs(target_year, source, region) 
        return template % template_args

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def tempextFilepath(self, target_year, source, region, root='project'):
        dirpath = self.sourceDirpath(source, region, root)
        dirpath = os.path.join(dirpath, 'temps')
        self._verifyDirpath(dirpath)
        filename = self.tempextFilename(target_year, source, region) 
        return os.path.join(dirpath, filename)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #  tool file access
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def toolFilepath(self, filetype, target_year, source, region, 
                            variety=None, root='tooldata'):
        if filetype == 'tempext':
            return self.tempextFilepath(target_year, source, region, root)
        else:
            return self.varietyFilepath(filetype, target_year, variety, source,
                                        region, root)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def toolFileManager(self, filetype, target_year, source, region,
                               variety=None, root='tooldata', mode='r'):
        path = self.toolFilepath(filetype, target_year, source, region,
                                 variety, root)
        return self.gridFileManager(path, 'tool', target_year, variety, mode)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def toolFileReader(self, filetype, target_year, source, region,
                             variety=None, root='tooldata'):
        path = self.toolFilepath(filetype, target_year, source, region,
                                     variety, root)
        return self.gridFileReader(path, 'tool', target_year, variety)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #  variety file access
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def varietyConfig(self, variety):
        if isinstance(variety, ConfigObject): return variety
        elif isinstance(variety, basestring):
            return self.tool.varieties.get(variety, None)
        else:
            errmsg = 'Unsupported type for "variety" argument : %s'
            return TypeError, errmsg % str(type(variety))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def varietyName(self, variety):
        if isinstance(variety, ConfigObject):
            tag = variety.get('tag', None)
            if tag is not None: return tag
            else: return variety.name
        elif isinstance(variety, basestring): return variety
        elif isinstance(variety, dict): return variety['name']
        else:
            raise TypeError, 'Unsupported type for "variety" argument.'

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def varietyDirpath(self, source, region, variety, target_year=None,
                             root='project'):
        dirpath = self.sourceDirpath(source, region, root)
        if target_year is not None:
            dirpath = os.path.join(dirpath, str(target_year))
        dirpath = os.path.join(dirpath, self.varietyToDirpath(variety))
        self._verifyDirpath(dirpath)
        return dirpath

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def varietyFilename(self, filetype, target_year, variety, source=None,
                              region=None, **kwargs):
        template = self.filenameTemplate(filetype)
        template_args = self.templateArgs(target_year, source, region, variety) 
        template_args.update(dict(kwargs))
        return template % template_args

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def varietyFilepath(self, filetype, target_year, variety, source, region,
                              root='project', **kwargs):
        dirpath = self.varietyDirpath(source, region, variety, root=root)
        filename = \
            self.varietyFilename(filetype, target_year, variety, **kwargs)
        return os.path.join(dirpath, filename)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def varietyToDirpath(self, variety):
        return self.normalizeDirpath(self.varietyName(variety).lower())

    def varietyToFilepath(self, variety):
        return self.normalizeFilepath(self.varietyName(variety))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def _verifyDirpath(self, dirpath):
        if not os.path.exists(dirpath): 
            try:
                os.makedirs(dirpath)
            except Exception as e:
                reason = ' : Issue with filepath "%s"' % dirpath
                info = sys.exc_info()[2]
                raise type(e), type(e)(e.message + reason), info


    # - - - # - - - # - - - # - - - # - - - # - - - # - - - # - - - # - - - #

    def _registerTempAccessClasses(self):
        self._registerAccessManagers('tempext',
                                     GrapeTemperatureFileReader,
                                     GrapeTemperatureFileManager,
                                     GrapeTemperatureFileManager)

    # - - - # - - - # - - - # - - - # - - - # - - - # - - - # - - - # - - - #

    def _registerToolAccessClasses(self):
        self._registerAccessManagers('tool',
                                     GrapeHardinessFileReader,
                                     GrapeHardinessFileManager,
                                     GrapeHardinessFileManager)


    # - - - # - - - # - - - # - - - # - - - # - - - # - - - # - - - # - - - #

    def _postInitConfig_(self, path_mode):
        self.project = self.config.project
        self.setDirpaths(path_mode)
        self.tool = self.config.tool
        self.toolname = self.config.get('toolname', self.tool.name)
        if path_mode == 'build':
            from frost.grape.config import GRAPE
            GRAPE.chill.copy('chill', self.tool)
            GRAPE.dormancy.copy('dormancy', self.tool)
            GRAPE.varieties.copy('varieties', self.tool)
            del GRAPE


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class GrapeHardinessToolFactory(GrapeHardinessFactoryMethods,
                                BasicSeasonalProjectFactory):

    def __init__(self, path_mode='prod'):
        BasicSeasonalProjectFactory.__init__(self, CONFIG)
        self._postInitConfig_(path_mode)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def tempextFileManager(self, target_year, source, region, root='tooldata',
                                 mode='r'):
        path = self.tempextFilepath(target_year, source, region, root)
        return self.gridFileManager(path, 'tempext', target_year, mode=mode)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def tempextFileReader(self, target_year, source, region, root='tooldata'):
        path = self.tempextFilepath(target_year, source, region, root)
        return self.gridFileReader(path, 'tempext', target_year)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def varietyFileManager(self, variety, target_year, source, region,
                                filetype='season', root='tooldata', mode='r'):
        path = self.varietyFilepath(filetype, target_year, variety, source,
                                    region, root)
        return self.gridFileManager(path, 'tool', target_year, variety, mode)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def varietyFileReader(self, variety, target_year, source, region,
                                filetype='season', root='tooldata'):
        path = self.varietyFilepath(filetype, target_year, variety, source,
                                    region, root)
        return self.gridFileReader(path, 'tool', target_year, variety)

    # - - - # - - - # - - - # - - - # - - - # - - - # - - - # - - - # - - - #

    def _registerAccessClasses(self):
        self._registerTempAccessClasses()
        self._registerToolAccessClasses()


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class GrapeHardinessBuildFactory(GrapeHardinessToolFactory):

    def __init__(self, path_mode='build'):
        GrapeHardinessToolFactory.__init__(self, path_mode)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def buildFileManager(self, filetype, target_year, source, region,
                               variety=None, mode='r'):
        if filetype == 'tempext':
            path = self.tempextFilepath(target_year, source, region, 'build')
            return self.gridFileManager(path, 'tempext', mode=mode)
        else:
            path = self.varietyFilepath(filetype, variety, target_year, source,
                                        region, 'build')
            return self.gridFileManager(filepath, filetype, target_year,
                                        variety, mode, chill=self.tool.chill,
                                        dormancy=self.tool.dormancy)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def buildFileReader(self, filetype, target_year, source, region,
                              variety=None):
        if filetype == 'tempext':
            path = self.tempextFilepath(target_year, source, region, 'build')
            return self.gridFileReader(path, 'tempext', target_year)
        else:
            path = self.varietyFilepath(filetype, variety, target_year, source,
                                        region, 'build')
            return self.gridFileReader(path, filetype, target_year, variety)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def tempextFileBuilder(self, target_year, source, region, mode='a',
                                 **kwargs):
        path = self.tempextFilepath(target_year, source, region, 'build')
        Class = self.fileAccessorClass('tempext', 'build')
        return Class(path, 'tempext', target_year, source, region, **kwargs)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def varietyFileBuilder(self, variety, target_year, source, region,
                                 filetype='season', mode='a', **kwargs):
        path = self.varietyFilepath(filetype, variety, target_year, source,
                                    region, 'build')
        Class = self.fileAccessorClass('tool', 'build')
        return Class(path, filetype, target_year, variety, source, region, 
                     self.tool.dormancy, self.tool.chill, **kwargs)

    # - - - # - - - # - - - # - - - # - - - # - - - # - - - # - - - # - - - #

    def _registerAccessClasses(self):
        from grapehard.grid import GrapeHardinessFileBuilder
        self._registerToolAccessClasses()
        self._registerAccessManager('tool', 'build', GrapeHardinessFileBuilder)

        from grapehard.grid import GrapeTemperatureFileBuilder
        self._registerTempAccessClasses()
        self._registerAccessManager('tempext', 'build',
                                    GrapeTemperatureFileBuilder)

        self._registerAccessManagers('build',
                                     GrapeHardinessFileReader,
                                     GrapeHardinessFileManager,
                                     GrapeHardinessFileManager)
