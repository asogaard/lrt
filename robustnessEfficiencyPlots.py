#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Script for producing publication-ready efficiency robustness plots for the large-radius tracking (LRT) PUBNOTE.

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


# Main function definition.
def main ():

    # Macro-specific styles
    ROOT.gROOT.GetStyle("AStyle").SetEndErrorSize(5.)

    # Parse command-line arguments
    args = parser.parse_args()

    # Initialise categories for which to plot distinct curves for each histogram
    algorithms = ['Standard', 'LargeD0']
    names      = ['Standard', 'Large-radius']
    types      = ['Signal'] # ['All', 'Signal']
    signals = ['RPV', 'Rhadron']
    groups = ['R20mm_50mm/',
              'R100mm_150mm/',
              'R200mm_300mm/',
              ]

    group_names = [ '[%s]' % grp[1:-1].replace('_', ', ').replace('p', '.') for grp in groups ]

    # Initialise list of histograms to be plotted 
    base = 'IDPerformanceMon/LargeD0/'
    histname = base + 'EffPlots/{alg}Tracks/{t}/{group}trackeff_vs_mu'

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
                h.RebinX(2)
                histograms.append(h)
                pass
            pass
        
        # Close file
        f.Close()


        # Efficiency of STD and LRT separately
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

        # Draw figure
        c = ap.canvas(batch=not args.show)
        for i, alg in enumerate(algorithms):
            N = len(group_names)
            N1, N2 = i * N, (i + 1) * N
            for hist, name, col in zip(histograms[N1:N2], group_names, colours):
                c.plot(hist, linecolor=col, markercolor=col, markerstyle=4*i+20, linewidth=2, linestyle=i+1, label=name if i == 0 else None, legend_option='L')
                pass
            pass

        c.text([signal_line(signal),
                "Fiducial selection applied",
                ] + (["%s particles" % t] if t != 'Signal' else []),
               qualifier="Simulation Internal")
        c.legend(header="R_{prod.} in:", categories=[(name, {'linestyle': i+1, 'markerstyle': 4*i+20, 'option': 'PL', 'linewidth': 2}) for i, name in enumerate(names)])
        c.xlabel("#mu")
        c.ylabel("Inclusive reconstruction efficiency")
        c.padding(0.55)

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
            h_comb = ROOT.TProfile('h_comb', "", ax.GetNbins(), ax.GetXmin(), ax.GetXmax())
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
        c = ap.canvas(batch=not args.show)
        for hist, name, col in zip(comb_histograms, group_names, colours):
            c.plot(hist, linecolor=col, markercolor=col, markerstyle=20, linewidth=2, label=name, legend_option='L')
            pass

        c.text([signal_line(signal),
                "Fiducial selection applied",
                ] + (["%s particles" % t] if t != 'Signal' else [])
               + ["All tracks"],
               qualifier="Simulation Internal")
        c.legend(header="R_{prod.} in:")
        c.xlabel("#mu")
        c.ylabel("Inclusive reconstruction efficiency")
        c.padding(0.5)

        # Show/save
        savename = '_'.join([signal] + histname.format(alg='Combined', t=t, group='').split('/')[2:]) + '.pdf'
        if args.show: c.show()
        if args.save: c.save('plots/' + savename)
        pass

    return


if __name__ == '__main__':
    main()
    pass

