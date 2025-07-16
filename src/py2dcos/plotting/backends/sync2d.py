from __future__ import annotations
from typing import TYPE_CHECKING

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from scipy.interpolate import RegularGridInterpolator

from py2dcos.core.locator import define_locator
from py2dcos.plotting.backends.base import PlotBase
from py2dcos.plotting.settings import PlotSettings
from py2dcos.config.resources import PeaksSigns

if TYPE_CHECKING:
    from py2dcos.core.correlation_model import CorrelationModel

class Sync2DPlot(PlotBase):
    """
    draws the synchronous-correlation 2d plot (the 'sync' mode).
    """
    def draw(
        self,
        model: "CorrelationModel",
        settings: PlotSettings,
    ) -> plt.Figure:
        
        fig = self.figure
        fig.set_facecolor("#f0f0f0")

        linewidth = 0.9
        fontsize  = 8
        
        # choose locator based on settings to control contour level placement
        locator = define_locator(settings.locator, settings.num_contours)

        # copy data and apply peak sign filtering if requested
        data = model.syncr.values.copy()
        if settings.peaks == "positive":
            data = np.where(data > 0, data, np.nan)
        elif settings.peaks == "negative":
            data = np.where(data < 0, data, np.nan)

        # compute color scale limits from filtered data
        zmin, zmax = np.nanmin(data), np.nanmax(data)

        # prepare interpolator for interactive coordinate display
        func = RegularGridInterpolator(
            (model.syncr.index, model.syncr.columns),
            model.syncr.values
        )
        def fmt(x, y):
            # return formatted x, y, z for tooltip display
            z = np.take(func((x, y)), 0)
            return 'x={x:.2f}  y={y:.2f}  z={z:.5f}'.format(x=x, y=y, z=z)

        # set up grid layout for central and marginal panels
        gs = mpl.gridspec.GridSpec(
            3, 6,
            width_ratios=[2., 2, 5, 1., 0.25, 2.],
            height_ratios=[2, 7, 2],
            wspace=0.0,
            hspace=0.0
        )
        keys = ['central', 'upper', 'lefter', 'lower']
        params = [
            'axis', 'which', 'bottom', 'top', 'right',
            'left', 'labelbottom', 'labelleft', 'labeltop', 'labelright'
        ]
        indices = [[1, 2], [0, 2], [1, 1], [2, 2]]

        # determine tick and label visibility for each panel
        panel_tick_params = {k: {} for k in keys}
        for k in keys:
            for p in params:
                if p in ('axis', 'which'):
                    panel_tick_params[k][p] = 'both'
                else:
                    panel_tick_params[k][p] = (
                        k == 'central' or p in ('bottom', 'top', 'right', 'left')
                    )
        for k in ('upper', 'lower'):
            panel_tick_params[k]['labelright'] = True
        panel_tick_params['lefter']['labelbottom'] = True
        panel_tick_params['lefter']['labeltop'] = True
        panel_tick_params['lefter']['labelleft'] = True
        panel_tick_params['upper']['labeltop'] = True
        panel_tick_params['lower']['labelbottom'] = True
        panel_tick_params['central']['labelbottom'] = False
        panel_tick_params['central']['labeltop'] = False
        panel_tick_params['central']['labelleft'] = False

        panels = {}
        # create panels once and share axes where needed
        for i, k in enumerate(keys):
            r, c = indices[i]
            if indices[i] not in ([1, 2], [1, 1], [1, 3]):
                panels[k] = fig.add_subplot(gs[r, c], sharex=panels.get('central'))
            elif indices[i] == [1, 1]:
                panels[k] = fig.add_subplot(gs[r, c], sharey=panels.get('central'))
            elif indices[i] == [1, 3]:
                panels[k] = fig.add_subplot(
                    gs[r, c],
                    sharex=panels.get('central'),
                    sharey=panels.get('central')
                )
            else:
                panels[k] = fig.add_subplot(gs[r, c])

            panels[k].tick_params(
                axis=panel_tick_params[k]['axis'],
                which=panel_tick_params[k]['which'],
                bottom=panel_tick_params[k]['bottom'],
                top=panel_tick_params[k]['top'],
                right=panel_tick_params[k]['right'],
                left=panel_tick_params[k]['left'],
                labelbottom=panel_tick_params[k]['labelbottom'],
                labelleft=panel_tick_params[k]['labelleft'],
                labeltop=panel_tick_params[k]['labeltop'],
                labelright=panel_tick_params[k]['labelright']
            )

        # invert x axis on left panel for correct orientation
        panels['lefter'].invert_xaxis()

        # plot reference spectra panels on upper and lefter panels
        num_wave = model.describe1.index
        data_trans = model.describe1
        panels['upper'].plot(num_wave, model.first1, 'r-', label='First', linewidth=linewidth)
        panels['upper'].plot(num_wave, data_trans['mean'], label='Mean', linewidth=linewidth)
        panels['upper'].fill_between(num_wave, data_trans['min'], data_trans['max'], alpha=0.3)
        panels['upper'].plot(num_wave, model.last1, 'k-', label='Last', linewidth=linewidth)
        panels['upper'].legend(loc='best', fontsize=fontsize)
        panels['upper'].set_xlim(num_wave.min(), num_wave.max())

        num_wave = model.describe2.index
        data_trans = model.describe2
        panels['lefter'].plot(model.first2, num_wave, 'r-', label='First', linewidth=linewidth)
        panels['lefter'].plot(data_trans['mean'], num_wave, label='Mean', linewidth=linewidth)
        panels['lefter'].fill_betweenx(num_wave, data_trans['min'], data_trans['max'], alpha=0.3)
        panels['lefter'].plot(model.last2, num_wave, 'k-', label='Last', linewidth=linewidth)
        panels['lefter'].legend(loc='best', fontsize=fontsize)
        panels['lefter'].set_ylim(num_wave.min(), num_wave.max())

        # plot diagonal values in lower panel
        num_wave = model.syncr.index
        panels['lower'].plot(num_wave, data.diagonal(0), linewidth=linewidth)
        panels['lower'].axhline(y=0., color='k', alpha=0.4)
        panels['lower'].set_xlim(num_wave.min(), num_wave.max())

        imshow_kwargs = dict(
            vmax=zmax,
            vmin=zmin,
            cmap=settings.color_map,
            extent=(num_wave[0], num_wave[-1], model.syncr.columns[0], model.syncr.columns[-1]),
            alpha=settings.color_map_intensity,
            aspect='auto'
        )

        # draw heatmap and contours in central panel
        imA = panels['central'].imshow(data[::-1, ::], **imshow_kwargs)
        panels['central'].contour(
            num_wave, model.syncr.columns, data,
            locator=locator,
            colors=settings.contour_line_color,
            alpha=settings.contour_line_alpha,
            linewidths=linewidth
        )

        # add colorbar panel
        cax = fig.add_subplot(gs[1, 4])
        fig.colorbar(imA, cax=cax)

        # overlay main or anti diagonal and plot its values
        if settings.sync_diag == 'main':
            panels['lower'].clear()
            panels['central'].plot(num_wave, model.syncr.columns, color='k', alpha=0.65, linewidth=linewidth)
            panels['lower'].plot(num_wave, data.diagonal(0), linewidth=linewidth)
            panels['lower'].axhline(y=0., color='k', alpha=0.4)
            panels['lower'].set_xlim(num_wave.min(), num_wave.max())
        else:
            panels['lower'].clear()
            panels['central'].plot(num_wave, model.syncr.columns[::-1], color='k', alpha=0.65, linewidth=linewidth)
            panels['lower'].plot(num_wave, np.fliplr(data).diagonal(), linewidth=linewidth)
            panels['lower'].axhline(y=0., color='k', alpha=0.4)
            panels['lower'].set_xlim(num_wave.min(), num_wave.max())

        # set formatter for interactive coordinate readout
        panels['central'].format_coord = fmt

        # enforce axis limits and orientation
        panels['central'].set_xlim(num_wave.min(), num_wave.max())
        panels['central'].set_ylim(model.syncr.columns.min(), model.syncr.columns.max())
        if settings.x_axis == 'decreasing':
            panels['central'].invert_xaxis()

        return fig
