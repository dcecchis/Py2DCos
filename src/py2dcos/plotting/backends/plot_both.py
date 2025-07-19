from __future__ import annotations
from typing import TYPE_CHECKING
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from scipy.interpolate import RegularGridInterpolator
from py2dcos.plotting.backends.locator import define_locator
from py2dcos.config.resources import PeaksSigns
from py2dcos.config.resources import AxisDirection
from py2dcos.config.resources import Diagonal
from py2dcos.config.resources import CANVAS_BACKGROUND
from py2dcos.types.plot_settings import PlotSettings

if TYPE_CHECKING:
    from py2dcos.core.math.correlation_model import CorrelationModel
    from matplotlib.figure import Figure

def plot_both2d(
        model: CorrelationModel,
        settings: PlotSettings,
        *,
        figure: Figure | None = None) -> Figure:
            

        fig = figure or plt.figure()
        fig.clf()
        fig.set_facecolor(CANVAS_BACKGROUND)

        # define default line width and font size for consistency
        linewidth, fontsize = 0.9, 8

        # choose locator for contour levels based on settings
        locator = define_locator(settings.locator, settings.num_contours)

        # copy sync and async arrays for peak filtering
        sync = model.syncr.values.copy()
        async_ = model.asyncr.values.copy()

        
        # apply peak-sign mask if user requested only pos or neg peaks
        def mask(data: np.ndarray) -> np.ndarray:
            if settings.peaks is PeaksSigns.POSITIVE:
                return np.where(data > 0, data, np.nan)
            if settings.peaks is PeaksSigns.NEGATIVE:
                return np.where(data < 0, data, np.nan)
            return data

        sync = mask(sync)
        async_ = mask(async_)

        # compute separate color scale limits for sync and async
        smin, smax = np.nanmin(sync), np.nanmax(sync)
        amin, amax = np.nanmin(async_), np.nanmax(async_)

        # prepare interpolators for interactive coordinate readout
        fmt_s = RegularGridInterpolator((model.syncr.index, model.syncr.columns), model.syncr.values)
        fmt_a = RegularGridInterpolator((model.asyncr.index, model.asyncr.columns), model.asyncr.values)
        def fmt1(x, y):
            z = np.take(fmt_s((x, y)), 0)
            return 'x={x:.2f}  y={y:.2f}  z={z:.5f}'.format(x=x, y=y, z=z)
        def fmt2(x, y):
            z = -np.take(fmt_a((x, y)), 0)
            return 'x={x:.2f}  y={y:.2f}  z={z:.5f}'.format(x=x, y=y, z=z)

        # define grid spec layout: margin panels, central maps, and colorbars
        gs = mpl.gridspec.GridSpec(
            5, 4,
            width_ratios=[2, 7, 0.2, 7],
            height_ratios=[0.4, 0.75, 2, 7, 2],
            wspace=0, hspace=0
        )

        # create axes for each panel and share axes for alignment
        ax = dict(
            sync    = fig.add_subplot(gs[3, 1]),
            async_  = fig.add_subplot(gs[3, 3]),
            upper   = fig.add_subplot(gs[2, 1]),
            upper_r = fig.add_subplot(gs[2, 3]),
            lefter  = fig.add_subplot(gs[3, 0]),
            lower   = fig.add_subplot(gs[4, 1]),
            lower_r = fig.add_subplot(gs[4, 3]),
        )
        # share x or y axes where appropriate to align panels
        ax['upper'].sharex(ax['sync'])
        ax['upper_r'].sharex(ax['async_'])
        ax['lefter'].sharey(ax['sync'])
        ax['lower'].sharex(ax['sync'])
        ax['lower_r'].sharex(ax['async_'])
        ax['async_'].sharex(ax['sync'])
        ax['async_'].sharey(ax['sync'])

        # configure tick parameters: hide ticks on secondary panels
        for panel in ax.values():
            panel.tick_params(
                axis='both', which='both', direction='out',
                bottom=False, top=False, left=False, right=False,
                labelbottom=False, labelleft=False,
                labeltop=False, labelright=False,
                length=4
            )
        # enable ticks and labels on margin panels for context
        ax['lefter'].tick_params(axis='x', which='both', top=True, labeltop=True)
        ax['lefter'].tick_params(axis='y', which='both', left=True, labelleft=True)
        ax['upper'].tick_params(axis='x', which='both', top=True, labeltop=True)
        ax['upper'].tick_params(axis='y', which='both', left=True, labelleft=True)
        ax['upper_r'].tick_params(axis='x', which='both', top=True, labeltop=True)
        ax['upper_r'].tick_params(axis='y', which='both', right=True, labelright=True)
        ax['lower'].tick_params(axis='x', which='both', bottom=True, labelbottom=True)
        ax['lower'].tick_params(axis='y', which='both', left=True, labelleft=True)
        ax['lower_r'].tick_params(axis='x', which='both', bottom=True, labelbottom=True)
        ax['lower_r'].tick_params(axis='y', which='both', right=True, labelright=True)
        ax['async_'].tick_params(axis='y', which='both', right=True, labelright=True)

        # plot reference statistics on upper panels for sync and async
        x1 = model.describe1.index
        d1 = model.describe1
        for subplot in (ax['upper'], ax['upper_r']):
            subplot.plot(x1, model.first1, 'r-', label="First", linewidth=linewidth)
            subplot.plot(x1, d1['mean'], label="Mean", linewidth=linewidth)
            subplot.fill_between(x1, d1['min'], d1['max'], alpha=0.3)
            subplot.plot(x1, model.last1, 'k-', label="Last", linewidth=linewidth)
            subplot.set_xlim(x1.min(), x1.max())
            subplot.legend(fontsize=fontsize)

        # plot reference statistics on lefter panel (rotated orientation)
        y1 = model.describe2.index
        d2 = model.describe2
        ax['lefter'].plot(model.first2, y1, 'r-', label="First", linewidth=linewidth)
        ax['lefter'].plot(d2['mean'], y1, label="Mean", linewidth=linewidth)
        ax['lefter'].fill_betweenx(y1, d2['min'], d2['max'], alpha=0.3)
        ax['lefter'].plot(model.last2, y1, 'k-', label="Last", linewidth=linewidth)
        ax['lefter'].set_ylim(y1.min(), y1.max())
        ax['lefter'].legend(fontsize=fontsize)

        # initial plot of main diagonal in lower panel for sync before heatmaps
        xi, yi = model.syncr.index, model.syncr.columns
        ax['lower'].plot(xi, sync.diagonal(0)[::-1], linewidth=linewidth)
        ax['lower'].axhline(0, color='k', alpha=0.4)
        ax['lower'].set_xlim(xi.min(), xi.max())

        # draw heatmap and contour for synchronous map
        im_s = ax['sync'].imshow(
            sync[::-1, :], cmap=settings.color_map,
            vmin=smin, vmax=smax,
            alpha=settings.color_map_intensity,
            aspect="auto",
            extent=(xi[0], xi[-1], yi[0], yi[-1]),
        )
        ax['sync'].contour(
            xi, yi, sync, locator=locator,
            vmin=smin, vmax=smax,
            colors=settings.contour_line_color,
            alpha=settings.contour_line_alpha,
            linewidths=linewidth,
        )

        # draw heatmap and contour for asynchronous map
        im_a = ax['async_'].imshow(
            async_[::-1, :], cmap=settings.color_map,
            vmin=amin, vmax=amax,
            alpha=settings.color_map_intensity,
            aspect="auto",
            extent=(xi[0], xi[-1], yi[0], yi[-1]),
        )
        ax['async_'].contour(
            xi, yi, async_, locator=locator,
            vmin=amin, vmax=amax,
            colors=settings.contour_line_color,
            alpha=settings.contour_line_alpha,
            linewidths=linewidth,
        )

        # add horizontal colorbars above each heatmap for scale reference
        cax_sync  = fig.add_subplot(gs[0, 1])
        cax_async = fig.add_subplot(gs[0, 3])
        cbar_sync  = fig.colorbar(im_s,  cax=cax_sync,  orientation='horizontal')
        cbar_async = fig.colorbar(im_a,  cax=cax_async, orientation='horizontal')
        for cb in (cbar_sync, cbar_async):
            cb.ax.tick_params(
                axis='x', which='both', direction='out',
                length=4, top=True, bottom=False,
                labeltop=True, labelbottom=False
            )

        # overlay main or anti diagonal on sync map and plot it below
        if settings.sync_diag is Diagonal.MAIN:
            diag_s = sync.diagonal(0)
            ax['sync'].plot(xi, yi, color='k', alpha=0.65, linewidth=linewidth)
        else:
            diag_s = np.fliplr(sync).diagonal(0)
            ax['sync'].plot(xi, yi[::-1], color='k', alpha=0.65, linewidth=linewidth)
        ax['lower'].clear()
        ax['lower'].plot(xi, diag_s, linewidth=linewidth)
        ax['lower'].axhline(0, color='k', alpha=0.4)

        # overlay main or anti diagonal on async map and plot it below
        if settings.async_diag is Diagonal.MAIN:
            diag_a = async_.diagonal(0)
            ax['async_'].plot(xi, yi, color='k', alpha=0.65, linewidth=linewidth)
        else:
            diag_a = np.fliplr(async_).diagonal(0)
            ax['async_'].plot(xi, yi[::-1], color='k', alpha=0.65, linewidth=linewidth)
        ax['lower_r'].clear()
        ax['lower_r'].plot(xi, diag_a, linewidth=linewidth)
        ax['lower_r'].axhline(0, color='k', alpha=0.4)

        # set axis limits and apply x-axis inversion if requested
        for key in ('sync', 'async_'):
            ax[key].set_xlim(xi.min(), xi.max())
            ax[key].set_ylim(yi.min(), yi.max())
            if settings.x_axis is AxisDirection.DECREASING:
                ax[key].invert_xaxis()

        # enable interactive coordinate display on panels
        ax['sync'].format_coord  = fmt1
        ax['async_'].format_coord = fmt2

        return fig
