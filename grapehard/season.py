
import datetime

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class GrapeHardinessSeasonDateMethods:

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def currentSeason(self):
        today = datetime.date.today()
        season = today.year
        # check to see if today is between season start and end of year
        start_day = self.tool.get('available_day', self.tool.season_start_day)
        season_start = datetime.date(season, *start_day)
        # today is after season start, season start is in first year of season
        if (today >= season_start): # so max available season is next year
            return season + 1
        # today is before next season starts, last available season has ended
        else: return season

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

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def maxAvailableDate(self, year=None):
        if year is not None:
            max_date = self.seasonEndDate(year)
        else:
            max_date = self.seasonEndDate(self.maxAvailableSeason())
        return min(max_date, datetime.date.today())

    def minAvailableDate(self):
        return self.seasonStartDate(self.minAvailableSeason())

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def maxAvailableSeason(self):
        season = self.tool.get('last_season', None)
        if season is not None: return season
        # not specified in config, make a guess based on current date
        return self.currentSeason()

    def minAvailableSeason(self):
        season = self.tool.get('first_season', None)
        if season is not None: return season
        # not specified in config, make a guess based on current date
        return self.currentSeason()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def seasonEndDate(self, target_year):
        return datetime.date(target_year, *self.tool.season_end_day)

    def seasonStartDate(self, target_year):
        start_day = self.tool.get('available_day', self.tool.season_start_day)
        if start_day[0] > self.tool.season_end_day[0]:
            return datetime.date(target_year-1, *start_day)
        return datetime.date(target_year, *start_day)

