#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Script for producing publication-ready resolution- and pull plots for the large-radius tracking (LRT) PUBNOTE.

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
from snippets.functions import displayName, displayUnit, displayNameUnit

# Main function definition.
def main ():
    
    # Parse command-line arguments
    args = parser.parse_args()

    # Comparing signal track resolution for LRT and STD tracks
    # --------------------------------------------------------------------------

    # Initialise categories for which to plot distinct curves for each histogram
    algorithms = ['Standard', 'LargeD0']
    names      = ['Standard', 'Large radius']
    signals    = ['RPV', 'Rhadron']
    rels       = ['res', 'resRel', 'pull']
    
    # Initialise variable versus which to plot the physics efficiency
    basic_vars = ['theta', 'phi', 'd0', 'z0', 'qOverP']
        
    # Initialise list of histograms to be plotted 
    base = 'IDPerformanceMon/LargeD0/'
    histname = base + 'ResolutionPlots/{alg}Tracks/Signal/{rel}_{var}'
        
    # Loop all combinations of track parameter, resolution type, and signal process.
    for var, rel, signal in itertools.product(basic_vars, rels, signals):
        
        # Open file from which to read histograms.
        f = ROOT.TFile(filename.format(signal=signal), 'READ')
        ROOT.TH1.AddDirectory(False)
        
        # Get list of histograms to plot
        histograms = list()
        
        for alg in algorithms:
            h = f.Get(histname.format(alg=alg, var=var, rel=rel))
            h.SetDirectory(0) # Keep in memory after file is closed.
            h.GetXaxis().SetNdivisions(507)
            h.GetYaxis().SetNdivisions(507)
            ax = h.GetXaxis()
            rebin = 1
            if signal == 'Rhadron':
                rebin = 2
                pass
            h.Rebin(rebin)
            ax.SetRangeUser(ax.GetXmin() / 10., ax.GetXmax() / 10.)
            histograms.append(h)
            pass
        
        # Close file
        f.Close()
        
        # Draw figure
        c = ap.canvas(batch=not args.show, size=(700, 500))
        for ihist, (hist, name, col) in enumerate(zip(histograms, names, colours)):
            c.hist(hist, linecolor=col, linewidth=3, linestyle=1+ihist, normalise=True, option='HIST')#, label=name + " tracks", normalise=True, option='HIST E2')
            c.hist(hist, linecolor=col, fillcolor=col, alpha=0.4, normalise=True, option='E2')
            pass
        c.text([signal_line(signal)],
               qualifier=qualifier)
        c.legend(width=0.28, categories=[
                (names[0] + " tracks", {'linecolor':colours[0], 'linewidth':3, 'linestyle':1, 'fillcolor':colours[0], 'alpha':0.4, 'option': 'FL'}),
                (names[1] + " tracks", {'linecolor':colours[1], 'linewidth':3, 'linestyle':2, 'fillcolor':colours[1], 'alpha':0.4, 'option': 'FL'})
                #('Statistical uncert.', {'fillcolor': ROOT.kGray, 'linecolor': ROOT.kGray + 1, 'option': 'F'})
                ])
        c.xlabel("%s^{reco.} - %s^{truth} [%s]" % (displayName(var), displayName(var), displayUnit(var)))
        c.ylabel("Fraction of tracks")

        # Show/save
        savename = '_'.join([signal] + histname.format(alg='Combined', var=var, rel=rel).split('/')[2:]) + '.pdf'
        if args.show: c.show()
        if args.save: c.save('plots/' + savename)
        pass
  
    
    # Binned by matching probability
    # --------------------------------------------------------------------------
    
    # Initialise categories for which to plot distinct curves for each histogram
    algorithms = ['Standard', 'LargeD0']
    names      = ['Standard', 'Large radius']
    types      = ['All', 'Signal']
    signals    = ['RPV', 'Rhadron']
    rels = ['res', 'resRel', 'pull']
    groups = ['prob_0p40_0p50/',
              'prob_0p50_0p60/',
              'prob_0p60_0p70/',
              'prob_0p70_0p80/',
              'prob_0p80_0p90/',
              'prob_0p90_1p00/',
              ]
    
    group_names = [ '[%s]' % grp[5:-1].replace('_', ', ').replace('p', '.') for grp in groups ]
    
    # Initialise variable versus which to plot the physics efficiency
    basic_vars = ['theta', 'phi', 'd0', 'z0', 'qOverP']
    
    # Initialise list of histograms to be plotted 
    base = 'IDPerformanceMon/LargeD0/'
    histname = base + 'ResolutionPlots/{alg}Tracks/{t}/{group}{rel}_{var}'
    
    # Loop all combinations of track parameter, tracking algorithm, truth particle type, resolution type, and signal process
    for var, (alg, name), t, rel, signal in itertools.product(basic_vars, zip(algorithms, names), types, rels, signals):
        
        # Open file from which to read histograms.
        f = ROOT.TFile(filename.format(signal=signal), 'READ')
        ROOT.TH1.AddDirectory(False)
        
        # Get list of histograms tp plot, manually.
        histograms = list()
        
        # Loop probability bins
        for igroup, group in enumerate(groups):
            h = f.Get(histname.format(alg=alg, var=var, t=t, rel=rel, group=group))
            h.SetDirectory(0) # Keep in memory after file is closed.
            h.Rebin(10) # 10
            histograms.append(h)
            pass
        
        # Close file
        f.Close()
        
        # Draw figure
        c = ap.canvas(batch=not args.show, size=(700, 500))
        for ihist, (hist, grp, col) in enumerate(zip(histograms, group_names, colours_pretty)):
            c.hist(hist, linecolor=col, linewidth=3, linestyle=1+ihist, label=grp, normalise=True)
            pass
        c.text([signal_line(signal),
                name + " tracks"]
               + (["%s particles" % t] if t != 'Signal' else []),
               qualifier=qualifier)
        c.legend(header="Match prob. in:", width=0.28, ymax=0.872)
        c.xlabel("%s^{reco.} - %s^{truth} [%s]" % (displayName(var), displayName(var), displayUnit(var)))
        c.ylabel("Fraction of tracks")
        c.padding(0.40)
        c.log()

        # Show/save
        savename = '_'.join([signal] + histname.format(alg=alg, var=var, t=t, rel=rel, group='').split('/')[2:]) + '.pdf'
        if args.show: c.show()
        if args.save: c.save('plots/' + savename)
        pass
    
    return


if __name__ == '__main__':
    main()
    pass

