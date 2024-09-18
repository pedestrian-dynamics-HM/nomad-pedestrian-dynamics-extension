import os
import datetime
import glob
import json
import os
import re
from logging import Logger

from nomad.datamodel import EntryArchive
from nomad.parsing.file_parser import TextParser, FileParser

from nomad_pedestrian_dynamics_extension.vadere_parser.metainfo.vadere import Model, Output, Simulation, \
    LocomotionModel, PsychologyModel


class PedestrianTrajectoryParser(TextParser):

    def __init__(self, **kwargs):
        super().__init__()
        self.units = None

    def parse(self, key=None):
        pass


class JSONParser(FileParser):
    """
    Parser for JSON files.
    Arguments:
        mainfile: the file to be parsed
        logger: logger
    """

    def __init__(self, mainfile: str = None, logger=None, **kwargs):
        super().__init__(mainfile, logger=logger, open=kwargs.get('open', None))

    @property
    def results(self):
        # TODO handle file
        if self._results is None:
            with open(self.mainfile, 'r') as file:
                self._results = json.load(file)

        return self._results

    def parse(self, key):
        """
        no parsing necessary
        """
        return self


class VadereParser:

    def __init__(self):

        self.logger = Logger("test")
        self.scenario_parser = JSONParser()
        self.pedestrian_traj_parser = PedestrianTrajectoryParser()

        self.simulation = Simulation(software_name="Vadere")
        self.model = Model()
        self.locomotion_model = LocomotionModel()
        self.psychology_model = PsychologyModel()

        self.output = Output()

    def init_parser(self, logger):

        # init scenario parser
        scenario_filepath = glob.glob(f"{self.maindir}/*.scenario")
        if len(scenario_filepath) == 1:
            scenario_filepath = scenario_filepath[0]
        else:
            raise ValueError(
                f"In the simulation output directory there must be one scenario file. Files found: {scenario_filepath}")
        self.scenario_parser.mainfile = scenario_filepath

        # init trajectory parser
        self.pedestrian_traj_parser.mainfile = os.path.join(self.maindir, 'postvis.traj')

    def parse_scenario_info(self):

        if self.scenario_parser.get("processWriters").get('isTimestamped'):
            day = re.search('\d{4}-\d{2}-\d{2}', self.maindir)
            date = datetime.datetime.strptime(day.group(), '%Y-%m-%d').date()
            self.simulation.date = date

        self.simulation.software_release = self.scenario_parser.get("release")

        self.model.time_step_size = self.scenario_parser.get("scenario").get("attributesSimulation").get(
            'simTimeStepLength')
        self.model.seed = self.scenario_parser.get("scenario").get("attributesSimulation").get('simulationSeed')

        self.locomotion_model.main_model = self.scenario_parser.get("scenario").get("mainModel").split(".")[-1]

        self.psychology_model.perception_model = self.scenario_parser.get("scenario").get("attributesSimulation").get(
            'simulationSeed')

        self.model.locomotion_model = self.locomotion_model
        self.model.psychology_model = self.psychology_model
        self.simulation.model = self.model

    def parse_trajectories(self):

        self.output.position = [ [1.0,0.0,0.0], [1.0,0.0,0.0] ]

        self.simulation.output = self.output


    def parse(self, filepath: str, archive: EntryArchive, logger):
        self.maindir = os.path.dirname(os.path.abspath(filepath))
        self.init_parser(logger)
        logger.info("Start parsing scenario file")
        self.parse_scenario_info()
        logger.info("Start parsing trajectory file")
        self.parse_trajectories()
        archive.data = self.simulation

# class CustomSection(PlotSection, EntryData):
#     m_def = Section()
#     time = Quantity(type=float, shape=['*'], unit='s', a_eln=dict(component='NumberEditQuantity'))
#     substrate_temperature = Quantity(type=float, shape=['*'], unit='K', a_eln=dict(component='NumberEditQuantity'))
#     chamber_pressure = Quantity(type=float, shape=['*'], unit='Pa', a_eln=dict(component='NumberEditQuantity'))
#
#     def normalize(self, archive, logger):
#         super(CustomSection, self).normalize(archive, logger)
#
#         first_line = px.scatter(x=self.time, y=self.substrate_temperature)
#         second_line = px.scatter(x=self.time, y=self.chamber_pressure)
#         figure1 = make_subplots(rows=1, cols=2, shared_yaxes=True)
#         figure1.add_trace(first_line.data[0], row=1, col=1)
#         figure1.add_trace(second_line.data[0], row=1, col=2)
#         figure1.update_layout(height=400, width=716, title_text="Creating Subplots in Plotly")
#         self.figures.append(PlotlyFigure(label='figure 1', figure=figure1.to_plotly_json()))
#
#         figure2 = px.scatter(x=self.substrate_temperature, y=self.chamber_pressure, color=self.chamber_pressure, title="Chamber as a function of Temperature")
#         self.figures.append(PlotlyFigure(label='figure 2', index=1, figure=figure2.to_plotly_json()))
#
#         heatmap_data = [[None, None, None, 12, 13, 14, 15, 16],
#              [None, 1, None, 11, None, None, None, 17],
#              [None, 2, 6, 7, None, None, None, 18],
#              [None, 3, None, 8, None, None, None, 19],
#              [5, 4, 10, 9, None, None, None, 20],
#              [None, None, None, 27, None, None, None, 21],
#              [None, None, None, 26, 25, 24, 23, 22]]
#
#         heatmap = go.Heatmap(z=heatmap_data, showscale=False, connectgaps=True, zsmooth='best')
#         figure3 = go.Figure(data=heatmap)
#         figure_json = figure3.to_plotly_json()
#         figure_json['config'] = {'staticPlot': True}
#         self.figures.append(PlotlyFigure(label='figure 3', index=0, figure=figure_json))
