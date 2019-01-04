import requests, configparser, os, argparse, time
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from datetime import datetime


class WebMon:

    CONFIG = configparser.ConfigParser()  # init config

    def __init__(self):

        print('created by @snags141')

        self.init_ini()  # initialise config
        args = self.parse_args()

        if args.addtargets:
            self.add_targets()  # run add targets
        else:
            if args.listtargets:
                self.print_all_targets()
            else:
                if args.scan:
                    if self.get_target_count() > 0:
                        self.do_scan()
                    else:
                        print("No targets specified!\nrun webmon.py -a")
                else:  # Run as normal
                    self.start_monitor()  # start the monitoring process

    def parse_args(self):
        parser = argparse.ArgumentParser(description='Use -a to quickly add targets to the config file')
        parser.add_argument('-a', '--addtargets', action='store_true', help='Add host targets to the config file')
        parser.add_argument('-l', '--listtargets', action='store_true', help='List current target host names')
        parser.add_argument('-s', '--scan', action='store_true', help='Run a scan of all current targets once')
        args = parser.parse_args()

        return args

    # write config file
    def write_file(self):
        self.CONFIG.write(open('config.ini', 'w'))

    def init_ini(self):

        # if doesnt exist, write default
        if not os.path.exists('config.ini'):
            self.add_targets()
        else:
            self.CONFIG.read("config.ini")

    def print_all_targets(self):
        print('\nCurrent Targets:')
        # Loop through CONFIG and print section titles
        for each_section in self.CONFIG.sections():
            print(' - ' + each_section)

    def add_targets(self):

        flag = 'y'

        while flag == 'y' or flag == 'Y':
            host_name = self.set_host_name()

            url = self.set_url()

            interval = self.set_interval()

            self.CONFIG[host_name] = {'target_url': url, 'interval_time': interval, 'last_scan': ""}
            self.write_file()

            print('\nAdd another target? y/n')
            flag = input('> ')

    def set_url(self):

        valid = False

        url = input('Please enter a target URL (incl. http(s)://)\n> ')

        while valid is False:

            val = URLValidator()

            try:
                val(url)
                if val:
                    valid = True

            except ValidationError:
                if url == '':
                    url = input('Please enter a target URL (incl. http(s)://)\n> ')
                else:
                    print('URL is not valid\n')
                    url = input('Please enter a valid URL (incl. http(s)://)\n> ')

        return url

    def validate_url(self, url):
        valid = False

        val = URLValidator()

        try:
            val(url)
            if val:
                valid = True
        except ValidationError:
            if url == '':
                print('URL is blank\n')
            else:
                print('URL is not valid\n')

        return valid

    def set_interval(self):  # Set the interval_time (int minutes) to check the site
        usr_input = input("How long between scans? (minutes):\n> ")

        return usr_input

    def get_target_count(self):

        count = 0

        for each_section in self.CONFIG.sections():
            count += 1

        return count

    def get_current_datetime(self):
        today = datetime.today()
        current_time = today.strftime('%Y-%m-%d %H:%M:%S')

        return current_time

    def get_time_diff(self, last_scan):

        current_time = self.get_current_datetime()

        fmt = '%Y-%m-%d %H:%M:%S'
        d1 = datetime.strptime(last_scan, fmt)  # '2018-11-09 6:00:00'
        d2 = datetime.strptime(current_time, fmt)

        # Convert to Unix timestamp
        d1_ts = time.mktime(d1.timetuple())
        d2_ts = time.mktime(d2.timetuple())

        # They are now in seconds, subtract and then divide by 60 to get minutes.
        time_difference = int(d2_ts - d1_ts) / 60  # Time difference in minutes

        return time_difference

    def set_host_name(self):

        valid = False

        host_name = input('Enter a name for this host\n> ')

        while not valid:

            # check if host_name already exists
            if self.CONFIG.has_section(host_name):
                print('A host with this name already exists\nPlease enter something else\n> ')
            # If not, proceed, if so, do nothing
            else:
                valid = True

        return host_name

    def update_config_section(self, section, target_url, interval_time, last_scan):
        self.CONFIG[section] = {'target_url': target_url, 'interval_time': interval_time,
                                'last_scan': last_scan}
        self.write_file()

    def start_scan(self, host_name, url):  # Initiate a scan on the given URL

        r = None
        status_code = None

        try:
            r = requests.get(url)
        except requests.exceptions.Timeout:
            error_string = "An error occured: timeout"
            self.write_log(host_name, 'Error', error_string)
            print(error_string)
        except requests.exceptions.TooManyRedirects:
            error_string = "An error occured: toomanyredirects"
            self.write_log(host_name, 'Error', error_string)
            print(error_string)
        except requests.exceptions.RequestException as e:
            print("an exception occurred")
            exception_args = e.args[0]
            error_string = str(exception_args)
            self.write_log(host_name, 'Error')
            print("Error = " + error_string)
            print(e)

        if r is not None:
            status_code = r.status_code
            self.write_log(host_name, 'Status Response', 'status_code = ' + str(status_code))

        print("Status code for " + host_name + " = " + str(status_code))

    def do_scan(self):
        for each_section in self.CONFIG.sections():

            target_url = self.CONFIG.get(each_section, 'target_url')

            interval_time = self.CONFIG.get(each_section, 'interval_time')

            last_scan = self.CONFIG.get(each_section, 'last_scan')

            # debug
            print('Target URL:')
            print(target_url)
            print('Interval Time:')
            print(interval_time)
            print('Last Scan:')
            print(last_scan)

            if not self.validate_url(target_url):
                print('Error: URL %s' % target_url + ' is not valid')
                break  # Quit program, config must have been changed outside of program

            if interval_time == '':
                print('Error: not configured properly for %s' % target_url)
                print('Missing interval_time')
                break  # Quit program, config must have been changed outside of program

            if last_scan == '':
                self.start_scan(each_section, target_url)
                self.update_config_section(each_section, target_url, interval_time, self.get_current_datetime())
            else:
                if int(self.get_time_diff(last_scan)) >= int(interval_time):
                    self.start_scan(each_section, target_url)
                    self.update_config_section(each_section, target_url, interval_time, self.get_current_datetime())

    def start_monitor(self):  # Start monitoring the target URL

        while 1 == 1:

            print('*Monitor started: running every 5 seconds*')

            time.sleep(5)

            self.do_scan()

            print('Waiting ...\n')

    def write_log(self, host_name, msg_type, error_string):
        log_file = './webmonlog.txt'
        log = open(log_file, "a")
        log.write(host_name + ' | ' + str(self.get_current_datetime) + ' | ' + msg_type + ': | ' + str(error_string))
        log.close()


WebMon()
