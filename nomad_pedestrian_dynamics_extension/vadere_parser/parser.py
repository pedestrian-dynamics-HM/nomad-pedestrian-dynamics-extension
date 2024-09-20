import os
import datetime
import glob
import json
import os
import re
from logging import Logger

from nomad.parsing import MatchingParser
from nomad.parsing.file_parser import FileParser, DataTextParser

from nomad_pedestrian_dynamics_extension.vadere_parser.metainfo.vadere import Model, Output, Simulation, \
    PsychologyModel, VadereResults, MacroscopicResults, MicroscopicResults, VadereProperties, CustomSection


class PedestrianTrajectoryParser(DataTextParser):

    def __init__(self, mainfile: str = None, logger=None, **kwargs):
        super().__init__()

    def parse(self, key=None):

        print("Try to parse")



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


class VadereParser(MatchingParser):

    def __init__(self):

        self.logger = Logger("test")
        self.scenario_parser = JSONParser()
        self.pedestrian_traj_parser = PedestrianTrajectoryParser()

        self.simulation = Simulation(software_name="Vadere")
        self.model = Model()

        self.psychology_model = PsychologyModel()
        self.output = Output()

        self.results = VadereResults()

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

        # store data in simulation object
        self.simulation.software_release = self.scenario_parser.get("release")
        if self.scenario_parser.get("processWriters").get('isTimestamped'):
            day = re.search('\d{4}-\d{2}-\d{2}', self.maindir)
            date = datetime.datetime.strptime(day.group(), '%Y-%m-%d').date()
            self.simulation.date = date

        # store data in simulation object
        if self.scenario_parser.get("scenario").get("attributesPsychology").get("usePsychologyLayer"):
            self.psychology_model.perception_model = self.scenario_parser.get("scenario").get("attributesPsychology").get("psychologyLayer").get("perception")
            self.psychology_model.cognition_model = self.scenario_parser.get("scenario").get("attributesPsychology").get("psychologyLayer").get("cognition")


        self.model.locomotion_model = self.scenario_parser.get("scenario").get("mainModel").split(".")[-1]
        self.model.psychology_model = self.psychology_model
        self.model.time_step_size = self.scenario_parser.get("scenario").get("attributesSimulation").get(
            'simTimeStepLength')
        self.model.seed = self.scenario_parser.get("scenario").get("attributesSimulation").get('simulationSeed')

        self.simulation.model = self.model

    def parse_trajectories(self, archive, logger):

        self.pedestrian_traj_parser.parse()
        self.output.position = [ [1.0,0.0,0.0], [2.0,0.0,0.0], [3.0,0.0,0.0], [4.0,0.0,0.0] ]
        self.simulation.output = self.output

        self.results.m_create(MicroscopicResults)
        self.results.m_create(MacroscopicResults)
        self.results.macroscopic_results.m_create(CustomSection)
        logger.info("PARSER: set id = 2")
        self.results.macroscopic_results.densities.sample_id = 2

        self.results.m_create(VadereProperties)

        self.results.properties.total_number_of_pedestrians = 234

        self.results.microscopic_results.trajectories = [[1.0, 0.0, 0.0], [2.0, 0.0, 0.0], [1,2,3]]
        self.results.microscopic_results.testdata1 = 14.5

        #self.results.macroscopic_results.densities = [[1.0, 0.0, 0.0], [2.0, 0.0, 0.0], [1, 2, 3]]
        self.results.macroscopic_results.testdata2 = 12.5

        archive.results = self.results





    def parse(self, filepath, archive, logger):
        self.maindir = os.path.dirname(os.path.abspath(filepath))
        self.init_parser(logger)
        logger.info("Start parsing scenario file")
        self.parse_scenario_info()
        logger.info("Start parsing trajectory file")

        self.parse_trajectories(archive, logger)
        archive.data = self.simulation



