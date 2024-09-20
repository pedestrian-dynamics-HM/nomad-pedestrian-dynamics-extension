import os
import datetime
import glob
import json
import os
import re
from logging import Logger

import numpy as np
import pandas
from nomad.parsing.file_parser import FileParser, DataTextParser

from nomad_pedestrian_dynamics_extension.vadere_parser.metainfo.vadere import Model, Simulation, \
    PsychologyModel, VadereResults, MacroscopicResults, MicroscopicResults, VadereProperties, Densities, Trajectories, \
    Scenario


class ScenarioPlot:
    def __init__(self, scenario_json):
        self._scenario_json = scenario_json

    def set_name(self, name):
        self._scenario_json["name"] = name

    @property
    def scenario(self):
        return self._scenario_json["scenario"]

    @property
    def topography(self):
        return self._scenario_json["scenario"]["topography"]

    @property
    def crs(self):
        return self._scenario_json["scenario"]["topography"]["attributes"][
            "referenceCoordinateSystem"
        ]

    @property
    def bound_dict(self):
        return self._scenario_json["scenario"]["topography"]["attributes"]["bounds"]

    @property
    def bound(self):
        b = self._scenario_json["scenario"]["topography"]["attributes"]["bounds"]
        return np.array[
            [b["x"], b["y"]],
            [b["x"], b["y"] + b["width"]],
            [b["x"] + b["height"], b["y"] + b["width"]],
            [b["x"] + b["height"], b["y"]],
        ]

    @property
    def offset(self):
        crs = self.crs
        if "translation" in crs:
            return np.array([crs["translation"]["x"], crs["translation"]["y"]])
        else:
            return np.array([0, 0])

    @property
    def epsg(self):
        return self.crs["epsgCode"]

    @property
    def obstacles(self):
        return self._scenario_json["scenario"]["topography"]["obstacles"]

    @property
    def measurementAreas(self):
        return self._scenario_json["scenario"]["topography"]["measurementAreas"]

    @property
    def stairs(self):
        return self._scenario_json["scenario"]["topography"]["stairs"]

    @property
    def targets(self):
        return self._scenario_json["scenario"]["topography"]["targets"]

    @property
    def target_changers(self):
        return self._scenario_json["scenario"]["topography"]["targetChangers"]

    @property
    def absorbing_areas(self):
        return self._scenario_json["scenario"]["topography"]["absorbingAreas"]

    @property
    def sources(self):
        return self._scenario_json["scenario"]["topography"]["sources"]

    @property
    def dynamic_elements(self):
        return self._scenario_json["scenario"]["topography"]["dynamicElements"]

    @property
    def attr_pedestrian(self):
        return self._scenario_json["scenario"]["topography"]["attributesPedestrian"]

    @property
    def bound(self):
        return self.topography["attributes"]["bounds"]

    def create_obstacle(self, x, y, width, height, id=-1):
        rect = {
            "id": id,
            "shape": {
                "x": x,
                "y": y,
                "width": width,
                "height": height,
                "type": "RECTANGLE",
            },
            "visible": True,
        }
        self.obstacles.append(rect)

    @staticmethod
    def shape_to_list(shape, to_shapely: bool = False):
        if shape["type"] == "POLYGON":
            points = np.array([[p["x"], p["y"]] for p in shape["points"]])
        elif shape["type"] == "RECTANGLE":
            start = np.array([shape["x"], shape["y"]])
            points = start
            points = np.append(points, start + np.array([shape["width"], 0]), axis=0)
            points = np.append(
                points, start + np.array([shape["width"], shape["height"]]), axis=0
            )
            points = np.append(points, start + np.array([0, shape["height"]]), axis=0)
            points = points.reshape((-1, 2))
        else:
            raise ValueError("Expected POLYGON or RECTANGLE")
        if to_shapely:
            if all(points[0] == points[-1]):
                return Polygon(points)
            else:
                return Polygon(np.append(points, points[0]).reshape((-1, 2)))

        else:
            return points

    def topography_frame(self, to_crs):
        default_colors = {
            "obstacles": "#B3B3B3",  # grey
            "targets": "#DD8452",  # orange
            "sources": "#55A868",  # green
        }

        data = []
        for element, color in default_colors.items():
            elements = self.topography[element]
            for e in elements:
                polygon = self.shape_to_list(e["shape"], to_shapely=True)
                style = dict(
                    fillColor=color,
                    fillOpacity=1.0,
                    weight=0,
                    zIndex=100,
                    color="#000000",
                )
                info = dict(e)
                del info["shape"]
                data.append((element, color, style, info, polygon))

        df = gpd.GeoDataFrame(
            data, columns=["type", "fillColor", "style", "info", "geometry"]
        )
        if to_crs is not None:
            df["geometry"] = df["geometry"].translate(
                xoff=self.offset[0], yoff=self.offset[1], zoff=0.0
            )

            df.crs = self.epsg
            df = df.to_crs(epsg=to_crs.replace("EPSG:", ""))

        return df


class VadereTopographyPlotter:
    """
    Plot helper that adds patches for obstacles, targets and source to a given
    axis.
    """

    default_colors = {
        "obstacles": "#B3B3B3",  # grey
        "targets": "#DD8452",  # orange
        "sources": "#55A868",  # green
    }

    def __init__(self, scenario_json):
        self.scenario = ScenarioPlot(scenario_json)

    def add_obstacles(self, ax: plt.Axes):
        return self.add_patches(ax, {"obstacles": "#B3B3B3"})

    def add_patches(self, ax: plt.Axes, element_type_map: dict = None, bound=None):
        if element_type_map is None:
            element_type_map = self.default_colors

        if bound is not None:
            x, y, w, h = bound
            bound: Polygon = Polygon(
                [(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)]
            )

        for element, color in element_type_map.items():
            elements = self.scenario.topography[element]
            polygons = [
                self.scenario.shape_to_list(e["shape"], to_shapely=True)
                for e in elements
            ]
            for poly in polygons:
                if bound is not None:
                    if poly.intersects(bound):
                        poly = poly.intersection(bound)
                # poly is closed patches does not have to close it,
                patch = patches.Polygon(
                    list(poly.exterior.coords),
                    edgecolor=color,
                    facecolor=color,
                    fill=True,
                    closed=False,
                )

                ax.add_patch(patch)

        return ax


class PedestrianTrajectoryParser(FileParser):

    def __init__(self, mainfile: str = None, logger=None, **kwargs):
        super().__init__(mainfile, logger=logger, open=kwargs.get('open', None))

    @property
    def results(self):
        if self._results is None:
            aaa = pandas.read_csv(self.mainfile, sep = " ",)

            self._results = aaa

        return self._results

    def parse(self, **kwargs):
        """
        no parsing necessary
        :param **kwargs:
        """
        return self

    def get_trajectories(self):
        traj = pandas.read_csv(self.mainfile, sep=" ", usecols=[0,1,2,3])

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

        self.psychology_model = PsychologyModel()
        self.logger.info("PARSER - init Create new Vadere results because of initalization")
        self.results = None
        self.id = None


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


        self.simulation.seed = self.scenario_parser.get("scenario").get("attributesSimulation").get('simulationSeed')
        self.simulation.total_simulation_time = self.scenario_parser.get("scenario").get("attributesSimulation").get('finishTime')

        self.simulation.model = self.model

        self.simulation.m_create(Scenario)

        width = self.scenario_parser.get("scenario").get("topography").get("attributes").get("bounds").get("width")
        height = self.scenario_parser.get("scenario").get("topography").get("attributes").get("bounds").get("height")

        sources = self.scenario_parser.get("scenario").get("topography").get("sources")
        targets = self.scenario_parser.get("scenario").get("topography").get("targets")



        self.simulation.scenario.dimensions = [width, height]
        self.simulation.scenario.number_of_sources = len(sources)
        self.simulation.scenario.number_of_targets = len(targets)





    def parse_trajectories(self, archive, logger):

        trajectories__ = self.pedestrian_traj_parser.get_trajectories()

        self.results = VadereResults()
        self.results.m_create(MicroscopicResults)
        self.results.m_create(MacroscopicResults)

        for ped, traj in trajectories__.groupby(by="pedestrian_id"):

            trajectory = Trajectories()

            trajectory.pedestrian_id = ped
            trajectory.position_x = list(traj["position_x"])
            trajectory.time = list(traj["time"])
            trajectory.position_y = list(traj["position_y"])

            if len(self.results.microscopic_results.trajectories) == 0:
                self.results.microscopic_results.trajectories = [trajectory]
            else:
                self.results.microscopic_results.trajectories.append(trajectory)

        time_interval = self.results.macroscopic_results.temporal_resolution.magnitude
        evaluation_times = np.arange(start=0, stop= self.simulation.total_simulation_time, step= time_interval)

        #evaluation_times = evaluation_times[0:5]


        spatial_resolution = self.results.macroscopic_results.spatial_resolution.magnitude

        origin_x = self.scenario_parser.get("scenario").get("topography").get("attributes").get("bounds").get("x")
        origin_y = self.scenario_parser.get("scenario").get("topography").get("attributes").get("bounds").get("y")
        width = self.scenario_parser.get("scenario").get("topography").get("attributes").get("bounds").get("width")
        height = self.scenario_parser.get("scenario").get("topography").get("attributes").get("bounds").get("height")

        gridx = np.arange(origin_x, width + spatial_resolution, spatial_resolution)
        gridy = np.arange(origin_y, height + spatial_resolution, spatial_resolution)


        max_count = 0

        if len(evaluation_times) > 50:
            evaluation_times = evaluation_times[:50]

        for evaluation_time in evaluation_times:
            densities_and_velocities = Densities()
            densities_and_velocities.time = evaluation_time

            lower_bound = evaluation_time
            upper_bound = lower_bound + evaluation_time

            position = trajectories__[(trajectories__['time'] >= lower_bound) & (trajectories__['time'] <= upper_bound)]
            position.drop_duplicates(inplace=True)

            x = position["position_x"]
            y = position["position_y"]

            densities__, _, _ = np.histogram2d(x, y, bins=[gridx, gridy])

            max_count = np.max([max_count,densities__.flatten().sum()]).astype(int)

            densities__ = densities__/spatial_resolution**2

            densities_and_velocities.densities = densities__

            if len(self.results.macroscopic_results.densities) == 0:
                self.results.macroscopic_results.densities = [densities_and_velocities]
            else:
                self.results.macroscopic_results.densities.append(densities_and_velocities)

        self.results.m_create(VadereProperties)
        self.results.properties.total_number_of_pedestrians = trajectories__["pedestrian_id"].max()
        self.results.properties.max_number_of_pedestrians = max_count


        archive.results = self.results



    def parse(self, filepath, archive, logger):

        self.maindir = os.path.dirname(os.path.abspath(filepath))
        self.init_parser(logger)
        logger.info("Start parsing scenario file")
        self.parse_scenario_info()
        logger.info("Start parsing trajectory file")

        self.parse_trajectories(archive, logger)
        archive.data = self.simulation



