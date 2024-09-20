import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import plotly.graph_objs as go
from matplotlib import patches
from nomad.datamodel import ArchiveSection
from nomad.datamodel.metainfo.plot import PlotlyFigure, PlotSection
from nomad.datamodel.results import Properties
from nomad.datamodel.results import Results
from nomad.metainfo import Datetime, Package, Quantity, Section, SubSection
from shapely.geometry import Polygon

m_package = Package(name='vadere_nomadmetainfo_json', description='None')


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


class Scenario(PlotSection):
    m_def = Section()

    number_of_sources = Quantity(
        type=np.int64, description="""Number of sources where agents are spawned."""
    )

    number_of_targets = Quantity(
        type=np.int64, description="""Number of targets."""
    )

    dimensions = Quantity(
        type=np.float64,
        shape=[2],
        description="""Outer dimension of the topography (width x height).""",
        unit='m'
    )

    origin_destination_matrix = Quantity(
        type=np.float64, shape=['number_of_sources', 'number_of_targets'], description="""Origin destination matrix."""
    )

    def normalize(self, archive, logger):
        super(Scenario, self).normalize(archive, logger)

        archive.scenario

        figure1 = px
        figure_json = figure1.to_plotly_json()
        self.figures.append(PlotlyFigure(label='X-Y-Position', index=0, figure=figure_json))


class Simulation(ArchiveSection):
    m_def = Section()

    software_name = Quantity(
        type=str, description="""Name of the software used for the simulation."""
    )

    software_release = Quantity(type=str, description="""Software release.""")

    date = Quantity(type=Datetime, description="""Start time of the execution.""")

    model = SubSection(sub_section=Model, description="""Simulation model.""")

    seed = Quantity(type=np.int64, description="""Simulation seed""",
                    )

    total_simulation_time = Quantity(
        type=np.float64,
        description="""Total simulation time""",
    )

    scenario = SubSection(sub_section=Scenario,
                          description="""Scenario properties."""
                          )


class Trajectories(PlotSection):
    m_def = Section()

    pedestrian_id = Quantity(
        type=np.int64,
        description="""Pedestrian id""",
    )

    time = Quantity(
        type=np.float64,
        shape=['1...*'],
        description="""Point of time""",
    )

    position_x = Quantity(
        type=np.float64,
        shape=['1...*'],
        description="""X-Position""",
    )

    position_y = Quantity(
        type=np.float64,
        shape=['1...*'],
        description="""Y-Position""",
    )

    def normalize(self, archive, logger):
        super(Trajectories, self).normalize(archive, logger)

        figure1 = px.scatter(x=self.position_x, y=self.position_y, title=f"X-Y-Position {self.pedestrian_id}")
        figure_json = figure1.to_plotly_json()
        self.figures.append(PlotlyFigure(label='X-Y-Position', index=0, figure=figure_json))


class MicroscopicResults(ArchiveSection):
    m_def = Section()

    trajectories = SubSection(
        sub_section=Trajectories,
        repeats=True
    )


class Densities(PlotSection):
    m_def = Section()

    time = Quantity(
        type=np.float64,
        description="""Point of time""",
        unit="s"
    )

    densities = Quantity(
        type=np.float64,
        shape=['1...*', '1...*'],
        description="""Densities""",
        unit="1/m**2"
    )

    def normalize(self, archive, logger):
        super(Densities, self).normalize(archive, logger)

        densities_plot = np.flip(self.densities.transpose(), 0)

        heatmap = go.Heatmap(z=densities_plot, showscale=True, colorbar=dict(thickness=5, title="Pedestrian density"))
        figure1 = go.Figure(data=heatmap)
        figure_json = figure1.to_plotly_json()
        self.figures.append(PlotlyFigure(label='Density', index=0, figure=figure_json))


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
        default=4,
        unit="s"
    )

    densities = SubSection(
        sub_section=Densities,
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

    microscopic_results = SubSection(sub_section=MicroscopicResults,
                                     description="""Microscopic results such as trajectories.""")

    macroscopic_results = SubSection(sub_section=MacroscopicResults,
                                     description="""Macroscopic results such as densities or flow.""")


m_package.__init_metainfo__()
