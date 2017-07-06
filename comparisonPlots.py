#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" 
Script for ...

Author: Andreas Sogaard (@asogaard)
Date:   4 July 2017
"""

# Basic
import itertools

# ROOT
import ROOT 

# Local
from common import *
from rootplotting import ap
from rootplotting.tools import *
from snippets.functions import displayNameUnit


# Main function definition.
def main ():

    # Parse command-line arguments
    args = parser.parse_args()

    # Input paths
    #base_path = '/afs/cern.ch/user/a/asogaard/Qualification/validation-rel21-2017-01-24/run/'
    base_path = '/eos/atlas/user/a/asogaard/Qualification/validation/'
    paths = [
        #base_path + '2017-06-30/output_Rhadron0.root',
        #base_path + '2017-06-30/output_Rhadron4.root',
        #base_path + '2017-07-04/output_Rhadron4.root',
        #base_path + '2017-07-05/output_Rhadron0.root',
        #base_path + 'output_Rhadron0.root',
        base_path + '2017-06-30/output_Rhadron.root',
        base_path + '2017-07-05/output_Rhadron.root',
        ]

    # Histograms to be compared
    histogram_names = [
        'IDPerformanceMon/LargeD0/EffPlots/StandardTracks/Signal/trackeff_vs_R',
        'IDPerformanceMon/LargeD0/EffPlots/LargeD0Tracks/Signal/trackeff_vs_R',
        'IDPerformanceMon/LargeD0/EffPlots/AllTracks/Signal/trackeff_vs_R',
        ]


    # Read in histograms
    histograms = list()
    for path in paths:
        histograms.append(list())
        f = ROOT.TFile(path, 'READ')
        for name in histogram_names:
            h = f.Get(name)
            h.SetDirectory(0)
            h.RebinX(2)
            histograms[-1].append(h)
            pass
        f.Close()
        pass

    # Definitions
    names = ['Standard tracks', 'Large radius tracks', 'Combined']

    # Draw figure
    c = ap.canvas(batch=not args.show, size=(700, 500))
    for ihist, (hist, name, col) in enumerate(zip(histograms[0], names, colours)):
        c.plot(hist, linecolor=col, markercolor=col, linestyle=1, markerstyle=20, option='PE', label=name, legend_option='L')
        pass
    for ihist, (hist, name, col) in enumerate(zip(histograms[1], names, colours)):
        c.plot(hist, linecolor=col, markercolor=col, linestyle=2, markerstyle=24, option='PE')
        pass
    c.text([signal_line('Rhadron')],
           qualifier=qualifier)

    c.ylim(0, 1.6)

    c.xlabel(displayNameUnit('r'))
    c.ylabel("Reconstruction effiency")
    c.legend(width=0.28, categories=[
            ('30/06/2017', {'linestyle':1, 'markerstyle':20, 'option':'PL'}),
            ('05/07/2017', {'linestyle':2, 'markerstyle':24, 'option':'PL'}),
            ])

    # Show/save
    savename = 'comparison.pdf'
    if args.show: c.show()
    if args.save: c.save('plots/' + savename)
    pass

    return


if __name__ == '__main__':
    main()
    pass
