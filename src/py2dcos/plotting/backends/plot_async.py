from __future__ import annotations
from typing import TYPE_CHECKING
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from scipy.interpolate import RegularGridInterpolator
from matplotlib.figure import Figure
from py2dcos.plotting.backends.locator import define_locator
from py2dcos.datatypes.plot_settings import PlotSettings
from py2dcos.config.resources import AxisDirection
from py2dcos.config.resources import PeaksSigns
from py2dcos.config.resources import Diagonal
from py2dcos.config.resources import CANVAS_BACKGROUND
if TYPE_CHECKING:
    from py2dcos.core.math.correlation_model import CorrelationModel
    from matplotlib.figure import Figure


def plot_async2d(
        model: CorrelationModel, 
        settings: PlotSettings,
        *,
        figure: Figure | None = None) -> Figure:
    
    # prepare the figure and background
    fig = figure or plt.figure()
    fig.clf()
    fig.set_facecolor(CANVAS_BACKGROUND)
    # define default line and font styling for consistency
    linewidth = 0.9
    fontsize = 8

    # select tick locator based on settings to control contour levels
    locator = define_locator(settings.locator, settings.num_contours)

    # extract async correlation array and apply peak sign filtering
    data = model.asyncr.values.copy()
    if settings.peaks is PeaksSigns.POSITIVE:
        data = np.where(data > 0, data, np.nan)
    elif settings.peaks is PeaksSigns.NEGATIVE:
        data = np.where(data < 0, data, np.nan)

    # determine color scale bounds from filtered data
    zmin, zmax = np.nanmin(data), np.nanmax(data)

    # prepare interpolation function for interactive readout
    func = RegularGridInterpolator((model.asyncr.columns, model.asyncr.index), model.asyncr.values)
    def fmt(x, y):
        z = -np.take(func((x, y)), 0)
        return 'x={x:.2f}  y={y:.2f}  z={z:.5f}'.format(x=x, y=y, z=z)

    # set up grid layout for multiple plot panels
    gs = mpl.gridspec.GridSpec(
        3, 6,
        width_ratios=[2., 2, 5, 1., 0.25, 2.],
        height_ratios=[2, 7, 2],
        wspace=0.0,
        hspace=0.0
    )

    # define panel names and shared axis parameters
    keys = ['central', 'upper', 'lefter', 'lower']
    params = ['axis', 'which', 'bottom', 'top', 'right', 'left',
                'labelbottom', 'labelleft', 'labeltop', 'labelright']
    indices = [[1, 2], [0, 2], [1, 1], [2, 2]]

    # initialize default tick parameter settings per panel
    panel_tick_params = {k: {} for k in keys}
    for k in keys:
        for p in params:
            if p in ['axis', 'which']:
                panel_tick_params[k][p] = 'both'
            else:
                panel_tick_params[k][p] = (k == 'central') or (p in ['bottom', 'top', 'right', 'left'])

    # adjust label visibility for specific panels
    for k in ['upper', 'lower']:
        panel_tick_params[k]['labelright'] = True
    panel_tick_params['lefter']['labelbottom'] = True
    panel_tick_params['lefter']['labeltop'] = True
    panel_tick_params['lefter']['labelleft'] = True
    panel_tick_params['upper']['labeltop'] = True
    panel_tick_params['lower']['labelbottom'] = True
    panel_tick_params['central']['labelbottom'] = False
    panel_tick_params['central']['labeltop'] = False
    panel_tick_params['central']['labelleft'] = False

    # create subplot axes for each panel, sharing axes where appropriate
    panels = {}
    for i, key in enumerate(keys):
        r, c = indices[i]
        if indices[i] not in [[1, 2], [1, 1], [1, 3]]:
            panels[key] = fig.add_subplot(gs[r, c], sharex=panels.get('central'))
        elif indices[i] == [1, 1]:
            panels[key] = fig.add_subplot(gs[r, c], sharey=panels.get('central'))
        elif indices[i] == [1, 3]:
            panels[key] = fig.add_subplot(gs[r, c],
                                            sharex=panels.get('central'),
                                            sharey=panels.get('central'))
        else:
            panels[key] = fig.add_subplot(gs[r, c])

        # apply tick styling to each panel
        panels[key].tick_params(
            axis=panel_tick_params[key]['axis'],
            which=panel_tick_params[key]['which'],
            bottom=panel_tick_params[key]['bottom'],
            top=panel_tick_params[key]['top'],
            right=panel_tick_params[key]['right'],
            left=panel_tick_params[key]['left'],
            labelbottom=panel_tick_params[key]['labelbottom'],
            labelleft=panel_tick_params[key]['labelleft'],
            labeltop=panel_tick_params[key]['labeltop'],
            labelright=panel_tick_params[key]['labelright']
        )

    # invert x-axis on the left panel for correct orientation
    panels['lefter'].invert_xaxis()

    # plot summary statistics on upper and lefter panels
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

    # plot diagonal review in lower panel before contours
    num_wave = model.asyncr.index
    panels['lower'].plot(num_wave, np.flip(np.fliplr(data).diagonal(0)), linewidth=linewidth)
    panels['lower'].axhline(y=0., color='k', alpha=0.4)
    panels['lower'].set_xlim(num_wave.min(), num_wave.max())

    # prepare color scale arguments for central panel image
    num_wave2 = model.asyncr.columns
    imshow_kwargs = dict(
        vmax=zmax,
        vmin=zmin,
        cmap=settings.color_map,
        extent=(num_wave[0], num_wave[-1], num_wave2[0], num_wave2[-1]),
        alpha=settings.color_map_intensity,
        aspect="auto",
    )

    # draw the heatmap and contour lines in the central panel
    imA = panels['central'].imshow(data[::-1, ::], **imshow_kwargs)
    panels['central'].contour(
        num_wave, num_wave2, data,
        locator=locator,
        colors=settings.contour_line_color,
        alpha=settings.contour_line_alpha,
        linewidths=linewidth
    )

    # add a colorbar next to the central panel
    caxA = fig.add_subplot(gs[1, 4])
    cbA = plt.colorbar(imA, cax=caxA)

    # overlay the selected diagonal on both central and lower panels
    if settings.async_diag is Diagonal.MAIN:
        panels['lower'].clear()
        panels['central'].plot(num_wave, num_wave2, color='k', alpha=0.65, linewidth=linewidth)
        panels['lower'].plot(num_wave, data.diagonal(0), linewidth=linewidth)
        panels['lower'].axhline(y=0., color='k', alpha=0.4)
        panels['lower'].set_xlim(num_wave.min(), num_wave.max())
    else:
        panels['lower'].clear()
        panels['central'].plot(num_wave, num_wave2[::-1], color='k', alpha=0.65, linewidth=linewidth)
        panels['lower'].plot(num_wave, np.flip(np.fliplr(data).diagonal(0)), linewidth=linewidth)
        panels['lower'].axhline(y=0., color='k', alpha=0.4)
        panels['lower'].set_xlim(num_wave.min(), num_wave.max())

    # set interactive coordinate formatter for central panel
    panels['central'].format_coord = fmt

    # enforce axis limits after plotting
    panels['central'].set_xlim(num_wave.min(), num_wave.max())
    panels['central'].set_ylim(num_wave2.min(), num_wave2.max())

    # invert central x-axis if user prefers decreasing orientation
    if settings.x_axis is AxisDirection.DECREASING:
        panels['central'].invert_xaxis()

    return fig
