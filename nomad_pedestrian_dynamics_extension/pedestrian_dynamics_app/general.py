

from nomad.config.models.plugins import AppEntryPoint
from nomad.config.models.ui import App, Column, Columns, FilterMenu, FilterMenus, Filters


pdapp = AppEntryPoint(
    name='PedestrianDynamicsApp',
    description='App for pedestrian dynamics plugins.',
    app = App(
        # Label of the App
        label='PedestrianDynamicsApp',
        # Path used in the URL, must be unique
        path='pedestrian_dynamics_app',
        # Used to categorize apps in the explore menu
        category='Theory',
        # Brief description used in the app menu
        description='An app customized for pedestrian dynamics data bases.',
        # Longer description that can also use markdown
        readme='The app ensures that only pedestrian dynamics specific data is displayed.',
        # Controls the available search filters. If you want to filter by
        # quantities in a schema package, you need to load the schema package
        # explicitly here. Note that you can use a glob syntax to load the
        # entire package, or just a single schema from a package.
        filters=Filters(
            include=['*#nomad_pedestrian_dynamics_extension.vadere_schema.simulation.Simulation'],
        ),
        # Controls which columns are shown in the results table
        columns=Columns(
            selected=[
                'entry_id'
                'data.simulation#nomad_pedestrian_dynamics_extension.vadere_schema.simulation.Simulation'
            ],
            options={
                'entry_id': Column(),
                'upload_create_time': Column(),
                'data.simulation#nomad_pedestrian_dynamics_extension.vadere_schema.simulation.Simulation': Column(),
            }
        ),
        # Dictionary of search filters that are always enabled for queries made
        # within this app. This is especially important to narrow down the
        # results to the wanted subset. Any available search filter can be
        # targeted here. This example makes sure that only entries that use
        # MySchema are included.
        filters_locked={
            "section_defs.definition_qualified_name:all": [
                "nomad_pedestrian_dynamics_extension.vadere_schema.simulation.Simulation"
            ]
        },
        # Controls the filter menus shown on the left
        filter_menus=FilterMenus(
            options={
                'material': FilterMenu(label="Material"),
            }
        ),
        # Controls the default dashboard shown in the search interface
        dashboard={
            'widgets': [
                {
                    'type': 'histogram',
                    'showinput': False,
                    'autorange': True,
                    'nbins': 30,
                    'scale': 'linear',
                    'quantity': 'data.simulation#nomad_pedestrian_dynamics_extension.vadere_schema.simulation.Simulation',
                    'layout': {
                        'lg': {
                            'minH': 3,
                            'minW': 3,
                            'h': 4,
                            'w': 12,
                            'y': 0,
                            'x': 0
                        }
                    }
                }
            ]
        }
    )
)