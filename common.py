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

#qualifier = "Simulation Preliminary"
qualifier = "Simulation Internal"

# Colours (pretty)
colours_pretty = [ROOT.kViolet + 7, ROOT.kAzure + 7, ROOT.kTeal, ROOT.kSpring - 2, ROOT.kOrange - 3, ROOT.kPink]
# Colours (ugly; for note)
colours = [ROOT.kRed, ROOT.kBlue, ROOT.kBlack, ROOT.kGreen, ROOT.kViolet, ROOT.kCyan, ROOT.kOrange]

# Low-stats, using new RPV sample with updated fiducial selection
#filename = '/eos/atlas/user/a/asogaard/Qualification/validation/2017-06-06/output_{signal}.root'

# High-stats
#filename = '/eos/atlas/user/a/asogaard/Qualification/validation/2017-06-07/output_{signal}.root'

# Low-stats, with track pT > 1000 MeV
#filename = '/eos/atlas/user/a/asogaard/Qualification/validation/2017-06-08/output_{signal}.root'
    
# High-stats, new RPV signal definition
#filename = '/eos/atlas/user/a/asogaard/Qualification/validation/2017-06-09/output_{signal}.root'

# High-stats, better resolution robustness binning
#filename = '/eos/atlas/user/a/asogaard/Qualification/validation/2017-06-10/output_{signal}.root'

# High-stats, only signal muons for RPV
#filename = '/eos/atlas/user/a/asogaard/Qualification/validation/2017-06-15/output_{signal}.root'

# High-stats, same R-hadron sample as Margaret
#filename = '/eos/atlas/user/a/asogaard/Qualification/validation/2017-06-17/output_{signal}.root'

# High-stats, smaller pT-range for robustness plots
#filename = '/eos/atlas/user/a/asogaard/Qualification/validation/2017-06-18/output_{signal}.root'

# High-stats, impose pT > 1000 MeV
#filename = '/eos/atlas/user/a/asogaard/Qualification/validation/2017-06-19/output_{signal}.root'

# High-stats, better Rprod binning for robustness studies
#filename = '/eos/atlas/user/a/asogaard/Qualification/validation/2017-06-21/output_{signal}.root'

# High-stats, better pT binning for robustness studies for RPV
#filename = '/eos/atlas/user/a/asogaard/Qualification/validation/2017-06-22/output_{signal}.root'

# High-stats, better truthprodR range
#filename = '/eos/atlas/user/a/asogaard/Qualification/validation/2017-06-22b/output_{signal}.root'

# High-stats, better q/p resolution robustness binning
#filename = '/eos/atlas/user/a/asogaard/Qualification/validation/2017-06-24/output_{signal}.root'
#filename = '/afs/cern.ch/user/a/asogaard/Qualification/validation-rel21-2017-01-24/run/2017-06-24/output_{signal}.root'

# High-stats, 10k events for R-hadron
#filename = '/eos/atlas/user/a/asogaard/Qualification/validation/2017-06-30/output_{signal}.root'

# High-stats, pT cut applied to truth rather than tracks
#filename = '/eos/atlas/user/a/asogaard/Qualification/validation/2017-07-05/output_{signal}.root'

# High-stats, pT-binned resolution robustness
filename = '/eos/atlas/user/a/asogaard/Qualification/validation/2017-07-06/output_{signal}.root'
