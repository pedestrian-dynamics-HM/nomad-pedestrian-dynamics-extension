import numpy as np
from nomad.datamodel import EntryMetadata
from nomad.metainfo import MSection, Quantity, Section


from nomad.datamodel.metainfo.plot import PlotSection, PlotlyFigure
from nomad.datamodel.data import EntryData
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots


class ExampleSection(MSection):
    pattern = Quantity(type=np.float64, shape=['*', '3'])


class ExampleParserChristina:
    def parse(self, mainfile, archive, logger):
        logger.info('parsing started.')

        with open(mainfile) as f:
            data = f.readlines()

        archive.metadata = EntryMetadata(external_id=data[0][1:])
        archive.data = ExampleSection()
        archive.data.pattern = [
            [float(number) for number in line.split(' ')] for line in data[1:]
        ]


class CustomSection(PlotSection, EntryData):
    m_def = Section()
    time = Quantity(type=float, shape=['*'], unit='s', a_eln=dict(component='NumberEditQuantity'))
    substrate_temperature = Quantity(type=float, shape=['*'], unit='K', a_eln=dict(component='NumberEditQuantity'))
    chamber_pressure = Quantity(type=float, shape=['*'], unit='Pa', a_eln=dict(component='NumberEditQuantity'))

    def normalize(self, archive, logger):
        super(CustomSection, self).normalize(archive, logger)

        first_line = px.scatter(x=self.time, y=self.substrate_temperature)
        second_line = px.scatter(x=self.time, y=self.chamber_pressure)
        figure1 = make_subplots(rows=1, cols=2, shared_yaxes=True)
        figure1.add_trace(first_line.data[0], row=1, col=1)
        figure1.add_trace(second_line.data[0], row=1, col=2)
        figure1.update_layout(height=400, width=716, title_text="Creating Subplots in Plotly")
        self.figures.append(PlotlyFigure(label='figure 1', figure=figure1.to_plotly_json()))

        figure2 = px.scatter(x=self.substrate_temperature, y=self.chamber_pressure, color=self.chamber_pressure, title="Chamber as a function of Temperature")
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

