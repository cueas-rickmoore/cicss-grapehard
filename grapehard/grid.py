
import datetime

from atmosci.utils.timeutils import DateIterator

from atmosci.seasonal.grid import SeasonalGridFileReader
from atmosci.seasonal.grid import SeasonalGridFileManager
from atmosci.seasonal.grid import SeasonalGridFileBuilder

from frost.grape.model import GrapeModelMethods 

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

from atmosci.seasonal.registry import REGBASE
from grapehard.config import CONFIG

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class BasicGrapehardToolMethods:

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def encodedDays(self, start_date, end_date):
        days = [ date.strftime('%Y-%m-%d')
                 for date in DateIterator(start_date, end_date) ]
        return self.tightJsonString(days)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def significantDates(self, dataset_path, include_season=False):
        dataset_attrs = self.getDatasetAttributes(dataset_path)
        dates = { }
        if include_season:
            dates['season_start'] = dataset_attrs['start_date']
            dates['season_end'] = dataset_attrs['end_date']
        if 'last_obs_date' in dataset_attrs:
            dates['last_obs'] = dataset_attrs['last_obs_date']
        if 'fcast_start_date' in dataset_attrs:
            dates['fcast_start'] = dataset_attrs['fcast_start_date']
            dates['fcast_end'] = dataset_attrs['fcast_end_date']
        elif 'fcast_start' in dataset_attrs:
            dates['fcast_start'] = dataset_attrs['fcast_start']
            dates['fcast_end'] = dataset_attrs['fcast_end']
        dates['last_valid'] = dataset_attrs['last_valid_date']
        return dates

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def tightJsonString(self, value):
        return json.dumps(value, separators=(',', ':'))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def _initGrapeProject_(self, target_year, registry=None):
        self.target_year = target_year

        if registry is not None:
            self.registry = registry.copy('registry', None)
        else:
            self.registry = REGBASE.copy('registry', None)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class BasicGrapeHardinessMethods(BasicGrapehardToolMethods):

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def _initManager_(self, **kwargs):
        chill = kwargs['chill']
        self.chillThresholdString = chill.getThresholdString
        self.common_chill_threshold = chill.common_threshold

        dormancy = kwargs['dormancy']
        self.dormancy_descriptions = dormancy.stages.attributes
        self.dormancy_stages = dormancy.stages.attributes.keys()[1:]
        self.dormancyIndexFromStage = dormancy.indexFromStage
        self.dormancyStageFromIndex = dormancy.stageFromIndex

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def _initVariety_(self, variety):
        print '\n\n_initVariety_\n', variety, '\n\n'
        self.variety = variety
        #self.acclimation_rate = variety.acclimation_rate
        #self.deacclimation_rate = variety.deacclimation_rate
        #self.ecodormancy_threshold = variety.ecodormancy_threshold
        #self.hardiness = variety.hardiness
        #self.stage_thresholds = variety.stage_thresholds
        #self.theta = variety.theta


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class GrapeHardinessFileReader(BasicGrapeHardinessMethods,
                               SeasonalGridFileReader):

    def __init__(self, filepath, target_year, variety):
        self._initGrapeProject_(target_year)
        SeasonalGridFileReader.__init__(self, filepath, REGBASE)
        self._initVariety_(variety)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class GrapeHardinessFileManager(BasicGrapeHardinessMethods, GrapeModelMethods,
                                SeasonalGridFileManager):

    def __init__(self, filepath, target_year, variety, mode='r', **kwargs):
        self._initGrapeProject_(target_year)
        SeasonalGridFileManager.__init__(self, filepath, REGBASE, mode=mode)
        self._initVariety_(variety)
        self._initManager_(**kwargs)

    # - - - # - - - # - - - # - - - # - - - # - - - # - - - # - - - # - - - #

    def _loadManagerAttributes_(self):
        SeasonalGridFileManager._loadManagerAttributes_(self)
        self._loadProjectFileAttributes_()


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class GrapeHardinessFileBuilder(BasicGrapeHardinessMethods, GrapeModelMethods,
                                SeasonalGridFileBuilder):

    def __init__(self, filepath, filetype, target_year, variety, source,
                       region, dormancy, chill, **kwargs):
        #self._initGrapeProject_(target_year)
        SeasonalGridFileBuilder.__init__(self, filepath, REGBASE, CONFIG, 
                                               filetype, source, target_year,
                                               region, **kwargs)
        self._initVariety_(variety)
        self._initManager_(chill=chill, dormancy=dormancy)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def _projectStartDate(self, year, **kwargs):
        start_date = kwargs.get('start_date', None)
        if start_date is None:
            day = self._projectStartDay(**kwargs)
            return datetime.date(year-1, *day)
        else: return start_date


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class GrapeTemperatureFileReader(BasicGrapehardToolMethods,
                                 SeasonalGridFileReader):

    def __init__(self, filepath):
        SeasonalGridFileReader.__init__(self, filepath, REGBASE)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class GrapeTemperatureFileManager(BasicGrapehardToolMethods,
                                  SeasonalGridFileManager):

    def __init__(self, filepath, mode='r'):
        SeasonalGridFileManager.__init__(self, filepath, REGBASE, mode=mode)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class GrapeTemperatureFileBuilder(BasicGrapehardToolMethods,
                                  SeasonalGridFileBuilder):

    def __init__(self, filepath, filetype, target_year, source, region, 
                       **kwargs):
        SeasonalGridFileBuilder.__init__(self, filepath, REGBASE, CONFIG,
                                               filetype, source, target_year, 
                                               region, **kwargs)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def _projectStartDate(self, year, **kwargs):
        start_date = kwargs.get('start_date', None)
        if start_date is None:
            day = self._projectStartDay(**kwargs)
            return datetime.date(year-1, *day)
        else: return start_date

