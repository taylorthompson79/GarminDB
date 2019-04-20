#!/usr/bin/env python

#
# copyright Tom Goetz
#

import unittest, os, logging, sys, datetime

import GarminDB
import Fit
from FileProcessor import *


root_logger = logging.getLogger()
handler = logging.FileHandler('unitests.log', 'w')
root_logger.addHandler(handler)
root_logger.setLevel(logging.INFO)

logger = logging.getLogger(__name__)

db_dir = os.environ['DB_DIR']
db_skip = os.environ['DB_SKIP'] == 'True'


@unittest.skipIf(db_skip, 'Skip DB tests')
class TestGarminDb(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db_params_dict = {}
        cls.db_params_dict['db_type'] = 'sqlite'
        cls.db_params_dict['db_path'] = db_dir

    def check_col_stats(self, db, table, col, name, ignore_le_zero, time_col,
        records_bounds, max_bounds, min_bounds, avg_bounds, latest_bounds):
        records = table.row_count(db)
        records_min, records_max = records_bounds
        self.assertGreater(records, records_min)
        self.assertLess(records, records_max)
        logger.info("%s records: %d", name, records)
        if time_col:
            maximum = table.get_time_col_max(db, col)
        else:
            maximum = table.get_col_max(db, col)
        max_min, max_max = max_bounds
        self.assertGreater(maximum, max_min)
        self.assertLess(maximum, max_max)
        logger.info("Max %s: %s", name, str(maximum))
        if time_col:
            minimum = table.get_time_col_min(db, col, None, None, ignore_le_zero)
        else:
            minimum = table.get_col_min(db, col, None, None, ignore_le_zero)
        min_min, min_max = min_bounds
        if time_col:
            self.assertGreaterEqual(minimum, min_min)
        else:
            self.assertGreater(minimum, min_min)
        self.assertLess(minimum, min_max)
        logger.info("Min %s: %s", name, str(minimum))
        if time_col:
            average = table.get_time_col_avg(db, col, None, None, ignore_le_zero)
        else:
            average = table.get_col_avg(db, col, None, None, ignore_le_zero)
        avg_min, avg_max = avg_bounds
        self.assertGreater(average, avg_min)
        self.assertLess(average, avg_max)
        logger.info("Avg %s: %s", name, str(average))
        latest = table.get_col_latest(db, col)
        latest_min, latest_max = latest_bounds
        self.assertGreater(latest, latest_min)
        self.assertLess(latest, latest_max)
        logger.info("Latest %s: %s", name, str(latest))

    def test_garmindb_exists(self):
        garmindb = GarminDB.GarminDB(self.db_params_dict)
        self.assertIsNotNone(garmindb)

    def test_garmindb_tables_exists(self):
        garmindb = GarminDB.GarminDB(self.db_params_dict)
        self.assertGreater(GarminDB.Attributes.row_count(garmindb), 0)
        self.assertGreater(GarminDB.Device.row_count(garmindb), 0)
        self.assertGreater(GarminDB.DeviceInfo.row_count(garmindb), 0)
        self.assertGreater(GarminDB.File.row_count(garmindb), 0)
        self.assertGreater(GarminDB.Weight.row_count(garmindb), 0)
        self.assertGreater(GarminDB.Stress.row_count(garmindb), 0)
        self.assertGreater(GarminDB.Sleep.row_count(garmindb), 0)
        self.assertGreater(GarminDB.SleepEvents.row_count(garmindb), 0)
        self.assertGreater(GarminDB.RestingHeartRate.row_count(garmindb), 0)

    def test_garmindb_tables_bounds(self):
        garmindb = GarminDB.GarminDB(self.db_params_dict)
        self.check_col_stats(
            garmindb, GarminDB.Weight, GarminDB.Weight.weight, 'Weight', False, False,
            (0, 10*365),
            (25, 300),
            (25, 300),
            (25, 300),
            (25, 300)
        )
        self.check_col_stats(
            garmindb, GarminDB.Stress, GarminDB.Stress.stress, 'Stress', True, False,
            (1, 10000000),
            (25, 100),
            (0, 2),
            (0, 100),
            (0, 100)
        )
        self.check_col_stats(
            garmindb, GarminDB.RestingHeartRate, GarminDB.RestingHeartRate.resting_heart_rate, 'RHR', True, False,
            (1, 10000000),
            (30, 100),
            (30, 100),
            (30, 100),
            (30, 100)
        )
        self.check_col_stats(
            garmindb, GarminDB.Sleep, GarminDB.Sleep.total_sleep, 'Sleep', True, True,
            (1, 10000000),
            (datetime.time(8), datetime.time(12)),
            (datetime.time(0), datetime.time(4)),
            (datetime.time(4), datetime.time(10)),
            (datetime.time(2), datetime.time(12))
        )
        self.check_col_stats(
            garmindb, GarminDB.Sleep, GarminDB.Sleep.rem_sleep, 'REM Sleep', True, True,
            (1, 10000000),
            (datetime.time(2), datetime.time(4)),
            (datetime.time(0), datetime.time(2)),
            (datetime.time(1), datetime.time(6)),
            (datetime.time(1), datetime.time(6))
        )


@unittest.skipIf(db_skip, 'Skip DB tests')
class TestActivitiesDb(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db_params_dict = {}
        cls.db_params_dict['db_type'] = 'sqlite'
        cls.db_params_dict['db_path'] = db_dir

    def test_garmin_act_db_tables_exists(self):
        garmin_act_db = GarminDB.ActivitiesDB(self.db_params_dict)
        self.assertGreater(GarminDB.Activities.row_count(garmin_act_db), 0)
        self.assertGreater(GarminDB.ActivityLaps.row_count(garmin_act_db), 0)
        self.assertGreater(GarminDB.ActivityRecords.row_count(garmin_act_db), 0)
        self.assertGreater(GarminDB.RunActivities.row_count(garmin_act_db), 0)
        self.assertGreater(GarminDB.WalkActivities.row_count(garmin_act_db), 0)
        self.assertGreater(GarminDB.PaddleActivities.row_count(garmin_act_db), 0)
        self.assertGreater(GarminDB.CycleActivities.row_count(garmin_act_db), 0)
        self.assertGreater(GarminDB.EllipticalActivities.row_count(garmin_act_db), 0)


@unittest.skipIf(db_skip, 'Skip DB tests')
class TestMonitoringDB(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db_params_dict = {}
        cls.db_params_dict['db_type'] = 'sqlite'
        cls.db_params_dict['db_path'] = db_dir

    def test_garmin_mon_db_exists(self):
        garmin_mon_db = GarminDB.MonitoringDB(self.db_params_dict)
        self.assertIsNotNone(garmin_mon_db)

    def test_garmin_mon_db_tables_exists(self):
        garmin_mon_db = GarminDB.MonitoringDB(self.db_params_dict)
        self.assertGreater(GarminDB.MonitoringInfo.row_count(garmin_mon_db), 0)
        self.assertGreater(GarminDB.MonitoringHeartRate.row_count(garmin_mon_db), 0)
        self.assertGreater(GarminDB.MonitoringIntensity.row_count(garmin_mon_db), 0)
        self.assertGreater(GarminDB.MonitoringClimb.row_count(garmin_mon_db), 0)
        self.assertGreater(GarminDB.Monitoring.row_count(garmin_mon_db), 0)

    def test_garmin_mon_db_steps_bounds(self):
        garmin_mon_db = GarminDB.MonitoringDB(self.db_params_dict)
        min = GarminDB.Monitoring.get_col_min(garmin_mon_db, GarminDB.Monitoring.steps)
        self.assertGreater(min, 0)
        max = GarminDB.Monitoring.get_col_max(garmin_mon_db, GarminDB.Monitoring.steps)
        self.assertGreater(max, 0)
        self.assertLess(max, 100000)


@unittest.skipIf(db_skip, 'Skip DB tests')
class TestGarminSummaryDB(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db_params_dict = {}
        cls.db_params_dict['db_type'] = 'sqlite'
        cls.db_params_dict['db_path'] = db_dir

    def test_garminsumdb_exists(self):
        garminsumdb = GarminDB.GarminSummaryDB(self.db_params_dict)
        self.assertIsNotNone(garminsumdb)

    def test_garminsumdb_tables_exists(self):
        garminsumdb = GarminDB.GarminSummaryDB(self.db_params_dict)
        self.assertTrue(GarminDB.Summary.row_count(garminsumdb) > 0)
        self.assertTrue(GarminDB.MonthsSummary.row_count(garminsumdb) > 0)
        self.assertTrue(GarminDB.WeeksSummary.row_count(garminsumdb) > 0)
        self.assertTrue(GarminDB.DaysSummary.row_count(garminsumdb) > 0)

    def test_garminsumdb_cols_have_values(self):
        garminsumdb = GarminDB.GarminSummaryDB(self.db_params_dict)
        self.assertGreater(GarminDB.MonthsSummary.get_col_max(garminsumdb, GarminDB.MonthsSummary.hr_avg), 0)
        self.assertGreater(GarminDB.MonthsSummary.get_col_max(garminsumdb, GarminDB.MonthsSummary.hr_min), 0)
        self.assertGreater(GarminDB.MonthsSummary.get_col_max(garminsumdb, GarminDB.MonthsSummary.hr_max), 0)
        self.assertGreater(GarminDB.MonthsSummary.get_col_max(garminsumdb, GarminDB.MonthsSummary.rhr_avg), 0)
        self.assertGreater(GarminDB.MonthsSummary.get_col_max(garminsumdb, GarminDB.MonthsSummary.rhr_min), 0)
        self.assertGreater(GarminDB.MonthsSummary.get_col_max(garminsumdb, GarminDB.MonthsSummary.rhr_max), 0)
        self.assertGreater(GarminDB.MonthsSummary.get_col_max(garminsumdb, GarminDB.MonthsSummary.weight_avg), 0)
        self.assertGreater(GarminDB.MonthsSummary.get_col_max(garminsumdb, GarminDB.MonthsSummary.weight_min), 0)
        self.assertGreater(GarminDB.MonthsSummary.get_col_max(garminsumdb, GarminDB.MonthsSummary.weight_max), 0)
        self.assertGreater(GarminDB.MonthsSummary.get_col_max(garminsumdb, GarminDB.MonthsSummary.stress_avg), 0)
        self.assertGreater(GarminDB.MonthsSummary.get_col_max(garminsumdb, GarminDB.MonthsSummary.calories_avg), 0)
        self.assertGreater(GarminDB.MonthsSummary.get_col_max(garminsumdb, GarminDB.MonthsSummary.calories_bmr_avg), 0)
        self.assertGreater(GarminDB.MonthsSummary.get_col_max(garminsumdb, GarminDB.MonthsSummary.calories_active_avg), 0)
        self.assertGreater(GarminDB.MonthsSummary.get_col_max(garminsumdb, GarminDB.MonthsSummary.activities), 0)
        self.assertGreater(GarminDB.MonthsSummary.get_col_max(garminsumdb, GarminDB.MonthsSummary.activities_calories), 0)
        self.assertGreater(GarminDB.MonthsSummary.get_col_max(garminsumdb, GarminDB.MonthsSummary.activities_distance), 0)

class TestFit(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.english_units = True
        cls.file_path = 'test_files/fit'
        cls.unknown_messages = []
        cls.unknown_message_fields = {}

    def check_message_types(self, fit_file):
        message_types = fit_file.message_types()
        for message_type in message_types:
            if message_type.name.startswith('unknown'):
                if message_type.name not in self.unknown_messages:
                    print ("Unknown message type: %s in %s" % (message_type.name, fit_file.type()))
                    self.unknown_messages.append(message_type.name)
            messages = fit_file[message_type]
            for message in messages:
                self.check_message_fields(message)

    def check_message_fields(self, message):
        self.check_timestamp(message)
        for field_name in message:
            if field_name.startswith('unknown'):
                message_type = message.type()
                field_value = str(message[field_name].value)
                if message_type not in self.unknown_message_fields:
                    print ("Unknown %s message field: %s value %s" % (message_type, field_name, field_value))
                    self.unknown_message_fields[message_type] = [field_name]
                elif field_name not in self.unknown_message_fields[message_type]:
                    print ("Unknown %s message field: %s value: %s" % (message_type, field_name, field_value))
                    self.unknown_message_fields[message_type].append(field_name)

    def check_value(self, message, key, expected_value):
        if key in message:
            value = message[key].value
            # print '\t' + repr(message[key])
            self.assertEqual(value, expected_value)

    def check_value_range(self, message, key, min_value, max_value):
        if key in message:
            value = message[key].value
            # print '\t' + repr(message[key])
            self.assertGreaterEqual(value, min_value)
            self.assertLess(value, max_value)

    def check_timestamp(self, message):
        self.check_value_range(message, 'timestamp', datetime.datetime(2000, 1, 1), datetime.datetime.now())

    def check_file_id(self, fit_file, file_type):
        messages = fit_file[Fit.MessageType.file_id]
        for message in messages:
            # print repr(message._fields)
            self.check_value(message, 'manufacturer', Fit.FieldEnums.Manufacturer.Garmin)
            self.check_value(message, 'type', file_type)

    def check_monitoring_file(self, filename):
        print ''
        fit_file = Fit.File(filename, self.english_units)
        self.check_message_types(fit_file)
        print filename + ' message types: ' + repr(fit_file.message_types())
        self.check_file_id(fit_file, Fit.FieldEnums.FileType.monitoring_b)
        messages = fit_file[Fit.MessageType.monitoring]
        for message in messages:
            # print repr(message._fields)
            self.check_message_fields(message)
            self.check_value_range(message, 'distance', 0, 100 * 5280)
            self.check_value_range(message, 'temperature_min', 0, 80)
            self.check_value_range(message, 'temperature_max', 0, 100)
            self.check_value_range(message, 'cum_ascent', 0, 5280)
            self.check_value_range(message, 'cum_descent', 0, 5280)

    def test_parse_monitoring(self):
        monitoring_path = self.file_path + '/monitoring'
        file_names = FileProcessor.dir_to_files(monitoring_path, '.*\.fit', False)
        for file_name in file_names:
            self.check_monitoring_file(file_name)

    def check_activity_file(self, filename):
        print ''
        fit_file = Fit.File(filename, self.english_units)
        print filename + ' message types: ' + repr(fit_file.message_types())
        self.check_message_types(fit_file)
        self.check_file_id(fit_file, Fit.FieldEnums.FileType.activity)
        messages = fit_file[Fit.MessageType.record]
        for message in messages:
            self.check_message_fields(message)
            # print repr(message._fields)
            self.check_value_range(message, 'temperature', 0, 100)
            if 'distance' in message and message['distance'].value > 0.1:
                self.check_value_range(message, 'distance', 0, 100 * 5280)
                self.check_value_range(message, 'avg_vertical_oscillation', 0, 10)
                self.check_value_range(message, 'step_length', 24, 64)
                self.check_value_range(message, 'speed', 0, 25)

    def test_parse_activity(self):
        activity_path = self.file_path + '/activity'
        file_names = FileProcessor.dir_to_files(activity_path, '.*\.fit', False)
        for file_name in file_names:
            self.check_activity_file(file_name)

if __name__ == '__main__':
    unittest.main(verbosity=2)

