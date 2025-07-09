# default GUI and processing settings
initial_status = {
            'sigmaGaussian': 0,
            'node_attenuation': False,
            'corrType': 'homo',
            'calcMethod': 'HT',
            'refSpectra': 'ini',
            'colorMap': 'coolwarm',
            'numOfContour': 6,
            'locator_choice': 'linear',
            'syncDiag': 'main',
            'asyncDiag': 'main',
            'xAxis': 'decreasing',
            'colorMapIntensity': 1.0,
            'colorLines': 'black',
            'colorLinesIntensity': 0.6,
            'shownGraph': 'both',
            'canvas': True,
            'figure': "",
            'reconstruction_components': 0,
            'peaks_signs': 'all'
        }

# supported line colors for plotting
color_list = ["navy", 'black', "white", "red", "lime", "blue", "yellow", "maroon", "olive",
              "green", "teal"]
# supported Matplotlib colormaps
cmap_list = ['bwr', 'PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu', 'RdYlBu',
             'RdYlGn', 'Spectral', 'coolwarm', 'seismic']

# available tick locator options
locators = ['linear', 'maxN', 'log']

