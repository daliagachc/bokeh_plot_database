from bokeh_plot_database.App import App
tb1 = 'uv_lfa'

#region parameters
parameters = {
    # region databases
    'databases':
        {
            # region tb1
            tb1:
                {
                    'database_name': tb1,
                    'user': tb1,
                    'psw': tb1,
                    'table': tb1,
                    'time_column_name': 'datetime',
                    'y_columns': {
                        'irradiance': {
                            'sql_name': 'irradiance',
                            'show_name': 'Irradiance',
                            'units': "W/m^2",
                            'color': 'black',
                            # 'function': '(0 * x + 1)'
                        }

                    }
                    ,
                    'ip': '10.8.3.1'
                }
            # endregion
        }
    # endregion
    ,
    # region plots
    'plots':
        {
            tb1: {
                'title': 'UVB en el LFA-UMSA La Paz-Bolivia',
                'databases_ref': [tb1]
            }
        }
    # endregion
    ,
    'plot_global_pars':
    # region plot_global_pars
        {
            'utc_offset_hours': -4,
            'utc_offset_enabled': True,
            'max_points_plots': 500,
            'first_interval_hours': 24,
            'width': 800,
            'height': 300,
            'webgl': False
        }
    # endregion
    ,
    'connected_plots': []

}
#endregion

App(parameters)

