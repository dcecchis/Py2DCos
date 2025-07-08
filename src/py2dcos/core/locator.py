from matplotlib import ticker

def define_locator(locator_choice='linear', levels=6):

    locator_map = {
        'linear': lambda: ticker.LinearLocator(numticks=levels),
        'maxN':   lambda: ticker.MaxNLocator(nbins=levels),
        'log':    lambda: ticker.LogLocator(numticks=levels),
    }

    if locator_choice not in locator_map:
        raise ValueError(f"Unsupported locator choice: '{locator_choice}'")

    return locator_map[locator_choice]()
