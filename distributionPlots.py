#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Script for producing ...

Author: Andreas Sogaard (@asogaard)
Date:   22 June 2017
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

    # Settings
    signals = ['RPV', 'Rhadron']
    variables = ['pt', 'prodR']
    histname = "IDPerformanceMon/LargeD0/basicPlot/SignalParticles/truth{var}"
    rebin = {
        'RPV':     2,
        'Rhadron': 1,
        }
    
    # Loop variables
    for var in variables:

        # Load histograms
        histograms = list()
        hn = histname.format(var=var)
        for signal in signals:
            f = ROOT.TFile(filename.format(signal=signal), 'READ')
            try:
                h = f.Get(hn)
                h.SetDirectory(0)
                if signal in rebin: h.Rebin(rebin[signal])
            except: # Plot doesn't exist for 'signal'
                print "Histogram '%s' does not exist for signal '%s'" % (hn, signal)
                h = None
                continue
            histograms.append(h)
            pass
        
        # Draw figure
        c = ap.canvas(batch=not args.show)
        for hist, signal, col in zip(histograms, signals, colours):
            c.hist(hist, label=signal_line(signal), linecolor=col, normalise=True)
            pass
        c.xlabel(displayNameUnit(var))
        c.ylabel("Fraction of signal particles")
        c.text(["MC truth"], qualifier=qualifier)
        c.legend()
        c.logy()
        if args.save: c.save('plots/distributions_{var}.pdf'.format(var=var))
        if args.show: c.show()
        pass

    return


if __name__ == '__main__':
    main()
    pass

