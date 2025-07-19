def define_locator(locator_choice='linear', levels=6):
    from matplotlib import ticker

    # map each supported choice to a factory for the corresponding locator
    locator_map = {
        'linear': lambda: ticker.LinearLocator(numticks=levels),
        'maxN':   lambda: ticker.MaxNLocator(nbins=levels),
        'log':    lambda: ticker.LogLocator(numticks=levels),
    }

    # ensure user picks one of the known locator algorithms
    if locator_choice not in locator_map:
        raise ValueError(f"unsupported locator choice: '{locator_choice}'")

    # create and return the locator so plotting code stays concise
    return locator_map[locator_choice]()
