import io
import os
from logging import Logger

import json

import glob
import numpy as np
from nomad.datamodel import EntryMetadata
from nomad.metainfo import MSection, Quantity, Section


from nomad.datamodel.metainfo.plot import PlotSection, PlotlyFigure
from nomad.datamodel.data import EntryData
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots


import datetime

import numpy as np
from nomad.datamodel import EntryArchive
from nomad.datamodel.metainfo.workflow import Workflow
from nomad.parsing.file_parser import Quantity, TextParser, FileParser
from nomad.units import ureg as units

from nomad_pedestrian_dynamics_extension.vadere_parser.metainfo.vadere import Model, Output, Simulation




def str_to_sites(string):
    sym, pos = string.split('(')
    pos = np.array(pos.split(')')[0].split(',')[:3], dtype=float)
    return sym, pos



calculation_parser = TextParser(
    quantities=[
        Quantity(
            'sites',
            r'([A-Z]\([\d\.\, \-]+\))',
            str_operation=str_to_sites,
            repeats=True,
        ),
        Quantity(
            Model.lattice,
            r'(?:latice|cell): \((\d)\, (\d), (\d)\)\,?\s*\((\d)\, (\d), (\d)\)\,?\s*\((\d)\, (\d), (\d)\)\,?\s*',  # noqa
            repeats=False,
        ),
        Quantity('energy', r'energy: (\d\.\d+)'),
        Quantity(
            'magic_source',
            r'done with magic source\s*\*{3}\s*\*{3}\s*[^\d]*(\d+)',
            repeats=False,
        ),
    ]
)




mainfile_parser = TextParser(
    quantities=[
        Quantity('date', r'(\d\d\d\d\/\d\d\/\d\d)', repeats=False),
        Quantity('program_version', r'super\_code\s*v(\d+)\s*', repeats=False),
        Quantity(
            'calculation',
            r'\s*system \d+([\s\S]+?energy: [\d\.]+)([\s\S]+\*\*\*)*',
            sub_parser=calculation_parser,
            repeats=True,
        ),
    ]
)


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



class ExampleParserNEW:

    def __init__(self):
        self.logger = Logger("test")
        self.scenario_parser = None
        self.scenario_file_extension = ".scenario"
        self.trajectory_file_extension = ".traj"


    def parse(self, mainfile: str, archive: EntryArchive, logger):
        # Log a hello world, just to get us started. TODO remove from an actual parser.

        logger.info('Hello World')

        scenario_filepath = glob.glob(f"{mainfile}/*{self.scenario_file_extension}")
        if len(scenario_filepath) == 1:
            scenario_filepath = scenario_filepath[0]
        else:
            raise ValueError(f"In the simulation output directory there must be one scenario file. Files found: {scenario_filepath}")

        self.scenario_parser = JSONParser(scenario_filepath, self.logger)
        filename = self.scenario_parser.get(key="release")


        simulation = Simulation(
            code_name='super_code', code_version=mainfile_parser.get('program_version')
        )
        date = datetime.datetime.strptime(mainfile_parser.date, '%Y/%m/%d')
        simulation.date = date

        for calculation in mainfile_parser.get('calculation', []):
            model = Model()

            model.lattice = calculation.get('lattice_vectors')
            sites = calculation.get('sites')
            model.labels = [site[0] for site in sites]
            model.positions = [site[1] for site in sites]
            simulation.model.append(model)

            output = Output()
            output.model = model
            output.energy = calculation.get('energy') * units.eV
            magic_source = calculation.get('magic_source')
            if magic_source is not None:
                archive.workflow2 = Workflow(x_example_magic_value=magic_source)
            simulation.output.append(output)
        # put the simulation section into archive data
        archive.data = simulation


#############################################################
# class ExampleSection(MSection):
#     pattern = Quantity(type=np.float64, shape=['*', '3'])
#
#
#
# class ExampleParserChristina:
#
#     def parse(self, mainfile, archive, logger):
#         logger.info('parsing started.')
#
#         with open(mainfile) as f:
#             data = f.readlines()
#
#         archive.metadata = EntryMetadata(external_id=data[0][1:])
#         archive.data = ExampleSection()
#         archive.data.pattern = [
#             [float(number) for number in line.split(' ')] for line in data[1:]
#         ]

#
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