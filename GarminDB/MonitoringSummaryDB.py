#!/usr/bin/env python

#
# copyright Tom Goetz
#

from HealthDB import *


class MonitoringSummaryDB(DB):
    Base = declarative_base()
    db_name = 'garmin_monitoring_summary.db'

    def __init__(self, db_path, debug=False):
        DB.__init__(self, db_path + "/" + MonitoringSummaryDB.db_name)
        MonitoringSummaryDB.Base.metadata.create_all(self.engine)


class Summary(MonitoringSummaryDB.Base, DBObject):
    __tablename__ = 'summary'

    name = Column(String, primary_key=True)
    value = Column(String)

    _relational_mappings = {}
    col_translations = {
        'value' : str,
    }
    min_row_values = 2

    @classmethod
    def find_query(cls, session, values_dict):
        return  session.query(cls).filter(cls.name == values_dict['name'])


class SummaryBase(DBObject):
    hr_avg = Column(Integer)
    hr_min = Column(Integer)
    hr_max = Column(Integer)
    intensity_mins = Column(Integer)
    moderate_activity_mins = Column(Integer)
    vigorous_activity_mins = Column(Integer)
    steps = Column(Integer)
    floors = Column(Integer)

    _relational_mappings = {}
    col_translations = {}
    min_row_values = 1


class MonthsSummary(MonitoringSummaryDB.Base, SummaryBase):
    __tablename__ = 'months_summary'

    first_day = Column(Date, primary_key=True)

    @classmethod
    def find_query(cls, session, values_dict):
        return  session.query(cls).filter(cls.first_day == values_dict['first_day'])


class WeeksSummary(MonitoringSummaryDB.Base, SummaryBase):
    __tablename__ = 'weeks_summary'

    first_day = Column(Date, primary_key=True)

    @classmethod
    def find_query(cls, session, values_dict):
        return  session.query(cls).filter(cls.first_day == values_dict['first_day'])


class DaysSummary(MonitoringSummaryDB.Base, SummaryBase):
    __tablename__ = 'days_summary'

    day = Column(Date, primary_key=True)

    @classmethod
    def find_query(cls, session, values_dict):
        return  session.query(cls).filter(cls.day == values_dict['day'])


