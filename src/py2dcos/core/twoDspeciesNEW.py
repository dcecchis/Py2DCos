#!/usr/bin/env python

import numpy as np
import matplotlib as mpl
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objs as go
#from mpl_toolkits.mplot3d import Axes3D
#from sklearn.decomposition import PCA
from scipy.interpolate import RegularGridInterpolator
from scipy.ndimage import gaussian_filter
import matplotlib.ticker as ticker


def reader(filename):
    if filename[1] == "csv":
        spec1 = pd.read_csv(filename[0], header=None, index_col=0)
        return spec1

    if filename[1] == "xlsx":
        ## The default option (only the matrix)
        # try:
        sheet, row, column = filename[-4:-1]
        row = int(row)
        skipRows = row - 1
        spec1 = pd.read_excel(filename[0], header=None, index_col=0, sheet_name=sheet, usecols=column,
                              skiprows=skipRows)

        if filename[-1] == True:  # check if columns are labeled
            firstCol = column.split(':')[0]  # first column of the column range
            nextCol = chr(
                ord(firstCol) + 1)  # get the following column, because the heading of the wavenumber column isnt relevant
            colRange = nextCol + column[1:]
            labels = pd.read_excel(filename[0], header=None, sheet_name=sheet, usecols=colRange, skiprows=skipRows - 1,
                                   nrows=1).values[0]
            if checklabels(labels):  # checks if labels are numbers and if they are equally spaced
                spec1 = interp(spec1, labels)
            else:
                pass

        # except:
        # spec1 = pd.read_excel(filename[0], header=None, index_col=0)

        # spec1 = pd.read_excel(filename[0], header=0, index_col=0)
        return spec1

    if filename[1] == "txt":
        spec1 = pd.read_csv(filename[0], header=None, index_col=0, sep=" ")
        return spec1


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


def checklabels(labelRow):  # checks if labels are numbers and if they are equally spaced
    if all(isinstance(element, (int, float)) for element in labelRow):  # check if labels are only nums
        differences = [labelRow[i + 1] - labelRow[i] for i in range(len(labelRow) - 1)]
        eqSpaced = not all(differences[0] == diff for diff in differences)  # checks if nums are equally spaced
        return eqSpaced
    else:
        return False


def interp(df, spacing):
    new_spacing = np.linspace(spacing[0], spacing[-1], len(spacing))
    df.columns = spacing

    for column in new_spacing:
        a = column not in df.columns
        if column not in df.columns:
            df[column] = np.nan

    df = df.sort_index(axis=1)
    df = df.interpolate(axis=1, method='index')

    for column in df.columns:
        if column not in new_spacing:
            df = df.drop(column, axis=1)

    return df


## The object must be easy to use even without the frontend

# a filename

class twoDspecies:
    def __init__(self, filename1: (list, str), filename2: (list, str) = '',
                 ref: str = 'ini', output: bool = False, method: str = "HT",
                 sigma_gaussian=0,
                 reconstruction_comps=0,
                 node_attenuation=False):

        '''
        Two-dimensionl spectral correlation
        Parameters .... the documentation should be completed
        '''

        self.canvas_ = None
        self.node_attenuation_bool = node_attenuation

        # if there is no second file, then copy the first
        if filename2 == "":
            filename2 = filename1

        if isinstance(filename1, str):
            filename1 = [filename1, filename1.split('.')[-2]]
        if isinstance(filename2, str):
            filename2 = [filename2, filename2.split('.')[-2]]

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

        if reconstruction_comps > 0:  # check if pca reconstruction is necessary
            spec1 = self.apply_pca_reconstruction(spec1, reconstruction_comps, scores_filename="spec1Scores.png")
            spec2 = self.apply_pca_reconstruction(spec2, reconstruction_comps, scores_filename="spec2Scores.png")

        if sigma_gaussian != 0:
            spec1 = self.apply_gaussian_filter(spec1, sigma_gaussian)
            spec2 = self.apply_gaussian_filter(spec2, sigma_gaussian)

        if node_attenuation:
            spec1 = self.apply_node_attenuation(spec1)
            spec2 = self.apply_node_attenuation(spec2)

        # obtain the mean, max, min, and quartiles for each wave number
        # along the perturbation samples
        self.describe1 = spec1.transpose().describe().transpose()
        self.describe2 = spec2.transpose().describe().transpose()

        self.first1 = spec1[1]
        self.first2 = spec2[1]
        self.last1 = spec1[spec1.columns[-2]]
        self.last2 = spec2[spec2.columns[-2]]

        # creates the dynamic spectrum depending on the choosen reference
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
            self.spec2 = spec2.sub(spec2[spec2.columns[-1]], axis=0)

        self.syncr = None
        self.asyncr = None
        # self.syn(output)
        # self.asyn(output)

    #  Here the object must change if we need to implement the fft version of the
    #  2D correlation. i.e, you ask for calculate from noda, or not because using
    #  fft, requires to complex calculations

    def apply_pca_reconstruction(self, data, n_components,
                                 report_filename="PCA_Report.txt",
                                 plot_correlogram=True, correlogram_filename='correlograma.png',
                                 plot_scores=True, scores_filename='scores.png'):

        # Center the data by subtracting column means.
        data_mean = data.mean()
        data_centered = data - data_mean

        from sklearn.decomposition import PCA
        pca = PCA(n_components=n_components)
        pca_result = pca.fit_transform(data_centered)

        # Reconstruct the data using the retained components.
        reconstructed = pca.inverse_transform(pca_result)
        reconstructed_df = pd.DataFrame(reconstructed, index=data.index, columns=data.columns)

        # Compute the correlation matrix of the reconstructed data.
        correlation_matrix = np.corrcoef(reconstructed_df.T)

        # Calculate explained variance statistics.
        explained_variance = pca.explained_variance_ratio_ * 100  # as percentages
        cumulative_variance = np.cumsum(explained_variance)

        # Generate a textual report.
        report_lines = []
        report_lines.append("PCA Report")
        report_lines.append("=" * 40)
        report_lines.append(f"Number of components used: {n_components}")
        report_lines.append("")
        report_lines.append("Explained Variance Ratio (%):")
        for i, ev in enumerate(explained_variance):
            report_lines.append(f"  PC{i + 1}: {ev:.2f}%")
        report_lines.append("")
        report_lines.append("Cumulative Variance (%):")
        for i, cv in enumerate(cumulative_variance):
            report_lines.append(f"  PCs 1 to {i + 1}: {cv:.2f}%")
        report_lines.append("")
        report_lines.append("Component Weights (Loadings):")
        for i, comp in enumerate(pca.components_):
            comp_str = ", ".join([f"{w:.4f}" for w in comp])
            report_lines.append(f"  PC{i + 1}: [{comp_str}]")
        report_text = "\n".join(report_lines)

        with open(report_filename, "w") as f:
            f.write(report_text)
        print(f"PCA report saved to {report_filename}")

        # Plot the correlogram (correlation matrix) if requested.
        if plot_correlogram:
            import matplotlib.pyplot as plt
            plt.figure(figsize=(8, 6))
            plt.imshow(correlation_matrix, cmap='coolwarm', interpolation='nearest')
            plt.colorbar()
            plt.title("Correlogram of Reconstructed Data")
            plt.xlabel("Variables")
            plt.ylabel("Variables")
            plt.tight_layout()
            if correlogram_filename:
                plt.savefig(correlogram_filename)
                print(f"Correlogram saved as {correlogram_filename}")
            else:
                plt.show()
            plt.close()

        # Plot the PCA scores if requested and if at least 2 components are available.
        if plot_scores:
            if n_components < 2:
                print("PCA scores plot not generated: need at least 2 components.")
            else:
                fig, ax = plt.subplots(figsize=(8, 6))

                # Plot the scores.
                ax.scatter(pca_result[:, 0], pca_result[:, 1], color='blue', marker='o')
                ax.set_xlabel(f"PC1 ({explained_variance[0]:.1f}% var)")
                ax.set_ylabel(f"PC2 ({explained_variance[1]:.1f}% var)")
                ax.set_title("PCA Scores Scatter Plot")

                ax.spines['left'].set_position('zero')
                ax.spines['bottom'].set_position('zero')
                ax.spines['right'].set_color('none')
                ax.spines['top'].set_color('none')

                # Add grid for clarity
                ax.grid(True, linestyle='--', alpha=0.5)

                threshold = np.percentile(np.abs(pca_result[:, 0]), 90)  # for example, top 10% in PC1
                for i, wavenumber in enumerate(data.index):
                    if abs(pca_result[i, 0]) > threshold or abs(pca_result[i, 1]) > threshold:
                        ax.annotate(str(wavenumber),
                                    (pca_result[i, 0], pca_result[i, 1]),
                                    fontsize=8,
                                    ha='center',
                                    va='center',
                                    color='darkred',
                                    xytext=(3, 3),
                                    textcoords='offset points')

                plt.tight_layout()
                if scores_filename:
                    plt.savefig(scores_filename)
                    print(f"PCA scores plot saved as {scores_filename}")

                plt.close()

        return reconstructed_df

    def apply_node_attenuation(self, spec, a=5, lam=5, eps=1e-7):
        """
        Applies the node attenuation filter function to the spectral data.
        The filter is computed from the average spectrum of self.spec1
        (assumed to have wavenumbers as the index and perturbation spectra in the columns)
        and then applied to both self.spec1 and self.spec2.

        Parameters:
            a (float): Repeat factor (typically 1).
            lam (float): Parameter to adjust the shape of the resolved peak profiles.
            eps (float): Small regularization constant to avoid division by zero.
            use_common_filter (bool): If True, a single filter (from the average) is applied to all spectra.
        """
        wavenumbers = spec.index.astype(float).to_numpy()

        # Compute the average spectrum over all columns.
        avg_spec = spec.mean(axis=1).to_numpy()

        # Compute first and second derivatives with respect to wavenumbers.
        A_prime = np.gradient(avg_spec, wavenumbers)
        A_double = np.gradient(A_prime, wavenumbers)

        # Compute the node attenuation filter.
        N_filter = np.exp(
            -a * ((A_double * avg_spec) - eps) /
            (lam * (A_prime ** 2) + np.abs(A_double * avg_spec) + eps)
        )

        # Apply the filter along the spectral (row) axis and return the new DataFrame.
        attenuated_spec = spec.multiply(N_filter, axis=0)
        return attenuated_spec

    def apply_gaussian_filter(self, spec, sigma):
        """
        Applies a Gaussian filter to the spectral data to smooth high-frequency noise.

        By default, the smoothing is applied along the spectral (wavenumber) axis only.
        If self.spec1 and self.spec2 have rows corresponding to wavenumbers and columns
        corresponding to perturbation samples, then setting sigma as (sigma, 0) will smooth
        only along the spectral direction.

        Parameters:
            sigma (float): Standard deviation for the Gaussian kernel. If a scalar is provided,
                           the filter is applied along the rows (spectral axis) only.
        """
        if isinstance(sigma, (int, float)):
            sigma = (sigma, 0)

        # Apply Gaussian filter on the underlying NumPy array
        smoothed_array = gaussian_filter(spec.values, sigma=sigma)

        # Reconstruct the DataFrame with the same index and columns as the input
        return pd.DataFrame(smoothed_array, index=spec.index, columns=spec.columns)

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
                                      columns=self.spec2.index)
            # sync.index = self.spec1.columns
            # sync.columns = self.spec2.columns
            # sync = sync.T    # It is supposed to be symmetric
        # elif method == "FFT" and self.syncr is None

        # if self.node_attenuation_bool:
        # self.syncr = self.apply_node_attenuation(self.syncr)

        elif method == "FFT":
            # Chi = np.fft.fft(self.spec1.values, axis=1) @ np.fft.ifft(self.spec2.values, axis=1, norm='forward').T / (float(self.spec1.columns[-1] - self.spec1.columns[0] )*np.pi)
            xfft = np.fft.fft(self.spec1.values, axis=1) / (float(self.spec1.shape[1])) ** 0.5
            yfft = np.fft.fft(self.spec2.values, axis=0) / (float(self.spec2.shape[0])) ** 0.5
            X = xfft @ np.conj(yfft).T / float(self.spec1.shape[0])
            self.syncr = pd.DataFrame(np.real(X),
                                      index=self.spec1.index,
                                      columns=self.spec2.index)

        if output:
            self.syncr.to_csv("sync.csv")

    def asyn(self, output: bool = False, method: str = "HT"):
        # I'm not sure about transposing at the end. x's are the indexes and y's the columns

        # method = "FFT"
        print(self.spec1.shape, self.spec2.shape)

        if method == "HT":
            self.asyncr = pd.DataFrame(
                self.spec1.values @ self.noda() @ self.spec2.values.T / (len(self.spec1.columns) - 1),
                index=self.spec1.index,
                columns=self.spec2.index)  # .transpose()
            # asyn.index = self.spec1.columns
            # asyn.columns = self.spec2.columns
            # asyn = asyn.T

            # if self.node_attenuation_bool:
            # self.asyncr = self.apply_node_attenuation(self.asyncr)

        elif method == "FFT":
            # on development
            xfft = np.fft.fft(self.spec1.values, axis=1) / (float(self.spec1.shape[1])) ** 0.5
            yfft = np.fft.fft(self.spec2.values, axis=1) / (float(self.spec2.shape[1])) ** 0.5
            X = xfft @ np.conj(yfft).T / (self.spec1.shape[0] - 1)
            self.asyncr = pd.DataFrame(np.imag(X),
                                       index=self.spec1.index,
                                       columns=self.spec2.index)

        if output:
            self.asyncr.to_csv("async.csv")

    def defineLocator(self, locator_choice='linear', levels=6):
        locator = None
        if locator_choice=='linear':
            locator = ticker.LinearLocator(numticks=levels)
        elif locator_choice=='maxN':
            locator = ticker.MaxNLocator(nbins=levels)
        elif locator_choice=='log':
            locator = ticker.LogLocator(numticks=levels)

        return locator


    def plotFunction(self, corrType='homo', calcMethod='HT', refSpectra='ini', colorMap='coolwarm',
                     numOfContour=6, locator_choice='linear', syncDiag='main', asyncDiag='anti', xAxis='decreasing', colorMapIntensity=1.0,
                     colorLines='black', colorLinesIntensity=0.6, shownGraph='both', canvas=False, figure=None,
                     eqSpaced=True, peaks_signs='all'):
        if figure:
            figure.clear()

        locator = self.defineLocator(locator_choice, numOfContour)

        fontsize = 8
        linewidth = 0.9

        if figure == None:
            self.figure = plt.figure()
        else:
            self.figure = figure

        self.figure.set_facecolor("#f0f0f0")

        ## Synchronous Spectra
        if shownGraph == 'sync':
            func = RegularGridInterpolator((self.syncr.index, self.syncr.columns), self.syncr.values)

            def fmt(x, y):
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
            num_wave = self.describe1.index
            data_trans = self.describe1
            panels['upper'].plot(num_wave, self.first1, 'r-', label='First', linewidth=linewidth)
            panels['upper'].plot(num_wave, data_trans['mean'], label='Mean', linewidth=linewidth)
            panels['upper'].fill_between(num_wave, data_trans['min'], data_trans['max'], alpha=0.3)
            panels['upper'].plot(num_wave, self.last1, 'k-', label='Last', linewidth=linewidth)
            panels['upper'].legend(loc='best', fontsize=fontsize)
            panels['upper'].set_xlim(num_wave.min(), num_wave.max())

            num_wave = self.describe2.index
            data_trans = self.describe2
            panels['lefter'].plot(self.first2, num_wave, 'r-', label='First', linewidth=linewidth)
            panels['lefter'].plot(data_trans['mean'], num_wave, label='Mean',
                                  linewidth=linewidth)  ## Attention! The data is inverted
            panels['lefter'].fill_betweenx(num_wave, data_trans['min'], data_trans['max'], alpha=0.3)
            panels['lefter'].plot(self.last2, num_wave, 'k-', label='Last', linewidth=linewidth)
            panels['lefter'].legend(loc='best', fontsize=fontsize)
            panels['lefter'].set_ylim(num_wave.min(), num_wave.max())

            # Setting the central and lower panels
            data = self.syncr.values
            if peaks_signs == 'all':
                pass
            elif peaks_signs == 'positive':
                data[data < 0] = abs(data).min()
            elif peaks_signs == 'negative':
                data[data > 0] = abs(data).min()

            num_wave = self.syncr.index
            num_wave2 = self.syncr.columns

            panels['lower'].plot(num_wave, data.diagonal(0), linewidth=linewidth)
            panels['lower'].axhline(y=0., color='k', alpha=0.4)
            panels['lower'].set_xlim(num_wave.min(), num_wave.max())

            # breakpoint()    # for debugging
            zmin = data.min()
            zmax = data.max()

            imshow_kwargs = {
                'vmax': zmax,
                'vmin': zmin,
                'cmap': colorMap,
                'extent': (num_wave[0], num_wave[-1], num_wave2[0], num_wave2[-1]),
            }

            imA = panels['central'].imshow(data[::-1, ::], alpha=colorMapIntensity, aspect="auto", **imshow_kwargs)

            panels['central'].contour(num_wave, num_wave2, data, locator=locator, cmap=None, vmin=zmin, vmax=zmax,
                                      colors=colorLines, alpha=colorLinesIntensity, linewidths=linewidth)
            # panels['central'].contourf(num_wave, num_wave2, data, numOfContour, cmap=colorMap, alpha=colorMapIntensity)

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

            # plt.xlabel("X axis")
            # plt.ylabel("Y axis")
            panels['central'].set_xlim(num_wave.min(), num_wave.max())
            panels['central'].set_ylim(num_wave2.min(), num_wave2.max())

            if xAxis == "decreasing":
                panels['central'].invert_xaxis()

            # plt.tight_layout()

            if canvas:
                self.canvas_.figure = self.figure
                self.canvas_.draw()

            else:
                plt.show()


        elif shownGraph == 'async':
            func = RegularGridInterpolator((self.asyncr.columns, self.asyncr.index), self.asyncr.values)

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
            num_wave = self.describe1.index
            data_trans = self.describe1
            panels['upper'].plot(num_wave, self.first1, 'r-', label='First', linewidth=linewidth)
            panels['upper'].plot(num_wave, data_trans['mean'], label='Mean', linewidth=linewidth)
            panels['upper'].fill_between(num_wave, data_trans['min'], data_trans['max'], alpha=0.3)
            panels['upper'].plot(num_wave, self.last1, 'k-', label='Last', linewidth=linewidth)
            panels['upper'].legend(loc='best', fontsize=fontsize)
            panels['upper'].set_xlim(num_wave.min(), num_wave.max())

            num_wave = self.describe2.index
            data_trans = self.describe2
            panels['lefter'].plot(self.first2, num_wave, 'r-', label='First', linewidth=linewidth)
            panels['lefter'].plot(data_trans['mean'], num_wave, label='Mean',
                                  linewidth=linewidth)  ## Attention! The data is inverted
            panels['lefter'].fill_betweenx(num_wave, data_trans['min'], data_trans['max'], alpha=0.3)
            panels['lefter'].plot(self.last2, num_wave, 'k-', label='Last', linewidth=linewidth)
            panels['lefter'].legend(loc='best', fontsize=fontsize)
            panels['lefter'].set_ylim(num_wave.min(), num_wave.max())

            # Setting the central and lower panels
            data = self.asyncr.values
            if peaks_signs == 'all':
                pass
            elif peaks_signs == 'positive':
                data[data < 0] = abs(data).min()
            elif peaks_signs == 'negative':
                data[data > 0] = abs(data).min()

            num_wave = self.asyncr.index
            num_wave2 = self.asyncr.columns

            # This test only plot the diagonal of sync 2D corr
            # diagonal = np.flip(np.fliplr(data).diagonal(0))
            # .setflags(write=True)
            # diagonal[diagonal < 1E-15] = 0.
            # panels['lower'].plot(num_wave, diagonal)
            panels['lower'].plot(num_wave, np.flip(np.fliplr(data).diagonal(0)), linewidth=linewidth)
            panels['lower'].axhline(y=0., color='k', alpha=0.4)
            panels['lower'].set_xlim(num_wave.min(), num_wave.max())

            # breakpoint()    # for debugging
            zmin = data.min()
            zmax = data.max()

            imshow_kwargs = {
                'vmax': zmax,
                'vmin': zmin,
                'cmap': colorMap,
                'extent': (num_wave[0], num_wave[-1], num_wave2[0], num_wave2[-1]),
            }
            imA = panels['central'].imshow(data[::-1, ::], alpha=colorMapIntensity, aspect="auto", **imshow_kwargs)
            panels['central'].contour(num_wave, num_wave2, data, locator=locator, cmap=None, vmin=zmin, vmax=zmax,
                                      colors=colorLines, alpha=colorLinesIntensity, linewidths=linewidth)
            # panels['central'].contourf(num_wave, num_wave2, data, numOfContour, cmap=colorMap, alpha=colorMapIntensity)

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

            # plt.xlabel("X axis")
            # plt.ylabel("Y axis")
            panels['central'].set_xlim(num_wave.min(), num_wave.max())
            panels['central'].set_ylim(num_wave2.min(), num_wave2.max())

            if xAxis == "decreasing":
                panels['central'].invert_xaxis()

            # plt.tight_layout()

            if canvas:
                self.canvas_.figure = self.figure
                self.canvas_.draw()
            else:
                plt.show()


        elif shownGraph == 'both':
            func1 = RegularGridInterpolator((self.syncr.index, self.syncr.columns), self.syncr.values)
            func2 = RegularGridInterpolator((self.asyncr.index, self.asyncr.columns), self.asyncr.values)

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
            # panel_tick_params['central']['labelright'] = False  # labels right is off in central panel

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
            # panels['lefter'].invert_yaxis()

            # Plotting the information...
            # panels['upper'].plot(num_wave,spect)
            num_wave = self.describe1.index
            data_trans = self.describe1
            panels['upper'].plot(num_wave, self.first1, 'r-', label='First', linewidth=linewidth)
            panels['upper'].plot(num_wave, data_trans['mean'], label='Mean', linewidth=linewidth)
            panels['upper'].fill_between(num_wave, data_trans['min'], data_trans['max'], alpha=0.3)
            # panels['upper'].fill_between(num_wave, data_trans['25%'], data_trans['75%'], alpha=0.6, label='Q25-Q75')
            panels['upper'].plot(num_wave, self.last1, 'k-', label='Last', linewidth=linewidth)
            panels['upper'].legend(loc='best', fontsize=fontsize)
            panels['upper'].set_xlim(num_wave.min(), num_wave.max())

            panels['upper_right'].plot(num_wave, self.first1, 'r-', label='First', linewidth=linewidth)
            panels['upper_right'].plot(num_wave, data_trans['mean'], label='Mean', linewidth=linewidth)
            panels['upper_right'].fill_between(num_wave, data_trans['min'], data_trans['max'], alpha=0.3)
            panels['upper_right'].plot(num_wave, self.last1, 'k-', label='Last', linewidth=linewidth)
            panels['upper_right'].legend(loc='best', fontsize=fontsize)
            panels['upper_right'].set_xlim(num_wave.min(), num_wave.max())

            num_wave = self.describe2.index
            data_trans = self.describe2
            panels['lefter'].plot(self.first2, num_wave, 'r-', label='First', linewidth=linewidth)
            panels['lefter'].plot(data_trans['mean'], num_wave, label='Mean',
                                  linewidth=linewidth)  ## Attention! The data is inverted
            panels['lefter'].fill_betweenx(num_wave, data_trans['min'], data_trans['max'], alpha=0.3)
            panels['lefter'].plot(self.last2, num_wave, 'k-', label='Last', linewidth=linewidth)
            panels['lefter'].legend(loc='best', fontsize=fontsize)
            panels['lefter'].set_ylim(num_wave.min(), num_wave.max())

            # Setting the central and lower panels

            data = self.syncr.values
            if peaks_signs == 'all':
                pass
            elif peaks_signs == 'positive':
                data[data < 0] = abs(data).min()
            elif peaks_signs == 'negative':
                data[data > 0] = abs(data).min()

            num_wave = self.syncr.index
            num_wave2 = self.syncr.columns
            # This test only plot the diagonal of sync 2D corr
            panels['lower'].plot(num_wave, data.diagonal(0), linewidth=linewidth)
            panels['lower'].axhline(y=0., color='k', alpha=0.4)
            panels['lower'].set_xlim(num_wave.min(), num_wave.max())

            # breakpoint()    # for debugging
            zmin = data.min()
            zmax = data.max()

            imshow_kwargs = {
                'vmax': zmax,
                'vmin': zmin,
                'cmap': colorMap,
                'extent': (num_wave[0], num_wave[-1], num_wave2[0], num_wave2[-1])
            }
            panels['central'].contour(num_wave, num_wave2, data, locator=locator, cmap=None, vmin=zmin, vmax=zmax,
                                      colors=colorLines, alpha=colorLinesIntensity, linewidths=linewidth)
            # panels['central'].contourf(num_wave, num_wave2, data, numOfContour, cmap=colorMap, alpha=colorMapIntensity)
            # aspectIm = 4.8/5
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
            data = self.asyncr.values
            if peaks_signs == 'all':
                pass
            elif peaks_signs == 'positive':
                data[data < 0] = abs(data).min()
            elif peaks_signs == 'negative':
                data[data > 0] = -abs(data).min()

            num_wave = self.asyncr.index
            num_wave2 = self.asyncr.columns

            # This test only plot the diagonal of sync 2D corr
            panels['lower_right'].plot(num_wave, np.flip(np.fliplr(data).diagonal(0)))
            panels['lower_right'].axhline(y=0., color='k', alpha=0.4)
            panels['lower_right'].set_xlim(num_wave.min(), num_wave.max())

            # breakpoint()    # for debugging
            zmin = data.min()
            zmax = data.max()

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

            # gs.tight_layout(self.figure)
            # gs.subplots_adjust(left = 0.1, bottom = 0.1, right = 0.9, top = 0.9, wspace=0.4, hspace=0.4)

            # plt.tight_layout()
            if canvas:
                self.canvas_.figure = self.figure
                self.canvas_.draw()

            else:
                plt.show()

    def plot3D(self, colorMap='coolwarm'):

        """

        syncr3d = plt.figure()
        asyncr3d = plt.figure()

        #syncr
        ax = syncr3d.add_subplot(111, projection='3d')
        X, Y = np.meshgrid(self.syncr.index, self.syncr.columns)
        Z = self.syncr.values
        ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap= colorMap)
        ax.set_xlabel('wavenumber')
        ax.set_ylabel('wavenumber')
        ax.set_title('Synchronous surface')
        syncr3d.show()

        #asyncr
        ax = asyncr3d.add_subplot(111, projection='3d')
        X, Y = np.meshgrid(self.asyncr.index, self.asyncr.columns)
        Z = self.asyncr.values
        ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap= colorMap)
        ax.set_xlabel('wavenumber')
        ax.set_ylabel('wavenumber')
        ax.set_title('Asynchronous surface')
        asyncr3d.show()

        """
        fig = go.Figure(data=[go.Surface(x=self.syncr.index, y=self.syncr.columns, z=self.syncr.values)])

        fig.update_layout(title='Synchronous Spectra',
                          margin=dict(l=65, r=50, b=65, t=90))

        fig.show()

        fig2 = go.Figure(
            data=[go.Surface(x=self.asyncr.index, y=self.asyncr.columns, z=self.asyncr.values)])

        fig2.update_layout(title='Asynchronous Spectra',
                           margin=dict(l=65, r=50, b=65, t=90))
        """
        fig2.update_layout(title='Asynchronous Spectra', autosize=False,
                          width=1000, height=1000,
                          margin=dict(l=65, r=50, b=65, t=90))
        """
        fig2.show()
