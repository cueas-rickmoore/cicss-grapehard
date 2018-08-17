#!/usr/bin/env python

import os
import datetime
ONE_DAY = datetime.timedelta(days=1)
import warnings

import numpy as N

from atmosci.utils.timeutils import elapsedTime

from grapehard.factory import GrapeHardinessBuildFactory

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

from optparse import OptionParser
parser = OptionParser()

parser.add_option('-r', action='store', dest='region', default=None)
parser.add_option('-s', action='store', dest='source', default=None)

parser.add_option('-v', action='store_true', dest='verbose', default=False)
parser.add_option('-z', action='store_true', dest='debug', default=False)

options, args = parser.parse_args()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

build_start = datetime.datetime.now()

debug = options.debug
verbose = options.verbose

today = datetime.date.today()

factory = GrapeHardinessBuildFactory()
project = factory.projectConfig()

if len(args) > 0: target_year = int(args[0])
else:
    target_year = factory.targetYear(today)
    if target_year is None: exit() # die gracefully during daily cron builds

region_key = options.region
if region_key is None: region_key = project.region
if len(region_key) == 2: region_key = region_key.upper()
region = factory.regionConfig(region_key)

source_key = options.source
if source_key is None: source_key = project.source
source = factory.sourceConfig(source_key)


# filter annoying numpy warnings
warnings.filterwarnings('ignore',"All-NaN axis encountered")
warnings.filterwarnings('ignore',"All-NaN slice encountered")
warnings.filterwarnings('ignore',"invalid value encountered in greater")
warnings.filterwarnings('ignore',"invalid value encountered in less")
warnings.filterwarnings('ignore',"Mean of empty slice")
# MUST ALSO TURN OFF WARNING FILTERS AT END OF SCRIPT !!!!!

temps = factory.buildFileReader('tempext', target_year, source, region)
date_attrs = temps.dateAttributes('reported.maxt')
temps.close()
last_obs = datetime.date(date_attrs['last_obs_date'])
last_valid = datetime.date(date_attrs['last_valid_date'])

# crops.grape.varieties.build has list of varieties currently being built
for variety_key in project.varieties:
    variety = factory.varietyConfig(variety)

    # get a reader for the variety file
    manager = \
        factory.buildFileManager('build', target_year, source, region, variety)
    var_last_obs = manager.dateAttribute('hardiness.temp', 'last_obs_date')
    prev_date = min(last_obs, var_last_obs)
    manager.close()
    start_date = prev_date + ONE_DAY

    # cannot assume all variety files are caught up to the same date
    # so, get maxt/mint again for each variety
    temps.open()
    maxt = temps.timeSlice('reported.maxt', start_date, last_valid, units='C')
    mint = temps.timeSlice('reported.mint', start_date, last_valid, units='C')
    temps.close()
    # need to use average temp in all GDD and chill calculations
    avgt = mint + ((maxt - mint) / 2.)
    del maxt, mint

    # estimate common chill
    daily = manager.estimateChill(avgt, manager.common_chill_threshold)
    # current accumulated common chill requires previous day's common chill
    dataset_name = 'chill.common.daily'
    manager.open('a')
    manager.updateDataset(dataset_name, daily, accumulated, start_date)
    manager.setDatasetAttributes(dataset_name, **date_attrs)
    manager.close()

    dataset_name = 'chill.common.accumulated'
    manager.open('a')
    prev_accum = manager.dataForTime(dataset_name, prev_date)
    accumulated = manager.accumulateChill(daily, prev_accum)
    manager.updateDataset(dataset_name, accumulated, start_date)
    manager.setDatasetAttributes(dataset_name, **date_attrs)
    manager.close()

    # dormancy stage from common accumulated chill
    stage = manager.dormancyStageFromChill(accumulated)
    dataset_name = 'dormancy.stage'
    manager.open('a')
    manager.updateDataset(dataset_name, stage, start_date)
    manager.setDatasetAttributes(dataset_name, **date_attrs)
    manager.close()

    # dormancy-based chill from avgt and dormancy stage
    daily = manager.dormancyBasedChill(avgt, dormancy_stage)
    dataset_name = 'chill.dormancy.daily'
    manager.open('a')
    manager.updateDataset(dataset_name, daily, start_date)
    manager.setDatasetAttributes(dataset_name, **date_attrs)
    manager.close()

    # accumulated dormancy chill
    dataset_name = 'chill.dormancy.accumulated'
    manager.open('a')
    prev_accum = manager.dataForTime(dataset_name, prev_date)
    accumulated = manager.accumulateChill(daily, prev_accum)
    manager.updateDataset(dataset_name, accumulated, start_date)
    manager.setDatasetAttributes(dataset_name, **date_attrs)
    manager.close()

    # dormancy-based GDD from avgt and dormancy stage
    dataset_name = 'gdd.daily'
    daily = manager.dormancyBasedGDD(avgt, dormancy_stage)
    manager.open('a')
    manager.updateDataset(datast_name, daily, start_date)
    manager.setDatasetAttributes(dataset_name, **date_attrs)
    manager.close()
    del avgt

    dataset_name = 'gdd.accumulated'
    manager.open('a')
    prev_accum = manager.dataForTime(dataset_name, prev_date)
    accumulated = \
        manager.accumulateGDD(daily, dormancy_stage, prev_accum)
    manager.updateDataset(datast_name, accumulated, start_date)
    manager.setDatasetAttributes(dataset_name, **date_attrs)
    manager.close()

    # calculates the hardiness temps
    manager.open('r')
    stage = manager.timeSlice('dormancy.stage', prev_date, last_valid)
    daily_chill = \
        manager.timeSlice('chill.dormancy.daily', prev_date, last_valid)
    accum_chill = \
        manager.timeSlice('chill.dormancy.accumulated', prev_date, last_valid)
    daily_gdd = manager.timeSlice('gdd.daily', prev_date, last_valid)
    prev_hardiness = manager.dataForTime('hardiness.temp', prev_date)
    estimates = manager.estimateHardiness(stage, daily_chill, accum_chill,
                                          daily_gdd, prev_hardiness)
    manager.close()
    # save the datasets
    hardiness, acclimation, deacclimation = estimates

    manager.open('r')
    dataset_name = 'hardiness.temp'
    manager.updateDataset(datast_name, hardiness, start_date)
    manager.setDatasetAttributes(dataset_name, **date_attrs)
    manager.close()

    manager.open('r')
    dataset_name = 'acclimation.factor'
    manager.updateDataset(datast_name, acclimation, start_date)
    manager.setDatasetAttributes(dataset_name, **date_attrs)
    manager.close()

    manager.open('r')
    dataset_name = 'deacclimation.factor'
    manager.updateDataset(datast_name, deacclimation, start_date)
    manager.setDatasetAttributes(dataset_name, **date_attrs)
    manager.close()

# turn annoying numpy warnings back on
warnings.resetwarnings()

