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
from snippets.functions import displayNameUnit, displayName, displayUnit


# Get "core" std.dev. and assoc. error
def getCoreStd (h, sigma=5, fix_mean=None):
    """ Method for getting the std.dev. in the central +/- sigma of a distribution. """
    
    # Check(s)
    # ...
    
    # Book keeping
    old_std = 0          # RMS from pervious iteration
    std     = h.GetXaxis().GetBinWidth(1) * 2 # RMS from current iteration
    it = 0                 # Iteration counter, to avoid endless loop
    fit = ROOT.TF1('fit', 'gaus')
    mean  = h.GetMean() if fix_mean is None else fix_mean
    
    # Perform iterations
    while abs(std - old_std) > 0 and it < 100:
        
        # Update axis limits
        fit.SetRange(mean - sigma * std, mean + sigma * std)
        h.Fit('fit', 'QR0')
        
        # Update RMSs
        old_std  = std
        std      = fit.GetParameter(2)
        it += 1
        pass
    
    # Return
    return fit.GetParameter(2), fit.GetParError(2), fit
                        

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
    signals = ['Rhadron', 'RPV']

    groups = {
        'Rhadron': ['Rprod_10mm_30mm/',
                    'Rprod_30mm_100mm/',
                    'Rprod_100mm_300mm/',],
        'RPV':     ['Rprod_10mm_30mm/',
                    'Rprod_30mm_100mm/',
                    'Rprod_100mm_300mm/',],
        }

    ylabel = "Standard deviation of the error on %s"

    deps = ['mu', 'pt']
    
    group_names = {signal: [ '[%s]' % grp[6:-1].replace('_', ', ').replace('p', '.').replace('mm', ' mm') for grp in groups[signal] ] for signal in signals}
    
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


    # pT-binned RMS profiles
    # --------------------------------------------------------------------------

    histograms = dict()

    ptgroups = [
        'pT_1GeV_3GeV/',
        'pT_10GeV_30GeV/',
        ]

    ptgroup_names = [ '[%s]' % grp[3:-1].replace('_', ', ').replace('p', '.').replace('GeV', ' GeV') for grp in ptgroups ]

    f = ROOT.TFile(filename.format(signal='Rhadron'), 'READ')
    ROOT.TH2.AddDirectory(False)

    # Create canvas
    c      = ap.canvas(batch=not args.show, size=(700, 500))
    c_temp = ap.canvas(batch=True)

    # Loop Rprod bins
    for igroup, (group, groupname) in enumerate(zip(groups['Rhadron'], group_names['Rhadron'])):
        print group, '(%s)' % groupname

        # Loop pT bins
        for ipt, (ptgroup, ptgroupname) in enumerate(zip(ptgroups, ptgroup_names)):
            print "--", ptgroup, '(%s)' % ptgroup_names
            hist = None

            # Loop tracking algorithms; add 
            for alg in algorithms:
                hn = base + 'ResolutionPlots/{alg}Tracks/Signal/{group}{ptgroup}res_d0_vs_mu'.format(alg=alg, group=group, ptgroup=ptgroup)
                h = f.Get(hn)
                h.SetDirectory(0)
                if hist is None:
                    hist = h.Clone(h.GetName() + '_clone')
                else:
                    hist.Add(h)
                    pass
                pass

            # Define bin edges
            if igroup < 2:
                pairs = [
                    (1,2), #  5 - 10
                    (3,3), # 10 - 15
                    (4,4), # 15 - 20
                    (5,5), # 20 - 25
                    (6,6), # 25 - 30
                    (7,8), # 30 - 40
                    ]
            else:
                pairs = [
                    (1,3), #  0 - 15
                    (4,5), # 15 - 25
                    (6,8), # 25 - 40
                    ]
                pass

            # Initialise graph point lists
            xs, ys, xels, xehs, yes = list(), list(), list(), list(), list()
            
            # Loop edge pairs to get projection
            for ibin, pair in enumerate(pairs):
                
                # Get and fit projection
                proj = hist.ProjectionY('_py', *pair)
                ax = hist.GetXaxis()

                # Clean-up (?) -- overflow bins
                nx = proj.GetXaxis().GetNbins()
                proj.SetBinContent(0,      0)
                proj.SetBinContent(nx + 1, 0)
                
                # Rebin (?)
                #if igroup > 0:
                #    #proj.RebinX(2*igroup)
                #    pass
                
                # Get graph variables
                x  = 0.5 * (ax.GetBinCenter(pair[0]) + ax.GetBinCenter (pair[1]))
                wl =       (x - ax.GetBinLowEdge(pair[0]))
                wh =       (ax.GetBinUpEdge(pair[1]) - x)
                
                # Get parameter RMS and assoc. error
                ROOT.TH1.StatOverflows(False)
                
                # Set number of sigmas to use in core RMS calculation
                sigma = 3
                
                par, err, fit = getCoreStd(proj, sigma=sigma, fix_mean=0)
                par2p5, _, _  = getCoreStd(proj, sigma=2.5, fix_mean=0)
                par2p0, _, _  = getCoreStd(proj, sigma=2.0, fix_mean=0)
                
                syst = max(abs(par2p5 - par), abs(par2p0 - par))
        
                print "==> err:", err, "| syst:",syst
                err = np.sqrt( np.square(err) + np.square(syst) )
                
                # Store data point
                if par > 0.:
                    xs .append(x)
                    ys .append(par)
                    xels.append(wl)
                    xehs.append(wh)
                    yes.append(err)
                    pass


                # Projection slice
                c_proj = ap.canvas(batch=not args.show)
                rms2sig, err2sig, fit2 = getCoreStd(proj, sigma=2, fix_mean=0)
                rms3sig, err3sig, fit3 = getCoreStd(proj, sigma=3, fix_mean=0)
                c_proj.hist(proj)
                c_proj._bare().cd()
                fit2.SetLineColor(ROOT.kBlue)
                fit3.SetLineColor(ROOT.kGreen)
                c_proj.xline(-2 * rms2sig, text='-2#sigma', linecolor=ROOT.kBlue)
                c_proj.xline(+2 * rms2sig, text='+2#sigma', linecolor=ROOT.kBlue)
                c_proj.xline(-3 * rms3sig, text='-3#sigma', linecolor=ROOT.kGreen)
                c_proj.xline(+3 * rms3sig, text='+3#sigma', linecolor=ROOT.kGreen)
                fit2.Draw('SAME')
                fit3.Draw('SAME')
                c_proj.xlim(-8*rms3sig, +8*rms3sig)
                c_proj.xlabel(displayNameUnit('d0'))
                c_proj.ylabel("Tracks")
                c_proj.text([displayName('r')  + " #in  " + group_names['Rhadron'][igroup],
                             displayName('pt') + " #in  " + ptgroup_names[ipt],
                             signal_line('Rhadron') + ' / ' + 'Large radius and standard tracks',
                             ] +
                            ["%s #in  [%.1f, %.1f] %s" % (displayName('mu'), 
                                                          ax.GetBinLowEdge(pair[0]),
                                                          ax.GetBinUpEdge (pair[1]),
                                                          displayUnit('mu'))] +
                            ["Tracks: %d (%d)" % (proj.Integral(), proj.Integral(0, proj.GetXaxis().GetNbins() + 1))],
                            qualifier=qualifier)
                
                if args.save: c_proj.save('plots/%s_RobustnessResolution_slice__%s_vs_%s__%s_%s_%d_%d.pdf' % ('Signal', 'd0', 'mu', 'Both', ptgroup[:-1], igroup, ibin))
               
                               
                pass # end: loop bins

            graph = ROOT.TGraphAsymmErrors(len(xs), 
                                           array('d', xs),
                                           array('d', ys),
                                           array('d', xels),
                                           array('d', xehs),
                                           array('d', yes),
                                           array('d', yes))

            # Create x-axis for graph
            graph = c_temp.graph(graph)
            c_temp._bare().cd()
            ROOT.gPad.Update()

            # Draw graph with x-axis
            c.graph(graph, linecolor=colours[igroup], markercolor=colours[igroup], markerstyle=4*ipt+20, linewidth=2, linestyle=ipt+1, label=groupname if ipt == 0 else None)
     
            pass

        pass

    c.text([signal_line('Rhadron'),
            "Large radius and standard tracks"],
           qualifier=qualifier)
    c.legend(header=displayName('r') + " in:", width=0.28, ymax=0.872)
    c.legend(header=displayName('pt') + " in:", categories=[(name, {'linestyle': i+1, 'markerstyle': 4*i+20, 'option': 'PL', 'linewidth': 2}) for i, name in enumerate(ptgroup_names)], width=0.28, ymax=0.65)
    c.padding(0.65)
    c.logy()
    c.xlim(0, 40)
    
    c.xlabel(displayNameUnit('mu'))
    c.ylabel(ylabel % displayNameUnit('d0'))
    
    # Show/save
    savename='Rhadron_ResolutionPlots_BothTracks_Signal_res_d0_vs_mu_pTbinned.pdf'
    if args.show: c.show()
    if args.save: c.save('plots/' + savename)
    


    # Regular stuff
    # --------------------------------------------------------------------------
    
    # Loop all combinations of track parameter, truth particle type, signal process, and dependency variable
    for var, t, dep in itertools.product(basic_vars, types, deps):

        combined_graphs = {signal: list() for signal in signals}
        
        # Loop signal separately, in order to (optionally) compare the two
        for signal in signals:
            
            # Open file from which to read histograms.
            f = ROOT.TFile(filename.format(signal=signal), 'READ')
            ROOT.TH1.AddDirectory(False)
            ROOT.TH2.AddDirectory(False)
            
            # Get list of histograms to plot, manually.
            histograms = list()
            comb_projs = dict()
            comb_xs = dict()
            #comb_ws = dict()
            comb_wls = dict()
            comb_whs = dict()
            
            # Get histograms
            bin_pairs = {
                'pt': list(),
                'mu': list(),
                }
            
            for alg in algorithms:
                
                for igroup, group in enumerate(groups[signal]):
                    
                    h = f.Get(histname.format(alg=alg, var=var, t=t, group=group, dep=dep, depdim='2D' if dep == 'pt' else ''))
                    if h is None:
                        pass
                    try:
                        h.SetDirectory(0) # Keep in memory after file is closed.
                    except AttributeError:
                        print "PROBLEM: '%s'" % histname.format(alg=alg, var=var, t=t, group=group, dep=dep, depdim='2D' if dep == 'pt' else '')
                        continue
                    
                    #xs, ys, xes, yes = list(), list(), list(), list()
                    xs, ys, xels, xehs, yes = list(), list(), list(), list(), list()
                    
                    # Allocate space if necessary
                    if not (group in comb_projs):
                        comb_projs[group] = list()
                        comb_xs[group] = list()
                        comb_wls[group] = list()
                        comb_whs[group] = list()
                        pass
                    
                    # Dynamically choose binning
                    if dep == 'pt' and  len(bin_pairs['pt']) <= igroup:
                        nx, ny = h.GetXaxis().GetNbins(), h.GetYaxis().GetNbins()
                        if signal == 'Rhadron':
                            edges = np.logspace(np.log10(1), np.log10(50), 8 - 2 * igroup + 1, endpoint=True)
                        else:
                            edges = np.linspace(0, 400, max(8 - 4 * igroup + 1, 2), endpoint=True)
                            #edges -= 0.2 # @TEMP: FIX FOR NICE BIN EDGES
                            edges[0] = 1
                            pass
           
                        bin_pairs['pt'].append(zip(edges[:-1], edges[1:]))
                        ax = h.GetXaxis()
                        bin_pairs['pt'][igroup] = [ (ax.FindBin(pair[0]), ax.FindBin(pair[1])) for pair in bin_pairs['pt'][igroup] ]
                        
                        # Ensure there is no overlap between bins
                        for idx in range(len(bin_pairs['pt'][igroup]) - 1):
                            if bin_pairs['pt'][igroup][idx][1] >= bin_pairs['pt'][igroup][idx+1][0]:
                                bin_pairs['pt'][igroup][idx+1] = (bin_pairs['pt'][igroup][idx][1]+1, bin_pairs['pt'][igroup][idx+1][1])
                                pass
                            pass

                        if signal == 'RPV':
                            bin_pairs['pt'][igroup][-1] = (bin_pairs['pt'][igroup][-1][0], nx)
                            pass
                        pass
                    
                    if dep == 'mu' and len(bin_pairs['mu']) <= igroup:
                        if igroup < 2:
                            pairs = [
                                (1,2), #  5 - 10
                                (3,3), # 10 - 15
                                (4,4), # 15 - 20
                                (5,5), # 20 - 25
                                (6,6), # 25 - 30
                                (7,8), # 30 - 40
                                ]
                        else:
                            pairs = [
                                (1,3), #  0 - 15
                                (4,5), # 15 - 25
                                (6,8), # 25 - 40
                                ]
                            pass
                        
                        bin_pairs['mu'].append( pairs )
                        pass
                    
                    # Loop x-axis bins in 2D histogram
                    for ibin in range(len(bin_pairs[dep][igroup])):
                        
                        pair = bin_pairs[dep][igroup][ibin]
                        ax = h.GetXaxis()
                        
                        # Get and fit projection
                        proj = h.ProjectionY('_py', *pair)
                        
                        # Clean-up (?)
                        if dep == 'mu':
                            # If highest bin content is larger than the average bin content in the remaining bins, remove it
                            nx = proj.GetXaxis().GetNbins()
                            proj.SetBinContent(0,      0)
                            proj.SetBinContent(nx + 1, 0)
                            pass
                        
                        # Rebin (?)
                        if dep == 'mu' and igroup > 0:
                            proj.RebinX(2*igroup)
                            pass
                        
                        # Get graph variables
                        x  = 0.5 * (ax.GetBinCenter(pair[0]) + ax.GetBinCenter (pair[1]))
                        wl =       (x - ax.GetBinLowEdge(pair[0]))
                        wh =       (ax.GetBinUpEdge(pair[1]) - x)
                        
                        # Add projection to list of combined projections (LRT + STD)
                        if len(comb_projs[group]) > ibin:
                            comb_projs[group][ibin].Add(proj)
                        else:
                            comb_projs[group].append(proj)
                            comb_xs[group].append(x)
                            comb_wls[group].append(wl)
                            comb_whs[group].append(wh)
                            pass
                        
                        # Get parameter RMS and assoc. error
                        ROOT.TH1.StatOverflows(False)
                        
                        # Set number of sigmas to use in core RMS calculation
                        sigma = 3
                        
                        par, err, fit = getCoreStd(proj, sigma=sigma, fix_mean=0)
                        par2p5, _, _  = getCoreStd(proj, sigma=2.5, fix_mean=0)
                        par2p0, _, _  = getCoreStd(proj, sigma=2.0, fix_mean=0)

                        syst = max(abs(par2p5 - par), abs(par2p0 - par))

                        if var == 'd0' and dep == 'mu':
                            print "==> err, syst:", err, syst
                            pass
                        err = np.sqrt( np.square(err) + np.square(syst) )

                        # Store data point
                        if par > 0.:
                            xs .append(x)
                            ys .append(par)
                            xels.append(wl / 2.)
                            xehs.append(wh / 2.)
                            yes.append(err)
                            pass
                        
                        # Easy access
                        ax  = h.GetXaxis()
                        pair = bin_pairs[dep][igroup][ibin]
                        
                        # Save projections slices
                        '''
                        c_proj = ap.canvas(batch=not args.show)
                        #rms2sig, err2sig, sigma2_min, sigma2_max = getCoreRMS(proj, sigma=2, fix_mean=0)
                        #rms3sig, err3sig, sigma3_min, sigma3_max = getCoreRMS(proj, sigma=3, fix_mean=0)
                        rms2sig, err2sig, fit2 = getCoreStd(proj, sigma=2, fix_mean=0)
                        rms3sig, err3sig, fit3 = getCoreStd(proj, sigma=3, fix_mean=0)
                        #fit.SetRange(-3*rms3sig,3*rms3sig)
                        c_proj.hist(proj)
                        c_proj._bare().cd()
                        fit2.SetLineColor(ROOT.kBlue)
                        fit3.SetLineColor(ROOT.kGreen)
                        c_proj.xline(-2 * rms2sig, text='-2#sigma', linecolor=ROOT.kBlue)
                        c_proj.xline(+2 * rms2sig, text='+2#sigma', linecolor=ROOT.kBlue)
                        c_proj.xline(-3 * rms3sig, text='-3#sigma', linecolor=ROOT.kGreen)
                        c_proj.xline(+3 * rms3sig, text='+3#sigma', linecolor=ROOT.kGreen)
                        fit2.Draw('SAME')
                        fit3.Draw('SAME')
                        c_proj.xlim(-8*rms3sig, +8*rms3sig)
                        c_proj.xlabel(displayNameUnit(var))
                        c_proj.ylabel("Tracks")
                        c_proj.text([displayName('r') + " #in  " + group_names[signal][igroup],
                                     signal_line(signal) + ' / ' + alg,
                                     ] +
                                    ["%s #in  [%.1f, %.1f] %s" % (displayName(dep), 
                                                                  ax.GetBinLowEdge(pair[0]),
                                                                  ax.GetBinUpEdge (pair[1]),
                                                                  displayUnit(dep))] +
                                    ["Tracks: %d (%d)" % (proj.Integral(), proj.Integral(0, proj.GetXaxis().GetNbins() + 1))],
                                    qualifier=qualifier)
                        
                        if args.save: c_proj.save('plots/%s_RobustnessResolution_slice__%s_vs_%s__%s_%d_%d.pdf' % (signal, var, dep, alg, igroup, ibin))
                        '''
                        pass
                    
                    # Create profile graph from points
                    if len(xs) > 0:
                        graph = ROOT.TGraphAsymmErrors(len(xs), 
                                                       array('d', xs),
                                                       array('d', ys),
                                                       array('d', xels),
                                                       array('d', xehs),
                                                       array('d', yes),
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
            c_temp = ap.canvas(batch=True)
            for i, alg in enumerate(algorithms):
                N = len(group_names[signal])
                N1, N2 = i * N, (i + 1) * N
                for hist, name, col in zip(histograms[N1:N2], group_names[signal], colours):
                    # Create x-axis for graph
                    hist = c_temp.graph(hist)
                    c_temp._bare().cd()
                    ROOT.gPad.Update()
                    # Draw graph with x-axis
                    c.graph(hist, linecolor=col, markercolor=col, markerstyle=4*i+20, linewidth=2, linestyle=i+1, label=name if i == 0 else None)
                    pass
                pass
            
            c.text([signal_line(signal)]
                   + (["%s particles" % t] if t != 'Signal' else []),
                   qualifier=qualifier)
            c.legend(header=displayName('r') + " in:", categories=[(name, {'linestyle': i+1, 'markerstyle': 4*i+20, 'option': 'PL', 'linewidth': 2}) for i, name in enumerate(names)], width=0.28)
            c.padding(0.50)
            c.xlim(h.GetXaxis().GetBinLowEdge(bin_pairs[dep][0] [0][0]),
                   h.GetXaxis().GetBinUpEdge (bin_pairs[dep][0][-1][1]))
            
            c.xlabel(displayNameUnit(dep))
            c.ylabel(ylabel % displayNameUnit(var))
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
            
            for igroup, (group, name) in enumerate(zip(groups[signal], group_names[signal])):# if signal == 'Rhadron' else groups[:-1]):
                projs = comb_projs[group]
                xs = comb_xs[group]
                wls = comb_wls[group]
                whs = comb_whs[group]
                xels = [w for w in wls]
                xehs = [w for w in whs]
                ys, yes, _ = zip(*[ getCoreStd(proj, sigma=sigma, fix_mean=0) for proj in projs ])

                ys2p5, _, _  = zip(*[ getCoreStd(proj, sigma=2.5, fix_mean=0) for proj in projs ])
                ys2p0, _, _  = zip(*[ getCoreStd(proj, sigma=2.0, fix_mean=0) for proj in projs ])

                syst = np.maximum(np.abs(np.array(ys2p5) - np.array(ys)), np.abs(np.array(ys2p0) - np.array(ys)))
                yes = np.sqrt( np.square(np.array(yes)) + np.square(syst) )

                graph = ROOT.TGraphAsymmErrors(len(xs), 
                                               array('d', xs),
                                               array('d', ys),
                                               array('d', xels),
                                               array('d', xehs),
                                               array('d', yes),
                                               array('d', yes))
                
                combined_graphs[signal].append((name, graph))
                comb_histograms.append(graph)

                # Draw projection slice
                '''
                #for ibin, (proj, x, w) in enumerate(zip(projs, xs, ws)):
                for ibin, (proj, x, wl, wh) in enumerate(zip(projs, xs, wls, whs)):
                    c_proj = ap.canvas(batch=not args.show)
                    #rms2sig, err2sig, sigma2_min, sigma2_max = getCoreRMS(proj, sigma=2, fix_mean=0)
                    #rms3sig, err3sig, sigma3_min, sigma3_max = getCoreRMS(proj, sigma=3, fix_mean=0)
                    rms2sig, err2sig, fit2  = getCoreStd(proj, sigma=2, fix_mean=0)
                    rms3sig, err3sig, fit3 = getCoreStd(proj, sigma=3, fix_mean=0)
                    c_proj.hist(proj)
                    c_proj._bare().cd()
                    #fit.SetRange(-3*rms3sig,3*rms3sig)
                    fit2.SetLineColor(ROOT.kBlue)
                    fit3.SetLineColor(ROOT.kGreen)
                    #c_proj.xline(sigma2_min, text='-2#sigma', linecolor=ROOT.kBlue)
                    #c_proj.xline(sigma2_max, text='+2#sigma', linecolor=ROOT.kBlue)
                    #c_proj.xline(sigma3_min, text='-3#sigma', linecolor=ROOT.kGreen)
                    #c_proj.xline(sigma3_max, text='+3#sigma', linecolor=ROOT.kGreen)
                    c_proj.xline(-2 * rms2sig, text='-2#sigma', linecolor=ROOT.kBlue)
                    c_proj.xline(+2 * rms2sig, text='+2#sigma', linecolor=ROOT.kBlue)
                    c_proj.xline(-3 * rms3sig, text='-3#sigma', linecolor=ROOT.kGreen)
                    c_proj.xline(+3 * rms3sig, text='+3#sigma', linecolor=ROOT.kGreen)
                    fit2.Draw('SAME')
                    fit3.Draw('SAME')
                    c_proj.xlabel(displayNameUnit(var))
                    c_proj.ylabel("Tracks")
                    c_proj.xlim(-8*rms3sig, +8*rms3sig)
                    c_proj.text([displayName('r') + " #in  " + group_names[signal][igroup],
                                 signal_line(signal) + ' / Combined LRT and standard',
                                 ] +
                                ["%s #in  [%.1f, %.1f] %s" % (displayName(dep), 
                                                              #x - w/2.,
                                                              #x + w/2.,
                                                              x - wl,
                                                              x + wh,
                                                              displayUnit(dep))] +
                                ["Tracks: %d (%d)" % (proj.Integral(), proj.Integral(0, proj.GetXaxis().GetNbins() + 1))],
                                qualifier=qualifier)
                    
                    if args.save: c_proj.save('plots/%s_RobustnessResolution_slice__%s_vs_%s__%s_%d_%d.pdf' % (signal, var, dep, 'Combined', igroup, ibin))
                    pass
                    '''
                pass
            
            # Draw figure
            c = ap.canvas(batch=not args.show, size=(700, 500))
            for ihist, (hist, name, col) in enumerate(zip(comb_histograms, group_names[signal], colours)):
                c.graph(hist, linecolor=col, markercolor=col, linewidth=2, markerstyle=20+ihist, linestyle=1+ihist, label=name)
                pass
            
            c.text([signal_line(signal),
                    "Large radius and standard tracks"]
                   + (["%s particles" % t] if t != 'Signal' else []),
                   qualifier=qualifier)
            c.legend(header=displayName('r') + " in:", width=0.28)
            if dep == 'pt':
                c.padding(0.50)
            else:
                c.padding(0.60)
                pass
            c.xlim(h.GetXaxis().GetBinLowEdge(bin_pairs[dep][0] [0][0]),
                   h.GetXaxis().GetBinUpEdge (bin_pairs[dep][0][-1][1]))

            c.xlabel(displayNameUnit(dep))
            c.ylabel(ylabel % displayNameUnit(var))
            if dep == 'pt':
                c.logy()
                pass
            
            # Show/save
            savename = '_'.join([signal] + histname.format(alg='Combined', var=var, t=t, group='', dep=dep, depdim='').split('/')[2:]) + '.pdf'
            if args.show: c.show()
            if args.save: c.save('plots/' + savename)
            
            pass # end: loop signals


        # Profile for STD and LRT combined for both Rhadron and RPV
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        c = ap.canvas(batch=not args.show, size=(700, 500))
        for i, signal in enumerate(reversed(signals)):
            for (name, graph), col in zip(combined_graphs[signal], colours):
                c.graph(graph, linecolor=col, markercolor=col, linewidth=2, markerstyle=24-4*i, linestyle=2-i, label=name if i == 1 else None, legend_option='L')
                pass
            pass
        
        c.text(["Large radius and standard tracks"],
               qualifier=qualifier)
        c.legend(header=displayName('r') + " in:", width=0.28, categories=[
                (signal_line(signal), {'linestyle': 2-i, 'markerstyle': 24-4*i, 'option': 'PL'}) for i, signal in enumerate(reversed(signals))
                ])
        if dep == 'pt':
            c.padding(0.35)
        else:
            c.padding(0.45)
            pass

        if dep == 'pt':
            c.xlim(1., 400.)
        else:
            c.xlim(0.,  40.)
            pass
        c.xlabel(displayNameUnit(dep))
        c.ylabel(ylabel % displayNameUnit(var))
        if dep == 'pt':
            c.logy()
            c.logx()
            pass
        
        # Show/save
        savename = '_'.join(['Both'] + histname.format(alg='Combined', var=var, t=t, group='', dep=dep, depdim='').split('/')[2:]) + '.pdf'
        if args.show: c.show()
        if args.save: c.save('plots/' + savename)

        pass # end: loop basic_vars, types, deps
    
    return


if __name__ == '__main__':
    main()
    pass

