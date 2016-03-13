# project name: pyranometer
# created by diego aliaga daliaga_at_chacaltaya.edu.bo
# import os
# import sys
#
# # script_dir = os.path.dirname(os.path.realpath(__file__))
# # sys.path.append(script_dir)

# import constants as cs
import bokeh_plot_database.functions as functions
from bokeh.io import curdoc, vplot
import my_logger

logger = my_logger.get_logger(name=__name__, level="DEBUG")


class App(object):
    def __init__(self, parameters):

        user_plots = functions.get_plots(parameters)

        plots = []

        for p in user_plots.itervalues():
            plots.append(p.plot)

        def update():

            for user_plot in user_plots.itervalues():
                user_plot.update()

        curdoc().add_periodic_callback(update, 1000)

        curdoc().add_root(
                vplot(
                        # button
                        *plots

                )
        )
