
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

    seed = Quantity(
        type = np.int64,
        description="""Simulation seed""",
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






class CustomSection(PlotSection, EntryData):
    m_def = Section()
    #time = Quantity(type=float, shape=['*'], unit='s', a_eln=dict(component='NumberEditQuantity'))
    #substrate_temperature = Quantity(type=float, shape=['*'], unit='K', a_eln=dict(component='NumberEditQuantity'))
    #chamber_pressure = Quantity(type=float, shape=['*'], unit='Pa', a_eln=dict(component='NumberEditQuantity'))


    def normalize(self, archive, logger):
        super(CustomSection, self).normalize(archive, logger)

        time = [1, 2, 3, 4, 5, 6, 7, 8]

        chamber_pressure = [4, 5, 5, 5, 6, 2, 0, 1]

        substrate_temperature = [0, 0, 5, 0, 0, 2, 0, 1]

        first_line = px.scatter(x=time, y=substrate_temperature)
        second_line = px.scatter(x=time, y=chamber_pressure)
        figure1 = make_subplots(rows=1, cols=2, shared_yaxes=True)
        figure1.add_trace(first_line.data[0], row=1, col=1)
        figure1.add_trace(second_line.data[0], row=1, col=2)
        figure1.update_layout(height=400, width=716, title_text="Creating Subplots in Plotly")
        self.figures.append(PlotlyFigure(label='figure 1', figure=figure1.to_plotly_json()))

        figure2 = px.scatter(x=self.substrate_temperature, y=chamber_pressure, color=chamber_pressure, title="Chamber as a function of Temperature")
        self.figures.append(PlotlyFigure(label='figure 2', index=1, figure=figure2.to_plotly_json()))

        heatmap_data = [[None, None, None, 12, 13, 14, 15, 16],
             [None, 1, None, 11, None, None, None, 17],
             [None, 2, 6, 7, None, None, None, 18],
             [None, 3, None, 8, None, None, None, 19],
             [5, 4, 10, 9, None, None, None, 20],
             [None, None, None, 27, None, None, None, 21],
             [None, None, None, 26, 25, 24, 23, 22]]

        heatmap = go.Heatmap(z=heatmap_data, showscale=False, connectgaps=True, zsmooth='best')
        figure3 = go.Figure(data=heatmap)
        figure_json = figure3.to_plotly_json()
        figure_json['config'] = {'staticPlot': True}

        self.figures.append(PlotlyFigure(label='figure 3', index=0, figure=figure_json))


class MacroscopicResults(ArchiveSection):
    m_def = Section()

    densities = SubSection(
            sub_section=CustomSection
    )

    testdata2= Quantity(
        type=np.float64,
        description="""DUMMY.""",
    )

class VadereProperties(Properties):

    m_def = Section(extends_base_section=False)

    total_number_of_pedestrians = Quantity(
        type=np.int64,
        description="""Total number of pedestrians in the simulation""",
    )

    #def normalize(self, archive, logger):
      #  pass







class VadereResults(Results):

    m_def = Section()

    testdata33 = Quantity(
        type=np.float64,
        description="""DUMMY.""",
    )

    properties = SubSection(sub_section=VadereProperties, description="""scenario specific properties""")

    microscopic_results = SubSection(sub_section=MicroscopicResults,description="""Microscopic results such as trajectories.""")

    macroscopic_results = SubSection(sub_section=MacroscopicResults,  description="""Macroscopic results such as densities or flow.""")






# We extend the existing common definition of section Workflow
class ExampleWorkflow(Workflow):
    # We alter the default base class behavior to add all definitions to the existing
    # base class instead of inheriting from the base class
    m_def = Section(extends_base_section=True)

    # We define an additional example quantity. Use the prefix x_<parsername>_ to denote
    # non common quantities.
    x_example_magic_value = Quantity(
        type=int, description='The magic value from a magic source.'
    )


m_package.__init_metainfo__()