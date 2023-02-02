#!/usr/bin/env python

import numpy as np
# import math
import matplotlib as mpl
import pandas as pd
import matplotlib.pyplot as plt


def checkHeader(df):
    ##### This functon seems not to work properly, I changed the header and
    ##### it looks to work now... But check if it is want you wanted
    col = df.columns
    # if float(col[0]) + float(col[-1]) == len(col)+1:
    #     pass
    # else:
    if float(col[0]) + float(col[-1]) != len(col) + 1:
        head = np.linspace(1, len(col), len(col))
        df.columns = head

    return df


def reader(filename):
    if filename[1] == "csv":
        spec1 = pd.read_csv(filename[0], header=None, index_col=0)
        return spec1

    if filename[1] == "xlsx":
        ## The default option (only the matrix)
        try:
            sheet, row, column = filename[-3:]
            row = int(row)
            spec1 = pd.read_excel(filename[0], header=None, index_col=0, sheet_name=sheet, usecols=column, skiprows=row)

        except:
            spec1 = pd.read_excel(filename[0], header=None, index_col=0)

        # spec1 = pd.read_excel(filename[0], header=0, index_col=0)
        return spec1

    if filename[1] == "txt":
        spec1 = pd.read_csv(filename[0], header=None, index_col=0, sep=" ")
        return spec1


## The object must be easy to use even without the frontend
class twoDspecies:
    def __init__(self, filename1: (list, str), filename2: (list, str) = '',
                 ref: str = 'mean', output: bool = False, method: str = "HT"):

        '''
        Two-dimensionl spectral correlation
        Parameters .... the documentation should be completed
        '''

        if filename2 == "":
            filename2 = filename1

        if isinstance(filename1, str):
            filename1 = [filename1, filename1.split('.')[-1]]
        if isinstance(filename2, str):
            filename2 = [filename2, filename2.split('.')[-1]]

        spec1 = reader(filename1)
        spec1 = checkHeader(spec1)

        spec2 = reader(filename2)
        spec2 = checkHeader(spec2)

        ## it needs to be check that the discretizations points
        ## in the perturbation variables are the same

        '''
        if not all(spec1.columns == spec2.columns):
            ## Raise an error handler
            print(error)
            return None
        '''

        # obtain the mean, max, min, and quartiles for each wave number
        # along the perturbation samples
        self.describe1 = spec1.transpose().describe().transpose()
        self.describe2 = spec2.transpose().describe().transpose()

        # creates the dynamic spectrum depending of the choosen reference
        if ref == 'zero':
            self.spec1 = spec1
            self.spec2 = spec2
        elif ref == 'mean':
            self.spec1 = spec1.sub(self.describe1['mean'], axis=0)
            self.spec2 = spec2.sub(self.describe2['mean'], axis=0)
        elif ref == 'min':
            self.spec1 = spec1.sub(self.describe1['min'], axis=0)
            self.spec2 = spec2.sub(self.describe2['min'], axis=0)
        elif ref == 'max':
            self.spec1 = spec1.sub(self.describe1['max'], axis=0)
            self.spec2 = spec2.sub(self.describe2['max'], axis=0)
        elif ref == 'ini':
            self.spec1 = spec1.sub(spec1[1], axis=0)
            self.spec2 = spec2.sub(spec2[1], axis=0)
        elif ref == 'end':
            self.spec1 = spec1.sub(spec1[spec1.columns[-1]], axis=0)
            self.spec2 = spec2.sub(spec1[spec1.columns[-1]], axis=0)

        # self.syncr = self.syn(output)
        # self.asyncr = self.asyn(output)
        # self.syn(output)
        # self.asyn(output)


    def noda(self):
        nn = len(self.spec1.columns)
        ## The actual values are calculated only once
        fill_pattern = [1. / (np.pi * float(i)) if i != 0 else 0. for i in range(nn)]
        noda_matrix = np.empty((nn, nn), dtype=float)
        for i in range(nn):
            noda_matrix[i, :] = [-fill_pattern[i - j] for j in range(i)] + [fill_pattern[j] for j in range(nn - i)]

        return noda_matrix

    def syn(self, output: bool = False, method: str = "HT"):
        # I'm not sure about transposing at the end. x's are the indexes and y's the columns

        if method == "HT":
            self.syncr = pd.DataFrame(self.spec1.values @ self.spec2.values.T / float(len(self.spec1.columns) - 1),
                                      index=self.spec1.index,
                                      columns=self.spec2.index)  # .transpose()
            # sync.index = self.spec1.columns
            # sync.columns = self.spec2.columns
            # sync = sync.T    # It is supposed to be symmetric
        elif method == "FFT":
            pass

        if output:
            self.syncr.to_csv("sync.csv")

    def asyn(self, output: bool = False, method: str = "HT"):
        # I'm not sure about transposing at the end. x's are the indexes and y's the columns

        if method == "HT":
            self.asyncr = pd.DataFrame(
                self.spec1.values @ self.noda() @ self.spec2.values.T / (len(self.spec1.columns) - 1),
                index=self.spec1.index,
                columns=self.spec2.index)  # .transpose()
            # asyn.index = self.spec1.columns
            # asyn.columns = self.spec2.columns
            # asyn = asyn.T

        elif method == "FFT":
            pass

        if output:
            self.asyncr.to_csv("async.csv")

    # For now we do it hard wired
    def plot_sync(self):

        fig = plt.figure(figsize=(9, 9))
        gs = mpl.gridspec.GridSpec(3, 2, width_ratios=[2, 5], height_ratios=[2, 5, 2], wspace=0.03, hspace=0.05)
        fontsize = 8
        # keys to name the panels
        keys = ['central', 'upper', 'lefter', 'lower']
        # proportion of the grids, to be able to iterates
        indices = [[1, 1], [0, 1], [1, 0], [2, 1]]
        panels = {}
        # Creating the panels. This is done just one
        for i in range(len(keys)):
            j, k = indices[i]
            panels[keys[i]] = fig.add_subplot(gs[j, k])
            panels[keys[i]].tick_params(
                axis='both',  # changes apply to the x-axis
                which='both',  # both major and minor ticks are affected
                bottom=False,  # ticks along the bottom edge are off
                top=False,  # ticks along the top edge are off
                right=False,  # ticks along the right edge are off
                left=False,  # ticks along the left edge are off
                labelbottom=False,  # labels along the bottom edge are off
                labelleft=False)  # labels along the left edge are off
        # Setting particularly the lefter panel
        panels['lefter'].invert_xaxis()
        # panels['lefter'].invert_yaxis()

        # Plotting the information...
        # panels['upper'].plot(num_wave,spect)
        num_wave = self.describe1.index
        data_trans = self.describe1
        panels['upper'].plot(num_wave, data_trans['mean'], label='Mean')
        panels['upper'].fill_between(num_wave, data_trans['min'], data_trans['max'], alpha=0.3, label='min-max')
        panels['upper'].fill_between(num_wave, data_trans['25%'], data_trans['75%'], alpha=0.6, label='Q25-Q75')
        panels['upper'].legend(loc='best', fontsize=fontsize)
        panels['upper'].set_xlim(num_wave.min(), num_wave.max())

        num_wave = self.describe2.index
        data_trans = self.describe2
        panels['lefter'].plot(data_trans['mean'], num_wave, label='Mean')  ## Attention! The data is inverted
        panels['lefter'].fill_betweenx(num_wave, data_trans['min'], data_trans['max'], alpha=0.3, label='min-max')
        panels['lefter'].fill_betweenx(num_wave, data_trans['25%'], data_trans['75%'], alpha=0.6, label='Q25-Q75')
        panels['lefter'].legend(loc='best', fontsize=fontsize)
        panels['lefter'].set_ylim(num_wave.min(), num_wave.max())

        # Setting the central and lower panels

        data = self.syncr.values
        num_wave = self.syncr.index
        num_wave2 = self.syncr.columns
        # This test only plot the diagonal of sync 2D corr
        panels['lower'].plot(num_wave, data.diagonal(0))
        panels['lower'].axhline(y=0., color='k', alpha=0.4)
        panels['lower'].set_xlim(num_wave.min(), num_wave.max())

        # breakpoint()    # for debugging
        zmin = data.min()
        zmax = data.max()

        num_contour = 12
        imshow_kwargs = {
            'vmax': zmax,
            'vmin': zmin,
            'cmap': "bwr",
            'extent': (num_wave[0], num_wave[-1], num_wave2[0], num_wave2[-1]),
        }
        panels['central'].imshow(data[::-1,::], alpha=0.6, **imshow_kwargs)
        panels['central'].contour(num_wave, num_wave2, data, num_contour, cmap=None, vmin=zmin, vmax=zmax,
                                  alpha=1.0, colors='black')
        panels['central'].plot(num_wave, num_wave2, linewidth=1.5, alpha=0.4)
        # plt.xlabel("X axis")
        # plt.ylabel("Y axis")
        panels['central'].set_xlim(num_wave.min(), num_wave.max())
        panels['central'].set_ylim(num_wave2.min(), num_wave2.max())

        # plt.show()
        return panels

    # For now we do it hard wired
    def plot_async(self):

        fig = plt.figure(figsize=(9, 9))
        gs = mpl.gridspec.GridSpec(3, 3, width_ratios=[2, 5, 0.25], height_ratios=[2, 5, 2], wspace=0.05, hspace=0.05)
        fontsize = 8
        # keys to name the panels
        keys = ['central', 'upper', 'lefter', 'lower']
        # proportion of the grids, to be able to iterates
        indices = [[1, 1], [0, 1], [1, 0], [2, 1]]
        panels = {}
        # Creating the panels. This is done just one
        for i in range(len(keys)):
            j, k = indices[i]
            panels[keys[i]] = fig.add_subplot(gs[j, k])
            panels[keys[i]].tick_params(
                axis='both',  # changes apply to the x-axis
                which='both',  # both major and minor ticks are affected
                bottom=False,  # ticks along the bottom edge are off
                top=False,  # ticks along the top edge are off
                right=False,  # ticks along the right edge are off
                left=False,  # ticks along the left edge are off
                labelbottom=False,  # labels along the bottom edge are off
                labelleft=False)  # labels along the left edge are off
        # Setting particularly the lefter panel
        panels['lefter'].invert_xaxis()
        # panels['lefter'].invert_yaxis()

        # Plotting the information...
        # panels['upper'].plot(num_wave,spect)
        num_wave = self.describe1.index
        data_trans = self.describe1
        panels['upper'].plot(num_wave, data_trans['mean'], label='Mean');
        panels['upper'].fill_between(num_wave, data_trans['min'], data_trans['max'], alpha=0.3, label='min-max');
        panels['upper'].fill_between(num_wave, data_trans['25%'], data_trans['75%'], alpha=0.6, label='Q25-Q75');
        panels['upper'].legend(loc='best', fontsize=fontsize)
        panels['upper'].set_xlim(num_wave.min(), num_wave.max())

        num_wave = self.describe2.index
        data_trans = self.describe2
        panels['lefter'].plot(data_trans['mean'], num_wave, label='Mean')  ## Attention! The data is inverted
        panels['lefter'].fill_betweenx(num_wave, data_trans['min'], data_trans['max'], alpha=0.3, label='min-max');
        panels['lefter'].fill_betweenx(num_wave, data_trans['25%'], data_trans['75%'], alpha=0.6, label='Q25-Q75');
        panels['lefter'].legend(loc='best', fontsize=fontsize)
        panels['lefter'].set_ylim(num_wave.min(), num_wave.max())

        # Setting the central and lower panels
        data = self.asyncr.values
        num_wave = self.asyncr.index
        num_wave2 = self.asyncr.columns
        # This test only plot the diagonal of sync 2D corr
        panels['lower'].plot(num_wave, np.flip(np.fliplr(data).diagonal(0)))
        panels['lower'].axhline(y=0., color='k', alpha=0.4)
        panels['lower'].set_xlim(num_wave.min(), num_wave.max())

        #breakpoint()    # for debugging
        zmin = data.min()
        zmax = data.max()

        num_contour = 12
        imshow_kwargs = {
            'vmax': zmax,
            'vmin': zmin,
            'cmap': "bwr",
            'extent': (num_wave[0], num_wave[-1], num_wave2[0], num_wave2[-1]),
        }
        im = panels['central'].imshow(data[::-1,::], alpha=0.6, **imshow_kwargs)
        panels['central'].contour(num_wave, num_wave2, data, num_contour, cmap=None, vmin=zmin, vmax=zmax,
                                  alpha=1.0, colors='black')
        panels['central'].plot(num_wave, num_wave2[::-1], linewidth=1.5, alpha=0.4)
        # plt.xlabel("X axis")
        # plt.ylabel("Y axis")
        panels['central'].set_xlim(num_wave.min(), num_wave.max())
        panels['central'].set_ylim(num_wave2.min(), num_wave2.max())
        cax = plt.axes( fig.add_subplot(gs[1,2]) )
        cb = plt.colorbar(im, cax=cax)
        cb.ax.yaxis.set_tick_params(labelright=True)

        plt.show()
        return panels
