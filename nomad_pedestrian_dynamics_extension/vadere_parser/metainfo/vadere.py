
import numpy as np
from nomad.datamodel import ArchiveSection, EntryData
from nomad.datamodel.metainfo.plot import PlotlyFigure, PlotSection
from nomad.datamodel.metainfo.workflow import Workflow
from nomad.datamodel.results import Properties
from nomad.datamodel.results import Results
from nomad.metainfo import Datetime, Package, Quantity,  Section, SubSection, MSection
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots

m_package = Package(name='vadere_nomadmetainfo_json', description='None')


class PsychologyModel(ArchiveSection):

    m_def = Section()


    perception_model = Quantity(
        type=str, description="""Name of the perception model"""
    )

    cognition_model = Quantity(
        type=str, description="""Name of the cognition model"""
    )



class Model(ArchiveSection):
    m_def = Section()

    locomotion_model = Quantity(
        type=str, description="""Locomotion model"""
    )

    psychology_model = SubSection(
        sub_section=PsychologyModel, description="""Psychological model"""
    )

    time_step_size = Quantity(
        type=np.float64,
        description="""Time between two evaluations of the simulation loop.""",
        unit='s'
    )



class Scenario(ArchiveSection):

    m_def = Section()

    number_of_sources = Quantity(
        type = np.int64, description="""Number of sources where agents are spawned."""
    )

    number_of_targets = Quantity(
        type=np.int64, description="""Number of targets."""
    )

    dimensions = Quantity(
        type=np.float64,
        shape=[2] ,
        description="""Outer dimension of the topography (width x height).""",
        unit='m'
    )

    origin_destination_matrix = Quantity(
        type=np.float64, shape=['number_of_sources', 'number_of_targets'], description="""Origin destination matrix."""
    )


class Output(ArchiveSection):
    m_def = Section()


    position = Quantity(
        type=np.float64,
        shape=['1...*',3],
        description="""Trajectories of the pedestrians.""",
    )


class Simulation(ArchiveSection):
    m_def = Section()

    software_name = Quantity(
        type=str, description="""Name of the software used for the simulation."""
    )

    software_release = Quantity(type=str, description="""Software release.""")

    date = Quantity(type=Datetime, description="""Start time of the execution.""")

    model = SubSection(sub_section=Model, description="""Simulation model.""")

    output = SubSection(sub_section=Output, description="""Simulation output.""")

    seed = Quantity(type = np.int64, description="""Simulation seed""",
    )

    total_simulation_time = Quantity(
        type = np.float64,
        description="""Total simulation time""",
    )




class MicroscopicResults(ArchiveSection):

    m_def = Section()


    trajectories = Quantity(
        type=np.float64,
        shape=['1...*',3],
        description="""DUMMY.""",
        default=[[1,2,4],[1,2,2]]
    )

    testdata1= Quantity(
        type=np.float64,
        description="""DUMMY.""",
        default = 1.234
    )




class DensitiesAndVelocities(PlotSection):

    m_def = Section()

    time = Quantity(
        type=np.float64,
        description="""Point of time""",
    )

    densities = Quantity(
        type=np.float64,
        shape=['1...*', '1...*'],
        description="""Densities""",
    )

    velocities = Quantity(
        type=np.float64,
        shape=['1...*', '1...*' ],
        description="""Velocities""",
    )


    def normalize(self, archive, logger):

        super(DensitiesAndVelocities, self).normalize(archive, logger)

        heatmap = go.Heatmap(z=self.densities, showscale=False, connectgaps=True, zsmooth='best')
        figure1 = go.Figure(data=heatmap)
        figure_json = figure1.to_plotly_json()
        self.figures.append(PlotlyFigure(label='Density', index=0, figure=figure_json))

        heatmap = go.Heatmap(z=self.velocities, showscale=False, connectgaps=True, zsmooth='best')
        figure2 = go.Figure(data=heatmap)
        figure_json = figure2.to_plotly_json()

        self.figures.append(PlotlyFigure(label='Velocity', index=1, figure=figure_json))


class MacroscopicResults(ArchiveSection):

    m_def = Section()

    spatial_resolution = Quantity(
        type=np.float64,
        description="""Spatial resolution corresponds to the side length of a cell. Default: 2""",
        default=2,
        unit="m"
    )

    temporal_resolution = Quantity(
        type=np.float64,
        description="""Temporal resolution corresponds to temporal resolution""",
        default=0.4,
        unit="s"
    )

    densities_and_velocities = SubSection(
        sub_section = DensitiesAndVelocities,
        repeats=True
    )



class VadereProperties(Properties):

    m_def = Section(extends_base_section=False)

    total_number_of_pedestrians = Quantity(
        type=np.int64,
        description="""Total number of pedestrians in the simulation""",
        default=0
    )

    max_number_of_pedestrians = Quantity(
        type=np.int64,
        description="""Maximum number of pedestrians in the simulation. Corresponds the total number in case of a one time spawning""",
        default=0
    )


class VadereResults(Results):

    m_def = Section()

    properties = SubSection(sub_section=VadereProperties, description="""Scenario specific properties""")

    microscopic_results = SubSection(sub_section=MicroscopicResults,description="""Microscopic results such as trajectories.""")

    macroscopic_results = SubSection(sub_section=MacroscopicResults,  description="""Macroscopic results such as densities or flow.""")




m_package.__init_metainfo__()