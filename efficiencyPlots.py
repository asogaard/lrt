#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" 
Script for producing publication-ready efficiency plots for the large-radius tracking (LRT) PUBNOTE.

Author: Andreas Sogaard (@asogaard)
Date:   7 June 2017
"""

# Basic
import itertools
from array import array

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

    # Initialise categories for which to plot distinct curved for each histogram
    algorithms = ['Standard', 'LargeD0']
    names      = ['Standard', 'Large radius', 'Combined']
    types   = ['', 'Primary', 'Secondary', 'Signal']
    signals = ['RPV', 'Rhadron']

    # Initialise variable versus which to plot the physics efficiency
    basic_vars = ['eta', 'phi', 'd0', 'z0', 'pt', 'R', 'Z', 'pt_low', 'pt_high']

    # Initialise list of histograms to be plotted 
    base = 'IDPerformanceMon/LargeD0/'
    histname = base + 'EffPlots/{alg}Tracks/{t}trackeff_vs_{var}'

    # Read in and plot each histogram
    for fn, var, t, signal in itertools.product([filename], basic_vars, types, signals):

        # Generate list of (path, histname) pairs to plot
        pathHistnamePairs = zip([fn.format(signal=signal)] * len(algorithms), [histname.format(t=t + ('/' if t != '' else ''), alg=alg, var=var) for alg in algorithms])

        # Load in histograms
        histograms = list()
        for path, hn in pathHistnamePairs:
            f = ROOT.TFile(path, 'READ')
            h = f.Get(hn)
            h.SetDirectory(0)
            if '_vs_R' in hn:
                if signal == 'Rhadron':
                    h.Rebin(2)
                else:
                    xbins = [0., 10., 20., 30., 40., 50., 70., 90., 110., 130., 150., 175., 200., 225., 250., 275., 300.]
                    h.Rebin(len(xbins)-1, 'hnew', array('d', xbins))
                    h = ROOT.gDirectory.Get('hnew')
                    h.SetDirectory(0)
                pass
            histograms.append(h)
            f.Close()
            pass

        # Compute combined efficiency
        h0 = histograms[0]
        h1 = histograms[1]
        ax = h0.GetXaxis()
        combined_eff = h0.Clone(h0.GetName() + '_comb') # ROOT.TProfile(h0.GetName() + '_comb', "", ax.GetNbins(), ax.GetXmin(), ax.GetXmax())
        combined_eff.Reset()
        for bin in range(1, ax.GetNbins() + 1):
            num_total = int(h0.GetBinEntries(bin))
            num_pass1 = int(h0.GetBinContent(bin) * num_total)
            num_pass2 = int(h1.GetBinContent(bin) * num_total)
            num_pass = num_pass1 + num_pass2
            num_fail = num_total - num_pass
            x = combined_eff.GetBinCenter(bin)
            for _ in range(num_pass): combined_eff.Fill(x, 1)
            for _ in range(num_fail): combined_eff.Fill(x, 0)
            pass
        histograms.append(combined_eff)

        # Draw figure
        c = ap.canvas(batch=not args.show, size=(700, 500))
        for ihist, (hist, name, col) in enumerate(zip(histograms, names, colours)):
            c.plot(hist, linecolor=col, markercolor=col, linestyle=1+ihist, markerstyle=20+ihist, label=name + (" tracks" if name != "Combined" else ""), legend_option='PL')
            pass
        c.text([signal_line(signal)],
               # + ([t + " particles"] if t != '' else []), 
               qualifier=qualifier)
        if ('Signal' in hn) and ('_vs_R' in hn):
            c.ylim(0, 1.6)
            pass
        c.xlabel(displayNameUnit(var)) # hist.GetXaxis().GetTitle().replace('prod.', 'prod'))
        c.ylabel("Reconstruction effiency")
        c.legend(width=0.28)

        # Radial locations of detector stuff
        if '_vs_R' in hn:
            """ Ugly vertical lines
            opts = {'linecolor': ROOT.kRed, 'linestyle': 3, 'text_horisontal': 'R', 'text_vertical': 'M'}
            c.xline( 33.25, **opts)
            c.xline( 50.5,  **opts)
            c.xline( 88.5,  **opts)
            c.xline(122.5,  **opts)

            opts['linecolor'] = ROOT.kBlue
            c.xline( 45.5, **opts)
            c.xline(242,   **opts)
            c.xline(255,   **opts)

            opts['linecolor'] = ROOT.kGreen
            c.xline( 229, **opts)
            """

            """ Pretty vertical lines
            opts = {'linecolor': ROOT.kRed, 'linestyle': 3, 'text_horisontal': 'R', 'text_vertical': 'M'}
            opts['linecolor'] = ROOT.kGray + 1
            c.xline( 33.25, text='IBL', **opts)
            c.xline( 50.5,  text='Pix. Layer 1', **opts)
            c.xline( 88.5,  text='Pix. Layer 2', **opts)
            if signal == 'Rhadron':
                opts['text_vertical'] = 'T'
                pass
            c.xline(122.5,  text='Pix. Layer 3', **opts)
            #c.xline(299.,   text='Layer 4', **opts)

            opts['linecolor'] = ROOT.kBlue
            opts['text_horisontal'] = 'L'
            opts['text_vertical'] = 'M'
            opts['linecolor'] = ROOT.kGray + 2
            c.xline( 45.5, text='Envelope 1', **opts)
            opts['text_vertical'] = 'T'
            c.xline(242,   text='Envelope 2', **opts)
            c.xline(255,   text='Envelope 3', **opts)

            opts['linecolor'] = ROOT.kGreen
            opts['linecolor'] = ROOT.kGray + 3
            c.xline( 229, text='Pixel tube', **opts)
            """

            #xlines = [33.25, 50.5, 88.5, 122.5, 299, # layers
            #          45.5, 242, 255, # envelopes
            #          ] 
            #c.xlines(xlines, linecolor=ROOT.kRed - 4)
            pass

        # Show/save
        savename = '_'.join([signal] + histname.format(t=t + ('/' if t != '' else ''), alg='', var=var).split('/')[2:]) + '.pdf'
        if args.show: c.show()
        if args.save: c.save('plots/' + savename)
        pass

    return


if __name__ == '__main__':
    main()
    pass
