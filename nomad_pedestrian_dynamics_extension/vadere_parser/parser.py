import datetime
import glob
import json
import os
import re
from logging import Logger

import numpy as np
import pandas
from nomad.parsing.file_parser import FileParser
from runschema.run import Run, Program

from nomad_pedestrian_dynamics_extension.vadere_schema.densities import Densities
from nomad_pedestrian_dynamics_extension.vadere_schema.macroscopic_quantities import MacroscopicResults
from nomad_pedestrian_dynamics_extension.vadere_schema.microscopic_quantities import MicroscopicResults
from nomad_pedestrian_dynamics_extension.vadere_schema.model import PsychologyModel, Model
from nomad_pedestrian_dynamics_extension.vadere_schema.properties import ScenarioProperties
from nomad_pedestrian_dynamics_extension.vadere_schema.results import VadereResults
from nomad_pedestrian_dynamics_extension.vadere_schema.scenario import Scenario
from nomad_pedestrian_dynamics_extension.vadere_schema.simulation import Simulation
from nomad_pedestrian_dynamics_extension.vadere_schema.trajectories import Trajectories


class PedestrianTrajectoryParser(FileParser):
    """
    Read postvis.traj files generated by the Vadere simulator
    Arguments:
        mainfile: the file to be parsed
        logger: logger
    """

    def __init__(self, mainfile: str = None, logger=None, **kwargs):
        super().__init__(mainfile, logger=logger, open=kwargs.get('open', None))

    @property
    def results(self):
        if self._results is None:
            self._results = pandas.read_csv(self.mainfile, sep=" ", )
        return self._results

    def parse(self, **kwargs):
        """
        no parsing necessary
        :param **kwargs:
        """
        return self

    def get_trajectories(self):
        traj = pandas.read_csv(self.mainfile, sep=" ", usecols=[0, 1, 2, 3])
        traj.columns.values[0] = "pedestrian_id"
        traj.columns.values[1] = "time"
        traj.columns.values[2] = "position_x"
        traj.columns.values[3] = "position_y"
        return traj


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

        self.logger = Logger(type(self).__name__)

        self.scenario_parser = JSONParser()
        self.pedestrian_traj_parser = PedestrianTrajectoryParser()
        self.simulation = Simulation()

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

    def add_meta_info_to_data_sec(self, archive):

        # use simple
        self.simulation.software_name = "Vadere"
        self.simulation.software_release = self.scenario_parser.get("release")

        if self.scenario_parser.get("processWriters").get('isTimestamped'):
            day = re.search('\d{4}-\d{2}-\d{2}', self.maindir)
            date = datetime.datetime.strptime(day.group(), '%Y-%m-%d').date()
            self.simulation.date = date

        self.simulation.seed = self.scenario_parser.get("scenario").get("attributesSimulation").get('simulationSeed')
        self.simulation.total_simulation_time = self.scenario_parser.get("scenario").get("attributesSimulation").get(
            'finishTime')

        self.simulation.model = self._get_model()
        self.simulation.scenario = self._get_scenario()

        archive.data = self.simulation
        archive.simulation = self.simulation

    def _get_scenario(self):
        scenario = Scenario()
        width = self.scenario_parser.get("scenario").get("topography").get("attributes").get("bounds").get("width")
        height = self.scenario_parser.get("scenario").get("topography").get("attributes").get("bounds").get("height")
        sources = self.scenario_parser.get("scenario").get("topography").get("sources")
        targets = self.scenario_parser.get("scenario").get("topography").get("targets")
        scenario.dimensions = [width, height]
        scenario.number_of_sources = len(sources)
        scenario.number_of_targets = len(targets)
        return scenario

    def _get_model(self):
        model = Model()
        model.locomotion_model = self.scenario_parser.get("scenario").get("mainModel").split(".")[-1]

        model.time_step_size = self.scenario_parser.get("scenario").get("attributesSimulation").get(
            'simTimeStepLength')

        # get psychological models
        psychology_model = PsychologyModel()
        if self.scenario_parser.get("scenario").get("attributesPsychology").get("usePsychologyLayer"):
            psychology_model.perception_model = self.scenario_parser.get("scenario").get("attributesPsychology").get(
                "psychologyLayer").get("perception")
            psychology_model.cognition_model = self.scenario_parser.get("scenario").get("attributesPsychology").get(
                "psychologyLayer").get("cognition")

        model.psychology_model = psychology_model
        return model

    def _get_trajectories(self):

        microscopic_results = MicroscopicResults()
        trajectories = self.pedestrian_traj_parser.get_trajectories()
        for ped, traj in trajectories.groupby(by="pedestrian_id"):

            trajectory = Trajectories()
            trajectory.pedestrian_id = ped
            trajectory.position_x = list(traj["position_x"])
            trajectory.time = list(traj["time"])
            trajectory.position_y = list(traj["position_y"])

            if len(microscopic_results.trajectories) == 0:
                microscopic_results.trajectories = [trajectory]
            else:
                microscopic_results.trajectories.append(trajectory)

        return microscopic_results

    def compute_and_add_results_to_results_sec(self, archive, logger):

        results = VadereResults()
        results.microscopic_results = self._get_trajectories()
        results.macroscopic_results = self._get_densities()
        results.properties = self._get_scenario_results()
        archive.results = results

    def _get_densities(self):

        macroscopic_results = MacroscopicResults()
        # discretization
        evaluation_times = self._get_temporal_discratization(macroscopic_results)
        gridx, gridy, cell_area = self._get_grid()

        # get density data from trajectories
        trajectories = self.pedestrian_traj_parser.get_trajectories()

        for evaluation_time in evaluation_times:

            densities_and_velocities = Densities()

            densities_and_velocities.time = evaluation_time
            lower_bound = evaluation_time
            upper_bound = lower_bound + evaluation_time

            position = trajectories[(trajectories['time'] >= lower_bound) & (trajectories['time'] <= upper_bound)]
            position = position[~position.duplicated('pedestrian_id', keep="first")]  # only keep first position
            densities__, _, _ = np.histogram2d(position["position_x"], position["position_y"], bins=[gridx, gridy])
            densities__ = densities__ / cell_area
            densities_and_velocities.densities = densities__

            if len(macroscopic_results.densities) == 0:
                macroscopic_results.densities = [densities_and_velocities]
            else:
                macroscopic_results.densities.append(densities_and_velocities)

        return macroscopic_results

    def _get_scenario_results(self):
        """"
        derive scenario specific properties
        #TODO here we could analyze the topology of the scenario
        """

        scenario_properties = ScenarioProperties()
        trajectories = self.pedestrian_traj_parser.get_trajectories()
        scenario_properties.total_number_of_pedestrians = trajectories["pedestrian_id"].max()
        return scenario_properties

    def _get_grid(self):
        """"
        get the spatial discretization for density computation. It is used to count the number of pedestrian in each cell
        """
        spatial_resolution = 1.0  # TODO - replace with user input?
        origin_x = self.scenario_parser.get("scenario").get("topography").get("attributes").get("bounds").get("x")
        origin_y = self.scenario_parser.get("scenario").get("topography").get("attributes").get("bounds").get("y")
        width = self.scenario_parser.get("scenario").get("topography").get("attributes").get("bounds").get("width")
        height = self.scenario_parser.get("scenario").get("topography").get("attributes").get("bounds").get("height")
        gridx = np.arange(origin_x, width + spatial_resolution, spatial_resolution)
        gridy = np.arange(origin_y, height + spatial_resolution, spatial_resolution)
        return gridx, gridy, spatial_resolution ** 2

    def _get_temporal_discratization(self, macroscopic_results):
        """"
        determine the simulation times at which the density should is evaluated
        """

        time_interval = macroscopic_results.temporal_resolution.magnitude
        finish_time = self.scenario_parser.get("scenario").get("attributesSimulation").get('finishTime')
        evaluation_times = np.arange(start=0, stop=finish_time, step=time_interval)
        return evaluation_times

    def add_run_information(self, archive):
        """"
        #TODO Adjust the Run interface and move data and results in the run obj. Do not forget to specify NOMAD references.
        Otherwise one can not search for properties.
        """

        sec_run = Run()
        sec_run.program = Program(
            name='Vadere',
            version=self.scenario_parser.get("release")
        )
        archive.run.append(sec_run)

    def parse(self, filepath, archive, logger):
        """"
         This is the actual main method.
        """

        self.maindir = os.path.dirname(os.path.abspath(filepath))

        logger.info("Start parsing and computing results.")
        self.init_parser(logger)
        self.add_meta_info_to_data_sec(archive)
        self.compute_and_add_results_to_results_sec(archive, logger)
        self.add_run_information(archive)

        logger.info("Finished parsing and computing results.")
