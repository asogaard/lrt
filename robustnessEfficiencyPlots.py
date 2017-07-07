#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Script for producing publication-ready efficiency robustness plots for the large-radius tracking (LRT) PUBNOTE.

Author: Andreas Sogaard (@asogaard)
Date:   7 June 2017
"""

# Basic
import itertools, array

# ROOT
import ROOT

# Local
from common import *
from rootplotting import ap
from rootplotting.tools import *
from snippets.functions import displayName

# Main function definition.
def main ():

    # Macro-specific styles
    ROOT.gROOT.GetStyle("AStyle").SetEndErrorSize(.5)

    # Parse command-line arguments
    args = parser.parse_args()

    # Initialise categories for which to plot distinct curves for each histogram
    algorithms = ['Standard', 'LargeD0']
    names      = ['Standard', 'Large radius']
    types      = ['Signal'] # ['All', 'Signal']
    signals = ['RPV', 'Rhadron'] 
    groups = ['R10mm_30mm/',
              'R30mm_100mm/',
              'R100mm_300mm/',
              ]
    #groups = ['R20mm_50mm/',
    #          'R100mm_150mm/',
    #          'R200mm_300mm/',
    #          ]

    group_names = [ '[%s]' % grp[1:-1].replace('_', ', ').replace('p', '.').replace('mm', ' mm') for grp in groups ]
    # @TEMP: Fix type in histogram names: 30mm_300mm -> 100mm_300mm
    #group_names = [gn.replace('30mm, 300mm', '100mm, 300mm') for gn in group_names]

    # Initialise list of histograms to be plotted 
    base = 'IDPerformanceMon/LargeD0/'
    histname = base + 'EffPlots/{alg}Tracks/{t}/{group}trackeff_vs_mu'

    edges = [0, 10, 15, 20, 25, 30, 40]

    # Loop all combinations of truth particle type and signal process
    for t, signal in itertools.product(types, signals):

        # Open file from which to read histograms.
        f = ROOT.TFile(filename.format(signal=signal), 'READ')
        ROOT.TH1.AddDirectory(False)
        ROOT.TH2.AddDirectory(False)
        
        # Get list of histograms tp plot, manually.
        histograms = list()

        # Get histograms
        for alg in algorithms:
            # Loop production radii groups
            for group in groups:
                h = f.Get(histname.format(alg=alg, t=t, group=group))
                h.SetDirectory(0) # Keep in memory after file is closed.
                #h.RebinX(2)
                newname = h.GetName() + "_rebinned_" + group + "_" + alg
                hn = h.Rebin(len(edges)-1, newname, array.array('d',edges))
                #histograms.append(h)
                histograms.append(hn)
                pass
            pass
        
        # Close file
        f.Close()


        # Efficiency of STD and LRT separately
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

        # Draw figure
        c = ap.canvas(batch=not args.show, size=(700, 500))
        for i, alg in enumerate(algorithms):
            N = len(group_names)
            N1, N2 = i * N, (i + 1) * N
            for hist, name, col in zip(histograms[N1:N2], group_names, colours):
                c.plot(hist, linecolor=col, markercolor=col, markerstyle=4*i+20, linewidth=2, linestyle=i+1, label=name if i == 0 else None)
                pass
            pass

        c.text([signal_line(signal)]
               + (["%s particles" % t] if t != 'Signal' else []),
               qualifier=qualifier)
        c.legend(header=displayName('r') + " in:", categories=[(name, {'linestyle': i+1, 'markerstyle': 4*i+20, 'option': 'PL', 'linewidth': 2}) for i, name in enumerate(names)], width=0.28)
        c.xlabel("#LT#mu#GT")
        c.ylabel("Reconstruction efficiency")
        c.ylim(0, 1.8)

        # Show/save
        savename = '_'.join([signal] + histname.format(alg='', t=t, group='').split('/')[2:]) + '.pdf'
        if args.show: c.show()
        if args.save: c.save('plots/' + savename)
    

        # Efficiency of STD and LRT combined
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

        # Compute combined efficiency
        comb_histograms = list()
        for h1, h2 in zip(histograms[:len(groups)], histograms[len(groups):]):
            # h1: standard | h2: large radius
            ax = h1.GetXaxis()
            h_comb = h1.Clone('h_comb')#ROOT.TProfile('h_comb', "", ax.GetNbins(), ax.GetXmin(), ax.GetXmax())
            h_comb.Reset()
            for bin in range(1, h1.GetXaxis().GetNbins() + 1):
                N_total = int(h1.GetBinEntries(bin)) # == h2.GetBinEntries(bin)
                N_1 = int(h1.GetBinContent(bin) * N_total)
                N_2 = int(h2.GetBinContent(bin) * N_total)
                mu = h1.GetBinCenter(bin)
                N_pass = N_1 + N_2
                N_fail = N_total - N_pass
                for _ in xrange(N_pass): h_comb.Fill(mu, True)
                for _ in xrange(N_fail): h_comb.Fill(mu, False)
                pass
            comb_histograms.append(h_comb)
            pass


        # Draw figure
        c = ap.canvas(batch=not args.show, size=(700, 500))
        for ihist, (hist, name, col) in enumerate(zip(comb_histograms, group_names, colours)):
            c.plot(hist, linecolor=col, markercolor=col, markerstyle=20+ihist, linestyle=1+ihist, linewidth=2, label=name)
            pass

        c.text([signal_line(signal)]
               + (["%s particles" % t] if t != 'Signal' else [])
               + ["Large radius and standard tracks"],
               qualifier=qualifier)
        c.legend(header=displayName('r') + " in:", width=0.28)
        c.xlabel("#LT#mu#GT")
        c.ylabel("Reconstruction efficiency")
        c.ylim(0, 1.8)

        # Show/save
        savename = '_'.join([signal] + histname.format(alg='Combined', t=t, group='').split('/')[2:]) + '.pdf'
        if args.show: c.show()
        if args.save: c.save('plots/' + savename)
        pass

    return


if __name__ == '__main__':
    main()
    pass

