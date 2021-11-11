#!/usr/bin/python
# https://github.com/joncloud/locust-csv-to-junit-xml/blob/publish/main.py

import csv
import datetime
import getopt
import sys
import xml.etree.ElementTree as ET


def main(argv):
    prefix = ''

    try:
        opts, _ = getopt.getopt(sys.argv[1:], 'hp:', ['prefix='])
    except getopt.GetoptError:
        print('main.py -p <prefix>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('main.py -p <prefix>')
            sys.exit()
        elif opt in ("-p", "--prefix"):
            prefix = arg

    if prefix == '':
        raise Exception('Prefix was not assigned')

    testsuites, testsuite = create_testsuites()
    append_testcases(prefix, testsuite)

    xml_tree = ET.ElementTree(testsuites)
    xml_tree.write("test_results.xml")


def create_testsuites():
    testsuites = ET.Element('testsuites')

    testsuite = ET.SubElement(testsuites, 'testsuite')
    testsuite.set('name', 'Locust Tests')

    timestamp = str(datetime.datetime.now()).replace(
        ' ',
        'T'
    )
    testsuite.set('timestamp', timestamp)

    return (testsuites, testsuite)


def append_testcases(prefix, testsuite):
    test_count = 0
    failure_count = 0

    with open(prefix + '_requests.csv', mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)

        line_count = 0
        for row in csv_reader:

            if line_count > 0:
                row_method = row['Method']
                row_name = row['Name']

                if row_method != 'None' and row_name != 'Total':
                    testcase = ET.SubElement(testsuite, 'testcase')

                    name = f'{row_method}\t{row_name} Average response time'
                    testcase.set('name', name)

                    test_count += int(row['# requests'])
                    failure_count += int(row['# failures'])
                    avg_response_s = float(row['Average response time']) / 1000
                    testcase.set('time', str(avg_response_s))

            line_count += 1

        testsuite.set('tests', str(test_count))
        testsuite.set('failures', str(failure_count))


if __name__ == '__main__':
    main(sys.argv[1:])