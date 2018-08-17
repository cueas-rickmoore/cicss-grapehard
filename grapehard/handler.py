
import datetime

from grapehard.season import GrapeHardinessSeasonDateMethods

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class GrapeHardinessRequestHandlerMethods(GrapeHardinessSeasonDateMethods):

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def appDateFormat(self, date):
        return date.strftime('%Y-%m-%d')

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def dayToSeasonDate(self, season, day):
        if day[0] <= self.tool.season_end_day[0]:
            return datetime.date(season, *day)
        if day[0] >= self.tool.season_end_day[0]:
            return datetime.date(season-1, *day)
        return None

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def defaultStartDate(self, target_year):
        return datetime.date(target_year-1, *self.tool.season_start_day)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def extractDataAccessParameters(self, request_dict):
        return self.extractLocationParameters(request_dict)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def setToolConfig(self, server_config):
        # create attribute for reference to tool config
        server_tool = server_config.get('tool', None)
        if server_tool is not None:
            self.tool.update(server_tool)
        self.toolname = self.server_config.get('toolname', self.toolname)

        key = self.tool.get('data_region_key', self.project.region)
        self.region = self.regionConfig(key)
        key = self.tool.get('data_source_key', self.project.source)
        self.source = self.sourceConfig(key)
