#Argument parser for TeleMetrics

import argparse

def argumentGet():
    parser = argparse.ArgumentParser(description='Run estimators and gather data from MINion telemetry files')
    parser.add_argument('-a', '--auto', help='toggles off automatic termination', action='store_false', default=True)
    parser.add_argument('-t', '--time', type=int, default=35, help='time between checks of file')
    parser.add_argument('runID', help='unique identifier for this run')
    parser.add_argument('-v', '--verbose', help='prints output to console', action='store_true')
    parser.add_argument('-i', '--input', help="RunID from epi2me", default=None)
    parser.add_argument('-g', '--csv_get', help="toggle csv download", action='store_true', default=False)
    parser.add_argument('-b', '--barcodes', help="valid barcodes in format: BC03,BC04")
    args = parser.parse_args()
    return args

