from typing import TYPE_CHECKING
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from scipy.interpolate import RegularGridInterpolator
from matplotlib.figure import Figure

from py2dcos.core.locator import define_locator
from py2dcos.plotting.backends.base import PlotBase
from py2dcos.plotting.settings import PlotSettings, Peaks 

if TYPE_CHECKING:
    # avoid circular imports at runtime
    from py2dcos.core.correlation_model import CorrelationModel

class Sync2DPlot(PlotBase):
    """
    Draws the synchronous‐correlation 2D plot (the 'sync' mode).
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
        
        locator = define_locator(settings.locator, settings.num_contours)

        data = model.syncr.values.copy()
        if settings.peaks is settings.Peaks.POSITIVE:
            data = np.where(data > 0, data, np.nan)
        elif settings.peaks is settings.Peaks.NEGATIVE:
            data = np.where(data < 0, data, np.nan)

        zmin, zmax = np.nanmin(data), np.nanmax(data)

        # synchronous 2D correlation plot
        func = RegularGridInterpolator((model.syncr.index, model.syncr.columns), model.syncr.values)

        def fmt(x, y):
            # show x,y,z on hover
            z = np.take(func((x, y)), 0)
            return 'x={x:.2f}  y={y:.2f}  z={z:.5f}'.format(x=x, y=y, z=z)

        gs = mpl.gridspec.GridSpec(3, 6, width_ratios=[2., 2, 5, 1., 0.25, 2.], height_ratios=[2, 7, 2], wspace=0.0,
                                    hspace=0.0)
        # keys to name the panels
        keys = ['central', 'upper', 'lefter', 'lower']
        params = ['axis', 'which', 'bottom', 'top', 'right', 'left', 'labelbottom', 'labelleft', 'labeltop',
                    'labelright']
        # proportion of the grids, to be able to iterates
        indices = [[1, 2], [0, 2], [1, 1], [2, 2]]

        panel_tick_params = {clave: {} for clave in keys}
        for clave in keys:
            # set tick/label visibility for each panel
            for param in params:
                if param in ['axis', 'which']:
                    panel_tick_params[clave][param] = 'both'
                else:
                    panel_tick_params[clave][param] = True if clave in ['central'] or param in ['bottom', 'top',
                                                                                                'right',
                                                                                                'left'] else False
        for clave in ['upper', 'lower']:
            panel_tick_params[clave]['labelright'] = True  # labels left is on in upper and lower panels
        # adjust specific label placements
        panel_tick_params['lefter']['labelbottom'] = True  # labels bottom is on in lefter panel
        panel_tick_params['lefter']['labeltop'] = True
        panel_tick_params['lefter']['labelleft'] = True

        panel_tick_params['upper']['labeltop'] = True
        panel_tick_params['lower']['labelbottom'] = True

        panel_tick_params['central']['labelbottom'] = False
        panel_tick_params['central']['labeltop'] = False
        panel_tick_params['central']['labelleft'] = False

        panels = {}
        # Creating the panels. This is done just once
        for i, clave in enumerate(keys):
            j, k = indices[i]
            if indices[i] not in [[1, 2], [1, 1], [1, 3]]:
                panels[clave] = fig.add_subplot(gs[j, k], sharex=panels['central'])
            elif indices[i] == [1, 1]:
                panels[clave] = fig.add_subplot(gs[j, k], sharey=panels['central'])
            elif indices[i] == [1, 3]:
                panels[clave] = fig.add_subplot(gs[j, k], sharex=panels['central'],
                                                        sharey=panels['central'])
            else:
                panels[clave] = fig.add_subplot(gs[j, k])

            panels[clave].tick_params(
                axis=panel_tick_params[clave]['axis'],  # changes apply to the x-axis
                which=panel_tick_params[clave]['which'],  # both major and minor ticks are affected
                bottom=panel_tick_params[clave]['bottom'],  # ticks along the bottom edge are off
                top=panel_tick_params[clave]['top'],  # ticks along the top edge are off
                right=panel_tick_params[clave]['right'],  # ticks along the right edge are off
                left=panel_tick_params[clave]['left'],  # ticks along the left edge are off
                labelbottom=panel_tick_params[clave]['labelbottom'],  # labels along the bottom edge are off
                labelleft=panel_tick_params[clave]['labelleft'],  # labels along the left edge are off
                labeltop=panel_tick_params[clave]['labeltop'],  # labels along the bottom edge are off
                labelright=panel_tick_params[clave]['labelright'])  # labels along the left edge are off

        # Setting particularly the lefter panel
        panels['lefter'].invert_xaxis()
        # panels['lefter'].invert_yaxis()

        # Plotting the information...
        # panels['upper'].plot(num_wave,spect)
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
        panels['lefter'].plot(data_trans['mean'], num_wave, label='Mean',
                                linewidth=linewidth)  ## Attention! The data is inverted
        panels['lefter'].fill_betweenx(num_wave, data_trans['min'], data_trans['max'], alpha=0.3)
        panels['lefter'].plot(model.last2, num_wave, 'k-', label='Last', linewidth=linewidth)
        panels['lefter'].legend(loc='best', fontsize=fontsize)
        panels['lefter'].set_ylim(num_wave.min(), num_wave.max())


        num_wave = model.syncr.index
        num_wave2 = model.syncr.columns

        panels['lower'].plot(num_wave, data.diagonal(0), linewidth=linewidth)
        panels['lower'].axhline(y=0., color='k', alpha=0.4)
        panels['lower'].set_xlim(num_wave.min(), num_wave.max())


        imshow_kwargs = dict(
            vmax = zmax,
            vmin = zmin,
            cmap = settings.color_map,
            extent = (num_wave[0], num_wave[-1], num_wave2[0], num_wave2[-1]),
            alpha = settings.color_map_intensity,
            aspect = "auto",
        )

        imA = panels['central'].imshow(data[::-1, ::], **imshow_kwargs)

        panels['central'].contour(num_wave, num_wave2, data, locator=locator, cmap=None, vmin=zmin, vmax=zmax,
                                    colors=settings.contour_line_color, alpha=settings.contour_line_alpha, linewidths=linewidth)

        # colour-bar
        cax = fig.add_subplot(gs[1, 4])
        fig.colorbar(imA, cax=cax)

        # Plotting the diagonal
        if settings.sync_diag == 'main':
            panels['lower'].clear()
            panels['central'].plot(num_wave, num_wave2, color='k', alpha=0.65, linewidth=linewidth)
            panels['lower'].plot(num_wave, data.diagonal(0), linewidth=linewidth)
            panels['lower'].axhline(y=0., color='k', alpha=0.4)
            panels['lower'].set_xlim(num_wave.min(), num_wave.max())

        else:
            panels['lower'].clear()
            panels['central'].plot(num_wave, num_wave2[::-1], color='k', alpha=0.65, linewidth=linewidth)
            panels['lower'].plot(num_wave, np.fliplr(data).diagonal(), linewidth=linewidth)
            panels['lower'].axhline(y=0., color='k', alpha=0.4)
            panels['lower'].set_xlim(num_wave.min(), num_wave.max())

        panels['central'].format_coord = fmt

        panels['central'].set_xlim(num_wave.min(), num_wave.max())
        panels['central'].set_ylim(num_wave2.min(), num_wave2.max())

        if settings.x_axis == "decreasing":
            panels['central'].invert_xaxis()

        return fig