# project name: pyranometer
# created by diego aliaga daliaga_at_chacaltaya.edu.bo
import Database
import UserPlot

def get_databases(parameters, global_pars):
    databases = dict()
    for db_name in parameters['databases'].keys():
        db_dic = parameters['databases'][db_name]
        databases[db_name] = Database.Database(
                dic=db_dic,
                user_plot=global_pars
        )
    return databases

def get_plots(parameters):
    shared_ranges = UserPlot.SharedRanges(parameters)
    plots = dict()
    for plot_name in parameters['plots'].keys():
        plot_dic = parameters['plots'][plot_name]
        plots[plot_name] = UserPlot.UserPlot(
                name=plot_name,
                dic=plot_dic,
                parameters_dic=parameters,
                shared_ranges=shared_ranges
        )
    return plots
