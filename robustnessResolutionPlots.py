#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Script for producing publication-ready robustness plots for the large-radius tracking (LRT) PUBNOTE.

Author: Andreas Sogaard (@asogaard)
Date:   8 June 2017
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

    # Macro-specific styles
    ROOT.gROOT.GetStyle("AStyle").SetEndErrorSize(.5)

    # Parse command-line arguments
    args = parser.parse_args()
    ap.canvas(batch=not args.show)

    # Initialise categories for which to plot distinct curves for each histogram
    algorithms = ['Standard', 'LargeD0']
    names      = ['Standard', 'Large radius']
    types      = ['Signal'] # ['All', 'Signal']
    signals = ['Rhadron'] # ['Rhadron', 'RPV']
    groups = [
        #'Rprod_0mm_1mm/',
        #'Rprod_1mm_3mm/',
        #'Rprod_3mm_10mm/',
        'Rprod_10mm_30mm/',
        'Rprod_30mm_100mm/',
        'Rprod_30mm_300mm/',
        #'Rprod_20mm_50mm/',
        #'Rprod_100mm_150mm/',
        #'Rprod_200mm_300mm/',
        #'',
              ]
    deps = ['mu', 'pt']

    group_names = [ '[%s]' % grp[6:-1].replace('_', ', ').replace('p', '.') for grp in groups ]
    # @TEMP: Fix type in histogram names: 30mm_300mm -> 100mm_300mm
    group_names = [gn.replace('30mm, 300mm', '100mm, 300mm') for gn in group_names]

    # Initialise variable versus which to plot the physics efficiency
    basic_vars = ['theta', 'phi', 'd0', 'z0', 'qOverP']

    # Initialise list of histograms to be plotted 
    base = 'IDPerformanceMon/LargeD0/'
    histname = base + 'ResolutionPlots/{alg}Tracks/{t}/{group}res{depdim}_{var}_vs_{dep}'

    # Accessor function to get the y-axis maximum
    def get_ymax (var):
        if var == 'theta':  return 0.01 * 1
        if var == 'phi':    return 0.01 * 1
        if var == 'd0':     return 1.0 * 1
        if var == 'z0':     return 2.0 * 1
        if var == 'qOverP': return 0.05 * 1
        return 0.01

    def get_ymax_comb (var):
        if var == 'theta':  return 0.008 * 1
        if var == 'phi':    return 0.007 * 1
        if var == 'd0':     return 1.2 # 0.8
        if var == 'z0':     return 1.2 * 1
        if var == 'qOverP': return 0.020
        return 0.01

    # Loop all combinations of track parameter, truth particle type, signal process, and dependency variable
    for var, t, signal, dep in itertools.product(basic_vars, types, signals, deps):

        # Open file from which to read histograms.
        f = ROOT.TFile(filename.format(signal=signal), 'READ')
        ROOT.TH1.AddDirectory(False)
        ROOT.TH2.AddDirectory(False)

        # Get list of histograms to plot, manually.
        histograms = list()
        comb_projs = dict()
        comb_xs = dict()
        comb_ws = dict()

        # Get histograms
        bin_pairs = list()
        bin_pairs_mu = list()
        for alg in algorithms:

            for igroup, group in enumerate(groups):

                h = f.Get(histname.format(alg=alg, var=var, t=t, group=group, dep=dep, depdim='2D' if dep == 'pt' else ''))
                if h is None:
                    pass
                try:
                    h.SetDirectory(0) # Keep in memory after file is closed.
                except AttributeError:
                    print "PROBLEM: '%s'" % histname.format(alg=alg, var=var, t=t, group=group, dep=dep, depdim='2D' if dep == 'pt' else '')
                    continue
                    pass

                xs, ys, xes, yes = list(), list(), list(), list()
                #rebin = ((igroup + 1)*2 if dep == 'pt' else 1)
                rebin = 1
                if dep == 'pt': # 36 bins total
                    rebins = [4,6,9,12] # [2, 4, 6]
                    rebin  = rebins[igroup]
                    pass
                
                # Allocate space if necessary
                if not (group in comb_projs):
                    comb_projs[group] = list()
                    comb_xs[group] = list()
                    comb_ws[group] = list()
                    pass

                # Dynamically choose binning
                if True and dep == 'pt' and len(bin_pairs) <= igroup:
                    nx, ny = h.GetXaxis().GetNbins(), h.GetYaxis().GetNbins()
                    if signal == 'Rhadron':
                        edges = np.logspace(np.log10(1), np.log10(50), 6 - 2 * igroup + 1, endpoint=True)
                    else:
                        edges = np.linspace(0, 400, 6 - 2 * igroup + 1, endpoint=True)
                        pass

                    bin_pairs.append(zip(edges[:-1], edges[1:]))
                    ax = h.GetXaxis()
                    bin_pairs[igroup] = [ (ax.FindBin(pair[0]), ax.FindBin(pair[1]) + 1) for pair in bin_pairs[igroup] ]
                    bin_pairs[igroup][-1] = (bin_pairs[igroup][-1][0], nx)
                    pass

                if True and dep == 'mu' and len(bin_pairs_mu) == 0:
                    bin_pairs_mu = [
                        (1,2),
                        (3,3),
                        (4,4),
                        (5,5),
                        (6,6),
                        (7,8),
                        ]
                    pass

                #for ibin in (xrange(h.GetXaxis().GetNbins() / rebin) if dep == 'mu' else range(len(bin_pairs[igroup]))):
                for ibin in (range(len(bin_pairs_mu)) if dep == 'mu' else range(len(bin_pairs[igroup]))):

                    # Get and fit projection
                    if dep == 'pt':# or True:
                        #proj = h.ProjectionY('_py', ibin * rebin + 1, ibin * rebin + (rebin - 1))
                        proj = h.ProjectionY('_py', *bin_pairs[igroup][ibin])
                    else:
                        #proj = h.ProjectionY('_py', ibin + 1, ibin + 1)
                        proj = h.ProjectionY('_py', *bin_pairs_mu[ibin])
                        pass

                    # Rebin
                    #proj.Rebin(5)
                    xmin, xmax = proj.GetXaxis().GetXmin(), proj.GetXaxis().GetXmax()
                    if dep == 'pt':
                        restrict = 3. # 3.
                    else:
                        restrict = 2.
                        pass
                    #proj.SetAxisRange(xmin / restrict, xmax / restrict)

                    # Get graph variables
                    if dep == 'pt':
                        #x = h.GetXaxis().GetBinUpEdge(ibin * rebin + rebin / 2)
                        #w = h.GetXaxis().GetBinWidth (ibin * rebin + 1) * rebin
                        x = 0.5 * (h.GetXaxis().GetBinCenter(bin_pairs[igroup][ibin][0]) + h.GetXaxis().GetBinCenter(bin_pairs[igroup][ibin][1]))
                        w = (h.GetXaxis().GetBinUpEdge(bin_pairs[igroup][ibin][1]) - h.GetXaxis().GetBinLowEdge(bin_pairs[igroup][ibin][0]))
                    else:
                        #x = h.GetXaxis().GetBinCenter(ibin + 1)
                        #w = h.GetXaxis().GetBinWidth (ibin + 1)
                        x = 0.5 * (h.GetXaxis().GetBinCenter(bin_pairs_mu[ibin][0]) + h.GetXaxis().GetBinCenter(bin_pairs_mu[ibin][1]))
                        w = (h.GetXaxis().GetBinUpEdge(bin_pairs_mu[ibin][1]) - h.GetXaxis().GetBinLowEdge(bin_pairs_mu[ibin][0]))
                        pass

                    # Add projection to list of combined projections (LRT + STD)
                    if len(comb_projs[group]) > ibin:
                        comb_projs[group][ibin].Add(proj)
                    else:
                        comb_projs[group].append(proj)
                        comb_xs[group].append(x)
                        comb_ws[group].append(w)
                        pass

                    # Get parameter RMS and assoc. error
                    ROOT.TH1.StatOverflows(False)
                    par, err = proj.GetStdDev(), proj.GetStdDevError()

                    sigma = 3

                    # Get "core" gausisan standard deviation and assoc. error
                    def getCoreStd (h, sigma=5):
                        rms   = h.GetRMS()
                        mean  = h.GetMean()
                        width = rms
                        fit = ROOT.TF1('fit', 'gaus(0)')# + pol0(3)')
                        fit.FixParameter(1, mean)
                        fit.SetParameter(2, rms / 4.) # * 0.5
                        h.Fit('fit', 'LRQ0')
                        """
                        it = 0
                        while abs(width - fit.GetParameter(2)) > 1E-03 * rms and it < 100:
                            it += 1
                            width = fit.GetParameter(2) 
                            fit.SetRange(mean - sigma * width, mean + sigma * width)
                            h.Fit('fit', 'LRQ0') # 'L...
                            pass
                            """
                        return fit.GetParameter(2), fit.GetParError(2)
                    
                    #par, err = getCoreStd(proj, sigma=sigma)

                    # Get "core" RMS and assoc. error
                    def getCoreRMS (h, sigma=5, fix_mean=None):
                        """ Method for getting the RMS in the central +/- sigma of a distribution. """

                        # Check(s)
                        # ...

                        # Book keeping
                        width     = 0          # RMS from pervious iteration
                        new_width = h.GetRMS() # RMS from current iteration
                        it = 0                 # Iteration counter, to avoid endless loop
                        xmin, xmax = h.GetXaxis().GetXmin(), h.GetXaxis().GetXmax() # Original axis limits

                        # Perform iterations
                        while abs(new_width - width) > 0 and it < 100:
                            # Initial conditions
                            if it == 0:
                                # Start inside-out, to minimise impact of outliers
                                rms = h.GetXaxis().GetBinWidth(1) * 4
                            else:
                                rms  = h.GetRMS()
                                pass
                            mean  = h.GetMean() if fix_mean is None else fix_mean

                            # Update axis limits
                            axmin = mean - sigma * rms
                            axmax = mean + sigma * rms
                            h.SetAxisRange(max(axmin,xmin), min(axmax,xmax))

                            # Update RMSs
                            width    = new_width
                            new_width = h.GetRMS()
                            it += 1
                            pass

                        # Store result before zooming out
                        result = h.GetRMS(), h.GetRMSError(), axmin, axmax

                        # Zooming back out
                        h.SetAxisRange(xmin, xmax)

                        # Return
                        return result
                    
                    #if dep == 'pt':
                    par, err, _, _ = getCoreRMS(proj, sigma=sigma, fix_mean=0)
                    #    pass

                    # FWHM
                    def getFWHM (h):
                        bin1 = proj.FindFirstBinAbove(proj.GetMaximum()/2)
                        bin2 = proj.FindLastBinAbove (proj.GetMaximum()/2)
                        par = proj.GetBinCenter(bin2) - proj.GetBinCenter(bin1)
                        err = np.sqrt( np.square(proj.GetBinWidth(bin1)/2.) + np.square(proj.GetBinWidth(bin2)/2.) )
                        return par, err

                    #par, err = getFWHM(h)

                    # Store data point
                    if par > 0.:
                        xs .append(x)
                        ys .append(par)
                        xes.append(w / 2.)
                        yes.append(err)
                        pass

                    # Save projections slices
                    c_proj = ap.canvas(batch=not args.show)
                    # @TODO: ZOOM OUT FROM RESTRICTED RANGE
                    rms2sig, err2sig, sigma2_min, sigma2_max = getCoreRMS(proj, sigma=2, fix_mean=0)
                    rms3sig, err3sig, sigma3_min, sigma3_max = getCoreRMS(proj, sigma=3, fix_mean=0)
                    c_proj.hist(proj)
                    c_proj.xline(sigma2_min, text='-2#sigma', linecolor=ROOT.kBlue)
                    c_proj.xline(sigma2_max, text='+2#sigma', linecolor=ROOT.kBlue)
                    c_proj.xline(sigma3_min, text='-3#sigma', linecolor=ROOT.kGreen)
                    c_proj.xline(sigma3_max, text='+3#sigma', linecolor=ROOT.kGreen)
                    c_proj.xlabel(displayNameUnit(var))
                    c_proj.ylabel("Tracks")
                    c_proj.text(["r_{prod} #in  " + group_names[igroup],
                                 signal_line(signal) + ' / ' + alg,
                                 ] +
                                (["p_{T} #in  [%.1f, %.1f] GeV" % (h.GetXaxis().GetBinLowEdge(bin_pairs[igroup][ibin][0]),
                                                                  h.GetXaxis().GetBinUpEdge(bin_pairs[igroup][ibin][1]))] if dep == 'pt' else ["#mu #in  [%d, %d]" % (h.GetXaxis().GetBinLowEdge(bin_pairs_mu[ibin][0]), h.GetXaxis().GetBinUpEdge(bin_pairs_mu[ibin][1]))]) + 
                                ["Tracks: %d (%d)" % (proj.Integral(), proj.Integral(0, proj.GetXaxis().GetNbins() + 1))],
                                qualifier="Simulation Internal")
                    
                    #proj.Draw("HIST")
                    if args.save: c_proj.save('plots/%s_RobustnessResolution_slice__%s_vs_%s__%s_%d_%d.pdf' % (signal, var, dep, alg, igroup, ibin))


                    pass

                # Create profile graph from points
                if len(xs) > 0:
                    graph = ROOT.TGraphErrors(len(xs), 
                                              array('d', xs),
                                              array('d', ys),
                                              array('d', xes),
                                              array('d', yes))
                else:
                    graph = ROOT.TGraphErrors()
                    pass
                histograms.append(graph)
                pass

            pass

        # Close file
        f.Close()


        # Profiles for STD and LRT separately
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        # Draw figure
        c = ap.canvas(batch=not args.show, size=(700, 500))
        for i, alg in enumerate(algorithms):
            N = len(group_names)
            N1, N2 = i * N, (i + 1) * N
            for hist, name, col in zip(histograms[N1:N2], group_names, colours):
                c.graph(hist, linecolor=col, markercolor=col, markerstyle=4*i+20, linewidth=2, linestyle=i+1, label=name if i == 0 else None)
                pass
            pass

        c.text([signal_line(signal)]
               + (["%s particles" % t] if t != 'Signal' else []),
               qualifier="Simulation Internal")
        c.legend(header="r_{prod} in:", categories=[(name, {'linestyle': i+1, 'markerstyle': 4*i+20, 'option': 'PL', 'linewidth': 2}) for i, name in enumerate(names)], width=0.28)
        if var == 'd0' and dep == 'pt':
            c.ylim(5E-03, 5E+00)
        elif var == 'qOverP' and dep == 'pt':
            c.ylim(5E-04, 5E-02)
        else:
            c.ylim(0, get_ymax(var) * (1.5 if dep == 'pt' else 1.0))
            pass
        if dep == 'pt':
            if signal == 'Rhadron': c.xlim(0,   50.)
            else:                   c.xlim(0, 400.)
            #c.logx()
        else:
            c.xlim(0,40.)
            pass
        c.xlabel(displayNameUnit(dep))
        c.ylabel('Residuals RMS, %s' % (displayNameUnit(var)))
        if dep == 'pt':
            c.logy()
            pass

        # Show/save
        savename = '_'.join([signal] + histname.format(alg='', var=var, t=t, group='', dep=dep, depdim='').split('/')[2:]) + '.pdf'
        if args.show: c.show()
        if args.save: c.save('plots/' + savename)


        # Profile for STD and LRT combined
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        # Compute combined plots.
        comb_histograms = list()
    
        for group in groups:# if signal == 'Rhadron' else groups[:-1]):
            projs = comb_projs[group]
            xs = comb_xs[group]
            ws = comb_ws[group]
            xes = [w/2. for w in ws]
            #ys, yes = zip(*[ (proj.GetRMS(), proj.GetRMSError()) for proj in projs ])
            ys, yes, _, _ = zip(*[ getCoreRMS(proj, sigma=sigma, fix_mean=0) for proj in projs ])

            graph = ROOT.TGraphErrors(len(xs), array('d', xs),
                                 array('d', ys),
                                 array('d', xes),
                                 array('d', yes))

            comb_histograms.append(graph)
            pass

         # Draw figure
        c = ap.canvas(batch=not args.show, size=(700, 500))
        for ihist, (hist, name, col) in enumerate(zip(comb_histograms, group_names, colours)):
            c.graph(hist, linecolor=col, markercolor=col, linewidth=2, markerstyle=20+ihist, linestyle=1+ihist, label=name)
            pass

        c.text([signal_line(signal),
                "Large radius and standard tracks"]
               + (["%s particles" % t] if t != 'Signal' else []),
               qualifier="Simulation Internal")
        c.legend(header="r_{prod} in:", width=0.28)
        if var == 'd0' and dep == 'pt':
            c.ylim(5E-03, 5E+00)
        elif var == 'qOverP' and dep == 'pt':
            c.ylim(5E-04, 5E-02)
        else:
            c.ylim(0, get_ymax_comb(var) * (1.5 if dep == 'pt' else 1.0))
            pass
        if dep == 'pt':
            if signal == 'Rhadron': c.xlim(0,  50.)
            else:                   c.xlim(0, 400.)
            #c.logx()
        else:
            c.xlim(0,40.)
            pass
        c.xlabel(displayNameUnit(dep))
        c.ylabel('Residuals RMS, %s' % (displayNameUnit(var)))
        if dep == 'pt':
            c.logy()
            pass

        # Show/save
        savename = '_'.join([signal] + histname.format(alg='Combined', var=var, t=t, group='', dep=dep, depdim='').split('/')[2:]) + '.pdf'
        if args.show: c.show()
        if args.save: c.save('plots/' + savename)

        pass

    return


if __name__ == '__main__':
    main()
    pass

