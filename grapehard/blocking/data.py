
import datetime
import json

from tornado.httputil import HTTPHeaders, ResponseStartLine

from atmosci.utils.timeutils import asDatetimeDate, elapsedTime

from grapehard.blocking.handler import GrapeHardinessBlockingRequestHandler
from grapehard.blocking.handler import GrapeHardinessVarietyRequestHandler

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

TOOL_DATA_HANDLERS =  { }

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class GrapeHardinessTempextHandler(GrapeHardinessBlockingRequestHandler):

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def __call__(self, request):
        start_response = datetime.datetime.now()

        # decode request variables into a dictionary
        request_dict = self.requestAsDict(request)

        # extract location coordinates
        location = self.extractLocationParameters(request_dict)
        lat, lon = location['coords']

        target_year = request_dict.get('season', None)

        # get the configured season limits
        dates = self.extractSeasonDates(request_dict, target_year)
        season_start = asDatetimeDate(dates['season_start'])
        season_end = asDatetimeDate(dates['season_end'])
        target_year = dates['season']
        del dates['season']
        # initialize response string with season dates
        response = \
            '{"tempexts":{%s,"data":{' % self.tightJsonString(dates)[1:-1]

        reader = \
            self.tempextFileReader(target_year, self.source, self.region)
        if self.mode in ('dev', 'test'):
            print 'tempexts file :', reader.filepath
        # add recent averages
        data = \
        reader.getSliceAtNode('mint', season_start, season_end, lon, lat)
        response = \
            '%s"mint":%s' % (response, self.serializeData(data, '%.1f'))

        # add climate normal averages
        data = \
        reader.getSliceAtNode('maxt', season_start, season_end, lon, lat)
        response = \
            '%s,"maxt":%s' % (response, self.serializeData(data, '%.1f'))

        reader.close()
        del data
        if self.mode in ('dev','test'):
            print 'tempexts data retrieved in',elapsedTime(start_response,True)

        self.respondWithJSON(request, '%s}}}' % response)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

TOOL_DATA_HANDLERS['tempexts'] = GrapeHardinessTempextHandler
#TOOL_DATA_HANDLERS['/tempexts'] = GrapeHardinessTempextHandler


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class GrapeHardinessTempDataHandler(GrapeHardinessVarietyRequestHandler):

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def __call__(self, request):
        start_response = datetime.datetime.now()

        # decode request variables into a dictionary
        request_dict = self.requestAsDict(request)

        varieties = self.extractVarietyParameters(request_dict)
        variety = varieties['variety']

        # extract location coordinates
        location = self.extractLocationParameters(request_dict)
        if 'coords' in location:
            lat, lon = location['coords']
        else:
            lat = location['lat']
            lon = location['lon']

        # target_year
        target_year = request_dict.get('season', None)
        # get the configured season limits
        dates = self.extractSeasonDates(request_dict, target_year)
        target_year = dates['season']

        # create a variety file reader
        reader =  self.varietyFileReader(variety, target_year, self.source,
                                         self.region, 'season')
        if self.mode in ('dev','test'):
            print 'hardtemp data file :', reader.filepath
        # path to the hardiness temp dataset
        dataset_path = 'hardtemp'

        # capture the significant dates for the dataset
        if 'dates' in self.mode_config \
        and target_year == self.mode_config.season:
            dates.update(self.mode_config.dates.attrs)
        else: dates.update(reader.significantDates(dataset_path))
        # temporarily free up the file
        reader.close()

        season_end = dates['season_end']
        end_date = asDatetimeDate(season_end)
        start_date = asDatetimeDate(dates['season_start'])
        if 'fcast_start' in dates:
            fcast_start = asDatetimeDate(dates['fcast_start'])
            if fcast_start > end_date: del dates['fcast_start']
        if 'fcast_end' in dates:
            fcast_end = asDatetimeDate(dates['fcast_end'])
            if fcast_end > end_date:
                if 'fcast_start' in dates: dates['fcast_end'] = season_end
                else: del dates['fcast_end']
        last_obs = asDatetimeDate(dates['last_obs'])
        if last_obs > end_date: dates['last_obs'] = season_end
        last_valid = asDatetimeDate(dates['last_valid'])
        if last_valid > end_date:
            dates['last_valid'] = season_end
            last_valid = asDatetimeDate(season_end)
        #dates = self.tightJsonString(dates)

        # get the accumulated GDD for Y axis of data plots
        reader.open()
        data = \
            reader.dataAtNode(dataset_path, lon, lat, start_date, last_valid)
        reader.close()
        if self.mode in ('dev','test'):
            print 'hardtemp data retrieved in ', elapsedTime(start_response,True)

        # initialize the response
        response_dict = { "hardtemp": { "variety":variety, "location":location,
                                      "dates":dates, "data":"data_array" }}
        response = self.tightJsonString(response_dict).replace('\\"','"')
        response = \
            response.replace('"data_array"', self.serializeData(data, '%.1f'))

        # send the response
        self.respondWithJSON(request, response)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def respondWithJSON(self, request, response_json):
        response = "HTTP/1.1 200 OK"
        headers = { "Content-Type": "application/json",
                    "Content-Length": "%d" % len(response_json) }
        if "Origin" in request.headers:
            origin = request.headers["Origin"]
            headers["Access-Control-Allow-Origin"] = origin
        request.connection.write_headers(
                           ResponseStartLine(request.version, 200, 'OK'),
                           HTTPHeaders(**headers))
        request.connection.write(response_json)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

TOOL_DATA_HANDLERS['hardtemp'] = GrapeHardinessTempDataHandler
#TOOL_DATA_HANDLERS['/hardtemp'] = GrapeHardinessTempDataHandler


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class GrapeHardinessSeasonDaysHandler(GrapeHardinessBlockingRequestHandler):

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def __call__(self, request):
        # decode request variables into a dictionary
        request_dict = self.requestAsDict(request)
        # target_year
        target_year = request_dict.get('season', None)
        # get the configured season limits
        dates = self.extractSeasonDates(request_dict, target_year)
        season_start = asDatetimeDate(dates['season_start'])
        season_end = asDatetimeDate(dates['season_end'])
        # create an array of days for X axis of data plots
        response_json = \
            '{"days":%s}' % self.serializeDates(season_start, season_end)

        # send the respnse
        self.respondWithJSON(request, response_json)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

TOOL_DATA_HANDLERS['daysInSeason'] = GrapeHardinessSeasonDaysHandler
#TOOL_DATA_HANDLERS['/daysInSeason'] = GrapeHardinessSeasonDaysHandler

