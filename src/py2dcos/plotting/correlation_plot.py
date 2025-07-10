from __future__ import annotations
from typing import Optional

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from scipy.interpolate import RegularGridInterpolator
import numpy as np
import matplotlib as mpl
import plotly.graph_objs as go
from py2dcos.core.correlation_model import CorrelationModel
from py2dcos.core.locator import define_locator


class CorrelationPlotter:

    def __init__(self, model: CorrelationModel,
                       figure: Figure|None = None,
                       canvas: FigureCanvasQTAgg|None = None):
        
        # store model and optional figure/canvas for GUI integration
        self.model   = model
        self.figure  = figure or plt.figure()
        self.canvas  = canvas

    def plot(
        self,
        *,
        colorMap: str = "coolwarm",
        numOfContour: int = 6,
        locator_choice: str = "linear",
        syncDiag: str = "main",
        asyncDiag: str = "anti",
        xAxis: str = "decreasing",
        colorMapIntensity: float = 1.0,
        colorLines: str = "black",
        colorLinesIntensity: float = 0.6,
        shownGraph: str = "both",
        peaks_signs: str = "all",
    ) -> Figure:
        # clear existing figure before drawing
        self.figure.clear()
        # pick tick locator based on user choice
        locator = define_locator(locator_choice, numOfContour)
        fontsize = 8
        linewidth = 0.9
        self.figure.set_facecolor("#f0f0f0")

        if shownGraph == 'sync':
            # synchronous 2D correlation plot
            func = RegularGridInterpolator((self.model.syncr.index, self.model.syncr.columns), self.model.syncr.values)

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
                    panels[clave] = self.figure.add_subplot(gs[j, k], sharex=panels['central'])
                elif indices[i] == [1, 1]:
                    panels[clave] = self.figure.add_subplot(gs[j, k], sharey=panels['central'])
                elif indices[i] == [1, 3]:
                    panels[clave] = self.figure.add_subplot(gs[j, k], sharex=panels['central'],
                                                            sharey=panels['central'])
                else:
                    panels[clave] = self.figure.add_subplot(gs[j, k])

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
            num_wave = self.model.describe1.index
            data_trans = self.model.describe1
            panels['upper'].plot(num_wave, self.model.first1, 'r-', label='First', linewidth=linewidth)
            panels['upper'].plot(num_wave, data_trans['mean'], label='Mean', linewidth=linewidth)
            panels['upper'].fill_between(num_wave, data_trans['min'], data_trans['max'], alpha=0.3)
            panels['upper'].plot(num_wave, self.model.last1, 'k-', label='Last', linewidth=linewidth)
            panels['upper'].legend(loc='best', fontsize=fontsize)
            panels['upper'].set_xlim(num_wave.min(), num_wave.max())

            num_wave = self.model.describe2.index
            data_trans = self.model.describe2
            panels['lefter'].plot(self.model.first2, num_wave, 'r-', label='First', linewidth=linewidth)
            panels['lefter'].plot(data_trans['mean'], num_wave, label='Mean',
                                  linewidth=linewidth)  ## Attention! The data is inverted
            panels['lefter'].fill_betweenx(num_wave, data_trans['min'], data_trans['max'], alpha=0.3)
            panels['lefter'].plot(self.model.last2, num_wave, 'k-', label='Last', linewidth=linewidth)
            panels['lefter'].legend(loc='best', fontsize=fontsize)
            panels['lefter'].set_ylim(num_wave.min(), num_wave.max())

            # Setting the central and lower panels
            data = self.model.syncr.values
            if peaks_signs == 'all':
                pass
            elif peaks_signs == 'positive':
                data = np.where(data > 0, data, np.nan)
            elif peaks_signs == 'negative':
                data = np.where(data < 0, data, np.nan)

            num_wave = self.model.syncr.index
            num_wave2 = self.model.syncr.columns

            panels['lower'].plot(num_wave, data.diagonal(0), linewidth=linewidth)
            panels['lower'].axhline(y=0., color='k', alpha=0.4)
            panels['lower'].set_xlim(num_wave.min(), num_wave.max())

            # central contour and imshow
            zmin = np.nanmin(data)
            zmax = np.nanmax(data)

            imshow_kwargs = {
                'vmax': zmax,
                'vmin': zmin,
                'cmap': colorMap,
                'extent': (num_wave[0], num_wave[-1], num_wave2[0], num_wave2[-1]),
            }

            imA = panels['central'].imshow(data[::-1, ::], alpha=colorMapIntensity, aspect="auto", **imshow_kwargs)

            panels['central'].contour(num_wave, num_wave2, data, locator=locator, cmap=None, vmin=zmin, vmax=zmax,
                                      colors=colorLines, alpha=colorLinesIntensity, linewidths=linewidth)

            caxA = plt.axes(self.figure.add_subplot(gs[1, 4]))
            cbA = plt.colorbar(imA, cax=caxA)

            # Plotting the diagonal
            if syncDiag == 'main':
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

            if xAxis == "decreasing":
                panels['central'].invert_xaxis()

            if self.canvas is not None:
                self.canvas.draw_idle()

            else:
                plt.show()


        elif shownGraph == 'async':
            # asynchronous 2D correlation plot
            func = RegularGridInterpolator((self.model.asyncr.columns, self.model.asyncr.index), self.model.asyncr.values)

            def fmt(x, y):
                z = -np.take(func((x, y)), 0)
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
                for param in params:
                    if param in ['axis', 'which']:
                        panel_tick_params[clave][param] = 'both'
                    else:
                        panel_tick_params[clave][param] = True if clave in ['central'] or param in ['bottom', 'top',
                                                                                                    'right',
                                                                                                    'left'] else False

            for clave in ['upper', 'lower']:
                panel_tick_params[clave]['labelright'] = True  # labels left is on in upper and lower panels

            panel_tick_params['lefter']['labelbottom'] = True  # labels bottom is on in lefter panel
            panel_tick_params['lefter']['labeltop'] = True
            panel_tick_params['lefter']['labelleft'] = True

            panel_tick_params['upper']['labeltop'] = True
            panel_tick_params['lower']['labelbottom'] = True

            panel_tick_params['central']['labelbottom'] = False
            panel_tick_params['central']['labeltop'] = False
            panel_tick_params['central']['labelleft'] = False

            panels = {}
            # Creating the panels. This is done just one
            for i, clave in enumerate(keys):
                j, k = indices[i]
                if indices[i] not in [[1, 2], [1, 1], [1, 3]]:
                    panels[clave] = self.figure.add_subplot(gs[j, k], sharex=panels['central'])
                elif indices[i] == [1, 1]:
                    panels[clave] = self.figure.add_subplot(gs[j, k], sharey=panels['central'])
                elif indices[i] == [1, 3]:
                    panels[clave] = self.figure.add_subplot(gs[j, k], sharex=panels['central'],
                                                            sharey=panels['central'])
                else:
                    panels[clave] = self.figure.add_subplot(gs[j, k])

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
            num_wave = self.model.describe1.index
            data_trans = self.model.describe1
            panels['upper'].plot(num_wave, self.model.first1, 'r-', label='First', linewidth=linewidth)
            panels['upper'].plot(num_wave, data_trans['mean'], label='Mean', linewidth=linewidth)
            panels['upper'].fill_between(num_wave, data_trans['min'], data_trans['max'], alpha=0.3)
            panels['upper'].plot(num_wave, self.model.last1, 'k-', label='Last', linewidth=linewidth)
            panels['upper'].legend(loc='best', fontsize=fontsize)
            panels['upper'].set_xlim(num_wave.min(), num_wave.max())

            num_wave = self.model.describe2.index
            data_trans = self.model.describe2
            panels['lefter'].plot(self.model.first2, num_wave, 'r-', label='First', linewidth=linewidth)
            panels['lefter'].plot(data_trans['mean'], num_wave, label='Mean',
                                  linewidth=linewidth)  ## Attention! The data is inverted
            panels['lefter'].fill_betweenx(num_wave, data_trans['min'], data_trans['max'], alpha=0.3)
            panels['lefter'].plot(self.model.last2, num_wave, 'k-', label='Last', linewidth=linewidth)
            panels['lefter'].legend(loc='best', fontsize=fontsize)
            panels['lefter'].set_ylim(num_wave.min(), num_wave.max())

            # Setting the central and lower panels
            data = self.model.asyncr.values
            if peaks_signs == 'all':
                pass
            elif peaks_signs == 'positive':
                data = np.where(data > 0, data, np.nan)
            elif peaks_signs == 'negative':
                data = np.where(data < 0, data, np.nan)

            num_wave = self.model.asyncr.index
            num_wave2 = self.model.asyncr.columns

            panels['lower'].plot(num_wave, np.flip(np.fliplr(data).diagonal(0)), linewidth=linewidth)
            panels['lower'].axhline(y=0., color='k', alpha=0.4)
            panels['lower'].set_xlim(num_wave.min(), num_wave.max())

            zmin = np.nanmin(data)
            zmax = np.nanmax(data)

            imshow_kwargs = {
                'vmax': zmax,
                'vmin': zmin,
                'cmap': colorMap,
                'extent': (num_wave[0], num_wave[-1], num_wave2[0], num_wave2[-1]),
            }
            imA = panels['central'].imshow(data[::-1, ::], alpha=colorMapIntensity, aspect="auto", **imshow_kwargs)
            panels['central'].contour(num_wave, num_wave2, data, locator=locator, cmap=None, vmin=zmin, vmax=zmax,
                                      colors=colorLines, alpha=colorLinesIntensity, linewidths=linewidth)

            caxA = plt.axes(self.figure.add_subplot(gs[1, 4]))
            cbA = plt.colorbar(imA, cax=caxA)

            # Plotting the diagonal
            if asyncDiag == 'main':
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

            panels['central'].format_coord = fmt

            panels['central'].set_xlim(num_wave.min(), num_wave.max())
            panels['central'].set_ylim(num_wave2.min(), num_wave2.max())

            if xAxis == "decreasing":
                panels['central'].invert_xaxis()

            if self.canvas is not None:
                self.canvas.draw_idle()
            else:
                plt.show()


        elif shownGraph == 'both':
            # combined sync and async 2D plots and colorbars
            func1 = RegularGridInterpolator((self.model.syncr.index, self.model.syncr.columns), self.model.syncr.values)
            func2 = RegularGridInterpolator((self.model.asyncr.index, self.model.asyncr.columns), self.model.asyncr.values)

            def fmt1(x, y):
                z = np.take(func1((x, y)), 0)
                return 'x={x:.2f}  y={y:.2f}  z={z:.5f}'.format(x=x, y=y, z=z)

            def fmt2(x, y):
                z = -np.take(func2((x, y)), 0)
                return 'x={x:.2f}  y={y:.2f}  z={z:.5f}'.format(x=x, y=y, z=z)

            gs = mpl.gridspec.GridSpec(5, 4, width_ratios=[2, 7, 0.2, 7],
                                       height_ratios=[0.4, 0.75, 2, 7, 2], wspace=0, hspace=0)
            gs.update(wspace=0, hspace=0)

            # proportion of the grids, to be able to iterates
            cbar_gs = {'central': gs[0, 1], 'right': gs[0, 3]}
            cbar_or = {'central': 'horizontal', 'right': 'horizontal'}
            indices = [[3, 1], [2, 1], [3, 0], [4, 1], [2, 3], [3, 3], [4, 3]]
            # keys to name the panels
            keys = ['central', 'upper', 'lefter', 'lower', 'upper_right', 'right', 'lower_right']
            params = ['axis', 'which', 'bottom', 'top', 'right', 'left', 'labelbottom', 'labelleft', 'labeltop',
                      'labelright']

            panel_tick_params = {clave: {} for clave in keys}
            for clave in keys:
                for param in params:
                    if param in ['axis', 'which']:
                        panel_tick_params[clave][param] = 'both'
                    else:
                        panel_tick_params[clave][param] = True if clave in ['central', 'right'] or param in ['bottom',
                                                                                                             'top',
                                                                                                             'right',
                                                                                                             'left'] else False

            for clave in ['upper', 'lower']:
                panel_tick_params[clave]['labelleft'] = True  # labels left is on in upper and lower panels

            for clave in ['upper_right', 'lower_right']:
                panel_tick_params[clave]['labelright'] = True  # labels left is on in upper and lower panels

            panel_tick_params['lefter']['labelbottom'] = True  # labels bottom is on in lefter panel
            panel_tick_params['lefter']['labelleft'] = True  # labels left is on in lefter panel

            for clave in ['lower', 'lower_right']:
                panel_tick_params[clave][
                    'labelbottom'] = True  # labels at bottom are on in lower and lower_right panels

            for clave in ['upper', 'upper_right']:
                panel_tick_params[clave]['labeltop'] = True  # labels at top are on in upper and upper_right panels

            # Setting labels for central and right panels
            for label in ['labelleft', 'labeltop', 'labelbottom']:
                panel_tick_params['central'][label] = False  # all labels are off in central panel
                panel_tick_params['right'][label] = False  # all labels are off in right panel
            panel_tick_params['central']['labelright'] = False  # all labels are off in central panel

            panel_tick_params['right']['labelleft'] = False  # labels left is off in right panel

            # ticks between panels are off
            panel_tick_params['central']['right'] = False
            panel_tick_params['upper']['right'] = False
            panel_tick_params['lower']['right'] = False
            panel_tick_params['right']['left'] = False
            panel_tick_params['upper_right']['left'] = False
            panel_tick_params['lower_right']['left'] = False

            panels = {}
            # Creating the panels. This is done just one
            for i, clave in enumerate(keys):
                j, k = indices[i]
                if clave not in ['central', 'lefter', 'right']:
                    panels[clave] = self.figure.add_subplot(gs[j, k], sharex=panels['central'])
                elif clave == 'right':
                    panels[clave] = self.figure.add_subplot(gs[j, k], sharex=panels['central'],
                                                            sharey=panels['central'])
                elif clave == 'lefter':
                    panels[clave] = self.figure.add_subplot(gs[j, k], sharey=panels['central'])
                else:
                    panels[clave] = self.figure.add_subplot(gs[j, k])

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

            # Plotting the information...
            num_wave = self.model.describe1.index
            data_trans = self.model.describe1
            panels['upper'].plot(num_wave, self.model.first1, 'r-', label='First', linewidth=linewidth)
            panels['upper'].plot(num_wave, data_trans['mean'], label='Mean', linewidth=linewidth)
            panels['upper'].fill_between(num_wave, data_trans['min'], data_trans['max'], alpha=0.3)
            panels['upper'].plot(num_wave, self.model.last1, 'k-', label='Last', linewidth=linewidth)
            panels['upper'].legend(loc='best', fontsize=fontsize)
            panels['upper'].set_xlim(num_wave.min(), num_wave.max())

            panels['upper_right'].plot(num_wave, self.model.first1, 'r-', label='First', linewidth=linewidth)
            panels['upper_right'].plot(num_wave, data_trans['mean'], label='Mean', linewidth=linewidth)
            panels['upper_right'].fill_between(num_wave, data_trans['min'], data_trans['max'], alpha=0.3)
            panels['upper_right'].plot(num_wave, self.model.last1, 'k-', label='Last', linewidth=linewidth)
            panels['upper_right'].legend(loc='best', fontsize=fontsize)
            panels['upper_right'].set_xlim(num_wave.min(), num_wave.max())

            num_wave = self.model.describe2.index
            data_trans = self.model.describe2
            panels['lefter'].plot(self.model.first2, num_wave, 'r-', label='First', linewidth=linewidth)
            panels['lefter'].plot(data_trans['mean'], num_wave, label='Mean',
                                  linewidth=linewidth)  ## Attention! The data is inverted
            panels['lefter'].fill_betweenx(num_wave, data_trans['min'], data_trans['max'], alpha=0.3)
            panels['lefter'].plot(self.model.last2, num_wave, 'k-', label='Last', linewidth=linewidth)
            panels['lefter'].legend(loc='best', fontsize=fontsize)
            panels['lefter'].set_ylim(num_wave.min(), num_wave.max())

            # Setting the central and lower panels

            data = self.model.syncr.values
            if peaks_signs == 'all':
                pass
            elif peaks_signs == 'positive':
                data = np.where(data > 0, data, np.nan)
            elif peaks_signs == 'negative':
                data = np.where(data < 0, data, np.nan)

            num_wave = self.model.syncr.index
            num_wave2 = self.model.syncr.columns
            # This test only plot the diagonal of sync 2D corr
            panels['lower'].plot(num_wave, data.diagonal(0), linewidth=linewidth)
            panels['lower'].axhline(y=0., color='k', alpha=0.4)
            panels['lower'].set_xlim(num_wave.min(), num_wave.max())

            zmin = np.nanmin(data)
            zmax = np.nanmax(data)

            imshow_kwargs = {
                'vmax': zmax,
                'vmin': zmin,
                'cmap': colorMap,
                'extent': (num_wave[0], num_wave[-1], num_wave2[0], num_wave2[-1])
            }
            panels['central'].contour(num_wave, num_wave2, data, locator=locator, cmap=None, vmin=zmin, vmax=zmax,
                                      colors=colorLines, alpha=colorLinesIntensity, linewidths=linewidth)

            aspectIm = "auto"
            imS = panels['central'].imshow(data[::-1, ::], alpha=colorMapIntensity, aspect=aspectIm, **imshow_kwargs)
            caxS = plt.subplot(cbar_gs['central'])
            cb_left = plt.colorbar(imS, cax=caxS, orientation=cbar_or['central'], )
            cb_left.ax.tick_params(
                top=True,
                labeltop=True,
                bottom=False,
                labelbottom=False,
            )

            # diagonals
            if syncDiag == 'main':
                panels['lower'].clear()
                panels['central'].plot(num_wave, num_wave2, linewidth=linewidth, color='k', alpha=0.65)
                panels['lower'].plot(num_wave, data.diagonal(0), linewidth=linewidth)
                panels['lower'].axhline(y=0., color='k', alpha=0.4)
                panels['lower'].set_xlim(num_wave.min(), num_wave.max())
            else:
                panels['lower'].clear()
                panels['central'].plot(num_wave, num_wave2[::-1], linewidth=linewidth, color='k', alpha=0.65)
                panels['lower'].plot(num_wave, np.fliplr(data).diagonal(), linewidth=linewidth)
                panels['lower'].axhline(y=0., color='k', alpha=0.4)
                panels['lower'].set_xlim(num_wave.min(), num_wave.max())

            panels['central'].set_xlim(num_wave.min(), num_wave.max())
            panels['central'].set_ylim(num_wave2.min(), num_wave2.max())
            panels['central'].format_coord = fmt1

            # Setting the right and lower_right panels
            data = self.model.asyncr.values
            if peaks_signs == 'all':
                pass
            elif peaks_signs == 'positive':
                data = np.where(data > 0, data, np.nan)
            elif peaks_signs == 'negative':
                data = np.where(data < 0, data, np.nan)

            num_wave = self.model.asyncr.index
            num_wave2 = self.model.asyncr.columns

            # This test only plot the diagonal of sync 2D corr
            panels['lower_right'].plot(num_wave, np.flip(np.fliplr(data).diagonal(0)))
            panels['lower_right'].axhline(y=0., color='k', alpha=0.4)
            panels['lower_right'].set_xlim(num_wave.min(), num_wave.max())

            # breakpoint()    # for debugging
            zmin = np.nanmin(data)
            zmax = np.nanmax(data)

            imshow_kwargs['vmax'] = zmax
            imshow_kwargs['vmin'] = zmin

            panels['right'].contour(num_wave, num_wave2, data, locator=locator, cmap=None, vmin=zmin, vmax=zmax,
                                    colors=colorLines, alpha=colorLinesIntensity, linewidths=linewidth)
            imA = panels['right'].imshow(data[::-1, ::], alpha=colorMapIntensity, aspect=aspectIm, **imshow_kwargs)
            caxA = plt.subplot(cbar_gs['right'])
            cb_right = plt.colorbar(imA, cax=caxA, orientation=cbar_or['right'])
            cb_right.ax.tick_params(
                top=True,
                labeltop=True,
                bottom=False,
                labelbottom=False,
            )

            if asyncDiag == 'main':
                panels['lower_right'].clear()
                panels['right'].plot(num_wave, num_wave2, linewidth=1., color='k', alpha=0.65)
                panels['lower_right'].plot(num_wave, data.diagonal(0), linewidth=linewidth)
                panels['lower_right'].axhline(y=0., color='k', alpha=0.4)
                panels['lower_right'].set_xlim(num_wave.min(), num_wave.max())

            else:
                panels['lower_right'].clear()
                panels['right'].plot(num_wave, num_wave2[::-1], linewidth=1., color='k', alpha=0.65)
                panels['lower_right'].plot(num_wave, np.flip(np.fliplr(data).diagonal(0)), linewidth=linewidth)
                panels['lower_right'].axhline(y=0., color='k', alpha=0.4)
                panels['lower_right'].set_xlim(num_wave.min(), num_wave.max())

            panels['right'].set_xlim(num_wave.min(), num_wave.max())
            panels['right'].set_ylim(num_wave2.min(), num_wave2.max())
            panels['right'].format_coord = fmt2

            if xAxis == 'decreasing':
                panels['central'].invert_xaxis()

            if self.canvas is not None:
                self.canvas.draw_idle()

            else:
                plt.show()


    def plot3d(self, *, color_map: str = "coolwarm"):
        # render 3D surface plots via Plotly
        fig = go.Figure(data=[go.Surface(x=self.model.syncr.index, y=self.model.syncr.columns, z=self.model.syncr.values)])

        fig.update_layout(title='Synchronous Spectra',
                          margin=dict(l=65, r=50, b=65, t=90))

        fig.show()

        fig2 = go.Figure(
            data=[go.Surface(x=self.model.asyncr.index, y=self.model.asyncr.columns, z=self.model.asyncr.values)])

        fig2.update_layout(title='Asynchronous Spectra',
                           margin=dict(l=65, r=50, b=65, t=90))
        fig2.show()
