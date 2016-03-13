from bokeh_plot_database.App import App
tb1 = 'uv_lfa'
tb = 'pyra_borrar'
parameters = {
    'databases':
    # region databases
        {
            tb1:
            # region
                {
                    'database_name': tb1,
                    'user': tb1,
                    'psw': tb1,
                    'table': tb1,
                    'time_column_name': 'datetime',
                    'y_columns': {
                        'irradiance': {
                            'sql_name': 'volts',
                            'show_name': 'irradiance',
                            'units': "W/m^2",
                            'color': 'black',

                            'function': 'x/(2*2)'
                        }

                    }
                    ,
                    'ip': '10.8.3.1'
                }
            # endregion
            ,
            'date':
            # region
                {
                    'database_name': 'borrar',
                    'user': 'root',
                    'psw': '1045',
                    'table': tb,
                    'time_column_name': 'datetime',
                    'y_columns': {
                        'volts': {
                            'sql_name': 'volts',
                            'show_name': 'volts1',
                            'units': "",
                            'color': 'black',
                            'function': '(0 * x + 1)'
                        }

                    }
                    ,
                    'ip': 'localhost'
                }
            # endregion
            ,

            'date1':
            # region
                {
                    'database_name': 'borrar',
                    'user': 'root',
                    'psw': '1045',
                    'table': tb,
                    'time_column_name': 'datetime',
                    'y_columns': {
                        'volts': {
                            'sql_name': 'volts',
                            'show_name': 'volts2',
                            'units': "",
                            'color': 'black',
                            'function': '(0 * x + 2)'
                        }

                    }
                    ,
                    'ip': 'localhost'
                }
            # endregion
        }
    # endregion
    ,
    'plots':
    # region plots
        {
            tb1: {
                'title': tb1,
                'databases_ref': [tb1]

            }
            ,

            'date': {
                'title': 'date',
                'databases_ref': ['date', 'date1'],

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
    'connected_plots': [
        ('uv_lfa', 'date')
    ]

}

App(parameters)

