
import datetime

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class GrapeHardinessSeasonDateMethods:

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def defaultDOI(self, target_year):
        doi = self.tool.default_doi
        if doi[0] > self.tool.season_end_day[0]:
            return datetime.date(target_year-1, *doi)
        return datetime.date(target_year, *doi)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def formatSeasonDescription(self, season):
        year = int(season)
        template = self.tool.season_description
        return template % {'start_year': year-1, 'end_year':year}

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def seasonEndDate(self, target_year):
        return datetime.date(target_year, *self.tool.season_end_day)

    def seasonStartDate(self, target_year):
        start_day = self.tool.season_start_day
        if start_day[0] > self.tool.season_end_day[0]:
            return datetime.date(target_year-1, *start_day)
        return datetime.date(target_year, *start_day)

