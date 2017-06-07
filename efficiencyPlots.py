#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" 
Script for producing publication-ready efficiency plots for the large-radius tracking (LRT) PUBNOTE.

Author: Andreas Sogaard (@asogaard)
Date:   7 June 2017
"""

# Basic
import itertools

# ROOT
import ROOT 

# Local
from common import *
from rootplotting import ap
from rootplotting.tools import *

# Command-line arguments parser
import argparse

parser = argparse.ArgumentParser(description="Produce publication-ready efficiency plots for the large-radius tracking (LRT) PUBNOTE.")

parser.add_argument('--show', dest='show', action='store_const',
                    const=True, default=False,
                    help='Show plots (default: False)')
parser.add_argument('--save', dest='save', action='store_const',
                    const=True, default=False,
                    help='Save plots (default: False)')

# Main function definition.
def main ():

    # Parse command-line arguments
    args = parser.parse_args()

    # Initialise categories for which to plot distinct curved for each histogram
    algorithms = ['Standard', 'LargeD0']
    names      = ['Standard', 'Large-radius']
    types   = ['', 'Primary', 'Secondary', 'Signal']
    signals = ['RPV', 'Rhadron']

    # Initialise variable versus which to plot the physics efficiency
    basic_vars = ['eta', 'phi', 'd0', 'z0', 'pt', 'R', 'Z', 'pt_low', 'pt_high']

    # Initialise list of histograms to be plotted 
    base = 'IDPerformanceMon/LargeD0/'
    histnames = [base + 'EffPlots/{{alg}}Tracks/{{t}}trackeff_vs_{var}'.format(var=var) for var in basic_vars]

    # Read in and plot each histogram
    for fn, hn, t, signal in itertools.product([filename], histnames, types, signals):
            
        # Generate list of (path, histname) pairs to plot
        pathHistnamePairs = zip([fn.format(signal=signal)] * len(histnames), [hn.format(t=t + ('/' if t != '' else ''), alg=alg) for alg in algorithms])
        
        # Load in histograms
        histograms = list()
        for path, histname in pathHistnamePairs:
            f = ROOT.TFile(path, 'READ')
            h = f.Get(histname)
            h.SetDirectory(0)
            histograms.append(h)
            f.Close()
            pass

        # Draw figure
        c = ap.canvas(batch=not args.show)
        for hist, name, col in zip(histograms, names, colours):
            c.plot(hist, linecolor=col, markercolor=col, label=name)
            pass
        c.text([signal_line(signal),
                "Fiducial selection applied",
                ], # + ([t + " particles"] if t != '' else []), 
               qualifier="Simulation Internal")
        c.legend(header="Track category:")

        # Show/save
        savename = '_'.join([signal] + hn.format(t=t + ('/' if t != '' else ''), alg='').split('/')[2:]) + '.pdf'
        if args.show: c.show()
        if args.save: c.save('plots/' + savename)
        pass

    return


if __name__ == '__main__':
    main()
    pass
