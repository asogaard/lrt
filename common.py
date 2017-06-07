# -*- coding: utf-8 -*-

""" Common definitions for LRT plotting macros.

Author: Andreas Sogaard (@asogaard)
Date:   7 June 2017
"""

# ROOT
import ROOT

# Command-line arguments parser
import argparse

parser = argparse.ArgumentParser(description="Produce publication-ready plots for the large-radius tracking (LRT) PUBNOTE.")

parser.add_argument('--show', dest='show', action='store_const',
                    const=True, default=False,
                    help='Show plots (default: False)')
parser.add_argument('--save', dest='save', action='store_const',
                    const=True, default=False,
                    help='Save plots (default: False)')

# Get the text-line describing the signal model
def signal_line (signal):
    if   signal == 'RPV':     return "Displaced leptons"
    elif signal == 'Rhadron': return "Displaced hadrons"
    return "NA"

# Get the text-line describing the collection of tracks used in the plot
def track_line (t, name):
    if t == 'Signal':
        return 'Signal {name} tracks'.format(name = name.lower())
    return '{name} tracks'.format(name = name)

# Colours
colours = [ROOT.kViolet + 7, ROOT.kAzure + 7, ROOT.kTeal, ROOT.kSpring - 2, ROOT.kOrange - 3, ROOT.kPink]

# Low-stats, using new RPV sample with updated fiducial selection
filename = '/eos/atlas/user/a/asogaard/Qualification/validation/2017-06-06//output_{signal}.root'
    
