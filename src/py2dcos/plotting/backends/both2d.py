from __future__ import annotations
from typing import TYPE_CHECKING

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from scipy.interpolate import RegularGridInterpolator

from py2dcos.core.locator import define_locator
from py2dcos.plotting.backends.base import PlotBase
from py2dcos.plotting.settings import PlotSettings, Peaks
from py2dcos.config.resources import PeaksSigns

if TYPE_CHECKING:
    from py2dcos.core.correlation_model import CorrelationModel


class Both2DPlot(PlotBase):
    """
    Side-by-side synchronous (left) + asynchronous (right) 2-D maps
    with shared reference spectra panels.
    """

    def draw(
        self,
        model: "CorrelationModel",
        settings: PlotSettings,
    ) -> plt.Figure:
        fig = self.figure
        fig.set_facecolor("#f0f0f0")

        linewidth, fontsize = 0.9, 8
        locator = define_locator(settings.locator, settings.num_contours)

        # ───────────────────────────────
        # Prepare sync / async matrices
        # ───────────────────────────────
        sync = model.syncr.values.copy()
        async_ = model.asyncr.values.copy()

        def mask(data: np.ndarray) -> np.ndarray:
            if settings.peaks is PeaksSigns.POSITIVE:
                return np.where(data > 0, data, np.nan)
            if settings.peaks is PeaksSigns.NEGATIVE:
                return np.where(data < 0, data, np.nan)
            return data

        sync = mask(sync)
        async_ = mask(async_)

        # colour-scale ranges (independent)
        smin, smax = np.nanmin(sync),   np.nanmax(sync)
        amin, amax = np.nanmin(async_), np.nanmax(async_)

        # Interpolators for coordinate read-out
        fmt_s = RegularGridInterpolator(
            (model.syncr.index, model.syncr.columns), model.syncr.values)
        fmt_a = RegularGridInterpolator(
            (model.asyncr.index, model.asyncr.columns), model.asyncr.values)
        
        def fmt1(x, y):
            z = np.take(fmt_s((x, y)), 0)
            return 'x={x:.2f}  y={y:.2f}  z={z:.5f}'.format(x=x, y=y, z=z)

        def fmt2(x, y):
            z = -np.take(fmt_a((x, y)), 0)
            return 'x={x:.2f}  y={y:.2f}  z={z:.5f}'.format(x=x, y=y, z=z)

        # ───────────────────────────────
        # GridSpec layout (left sync, right async)
        # ───────────────────────────────
        gs = mpl.gridspec.GridSpec(
            5, 4,
            width_ratios=[2, 7, 0.2, 7],     # lefter | sync | cbar | async
            height_ratios=[0.4, 0.75, 2, 7, 2],
            wspace=0, hspace=0
        )

        # axes dictionary
        ax = dict(
            sync      = fig.add_subplot(gs[3, 1]),
            async_    = fig.add_subplot(gs[3, 3]),
            upper     = fig.add_subplot(gs[2, 1], sharex=None),
            upper_r   = fig.add_subplot(gs[2, 3], sharex=None),
            lefter    = fig.add_subplot(gs[3, 0], sharey=None),
            lower     = fig.add_subplot(gs[4, 1], sharex=None),
            lower_r   = fig.add_subplot(gs[4, 3], sharex=None),
        )
        # share central axes
        ax['upper'].sharex(ax['sync'])
        ax['upper_r'].sharex(ax['async_'])
        ax['lefter'].sharey(ax['sync'])
        ax['lower'].sharex(ax['sync'])
        ax['lower_r'].sharex(ax['async_'])

        for a in ax.values():
            a.tick_params(axis='both', which='both', direction='out', bottom=False, top=False, left=False, right=False, labelbottom=False, labelleft=False, labeltop=False, labelright=False, length=4)

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

        x1 = model.describe1.index
        d1 = model.describe1
        for target in (ax['upper'], ax['upper_r']):
            target.plot(x1, model.first1, 'r-', label="First", linewidth=linewidth)
            target.plot(x1, d1['mean'], label="Mean", linewidth=linewidth)
            target.fill_between(x1, d1['min'], d1['max'], alpha=0.3)
            target.plot(x1, model.last1,  'k-', label="Last", linewidth=linewidth)
            target.set_xlim(x1.min(), x1.max())
            target.legend(fontsize=fontsize)

        y1 = model.describe2.index
        d2 = model.describe2
        ax['lefter'].plot(model.first2, y1, 'r-', label="First", linewidth=linewidth)
        ax['lefter'].plot(d2['mean'],    y1, label="Mean",       linewidth=linewidth)
        ax['lefter'].fill_betweenx(y1, d2['min'], d2['max'], alpha=0.3)
        ax['lefter'].plot(model.last2,  y1, 'k-', label="Last", linewidth=linewidth)
        ax['lefter'].set_ylim(y1.min(), y1.max())
        ax['lefter'].legend(fontsize=fontsize)

        # ── Heat-maps & contours ─────────────────────────────────────
        xi, yi = model.syncr.index, model.syncr.columns

        im_s = ax['sync'].imshow(
            sync[::-1, :],
            cmap=settings.color_map,
            vmin=smin, vmax=smax,
            alpha=settings.color_map_intensity,
            aspect="auto",
            extent=(xi[0], xi[-1], yi[0], yi[-1]),
        )
        ax['sync'].contour(
            xi, yi, sync,
            locator=locator,
            vmin=smin, vmax=smax,
            colors=settings.contour_line_color,
            alpha=settings.contour_line_alpha,
            linewidths=linewidth,
        )

        im_a = ax['async_'].imshow(
            async_[::-1, :],
            cmap=settings.color_map,
            vmin=amin, vmax=amax,
            alpha=settings.color_map_intensity,
            aspect="auto",
            extent=(xi[0], xi[-1], yi[0], yi[-1]),
        )
        ax['async_'].contour(
            xi, yi, async_,
            locator=locator,
            vmin=amin, vmax=amax,
            colors=settings.contour_line_color,
            alpha=settings.contour_line_alpha,
            linewidths=linewidth,
        )

        # colourbars
        cax_sync  = fig.add_subplot(gs[0, 1])
        cax_async = fig.add_subplot(gs[0, 3])

        cbar_sync  = fig.colorbar(im_s,  cax=cax_sync,  orientation='horizontal')
        cbar_async = fig.colorbar(im_a,  cax=cax_async, orientation='horizontal')

        for cb in (cbar_sync, cbar_async):
            cb.ax.tick_params(
                axis='x',       
                which='both',    
                direction='out',
                length=4,
                top=True,       
                bottom=False,  
                labeltop=True,   
                labelbottom=False
    )
        # Sync diagonal
        if settings.sync_diag == "main":
            diag_s = sync.diagonal(0)
            ax['sync'].plot(xi, yi, color='k', alpha=0.65, linewidth=linewidth)
        else:
            diag_s = np.fliplr(sync).diagonal(0)
            ax['sync'].plot(xi, yi[::-1], color='k', alpha=0.65, linewidth=linewidth)

        ax['lower'].plot(xi, diag_s, linewidth=linewidth)
        ax['lower'].axhline(0, color='k', alpha=0.4)

        # Async diagonal
        if settings.async_diag == "main":
            diag_a = async_.diagonal(0)
            ax['async_'].plot(xi, yi, color='k', alpha=0.65, linewidth=linewidth)
        else:
            diag_a = np.fliplr(async_).diagonal(0)
            ax['async_'].plot(xi, yi[::-1], color='k', alpha=0.65, linewidth=linewidth)

        ax['lower_r'].plot(xi, diag_a, linewidth=linewidth)
        ax['lower_r'].axhline(0, color='k', alpha=0.4)

        # Axis bounds & orientation
        for key in ('sync', 'async_'):
            ax[key].set_xlim(xi.min(), xi.max())
            ax[key].set_ylim(yi.min(), yi.max())
            if settings.x_axis == "decreasing":
                ax[key].invert_xaxis()

        ax['sync'].format_coord  = fmt1
        ax['async_'].format_coord = fmt2

        return fig
