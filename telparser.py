#Argument parser for TeleMetrics

import argparse

def argumentGet():
    parser = argparse.ArgumentParser(description='Run estimators and gather data from MINion telemetry files')
    parser.add_argument('-a', '--auto', help='turns run off automatically if tests are within acceptable parameters', action='store_true')
    parser.add_argument('location', help='location of the telemetry file')
    parser.add_argument('-%', '--percent', type=float, help='accuracy percentage threshold', default=70.0)
    parser.add_argument('-t', '--time', type=int, default=30, help='time between checks of file')
    parser.add_argument('runID', help='unique identifier for this run')
    parser.add_argument('-v', '--verbose', help='prints output to console', action='store_true')
    args = parser.parse_args()
    return args

