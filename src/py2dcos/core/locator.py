def define_locator(locator_choice='linear', levels=6):
    from matplotlib import ticker

    # map choices to ticker constructors
    locator_map = {
        'linear': lambda: ticker.LinearLocator(numticks=levels),
        'maxN':   lambda: ticker.MaxNLocator(nbins=levels),
        'log':    lambda: ticker.LogLocator(numticks=levels),
    }

    # reject unsupported choices
    if locator_choice not in locator_map:
        raise ValueError(f"Unsupported locator choice: '{locator_choice}'")

    # return the requested locator instance
    return locator_map[locator_choice]()
