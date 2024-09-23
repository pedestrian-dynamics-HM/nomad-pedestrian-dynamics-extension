import numpy as np
from nomad.datamodel import ArchiveSection
from nomad.metainfo import Section, Quantity, SubSection

from nomad_pedestrian_dynamics_extension.vadere_schema.densities import Densities


class MacroscopicResults(ArchiveSection):

    m_def = Section()

    spatial_resolution = Quantity(
        type=np.float64,
        description="""Spatial resolution corresponds to the side length of a cell. Default: 2""",
        default=1, # TODO make adjustable
        unit="m"
    )

    temporal_resolution = Quantity(
        type=np.float64,
        description="""Temporal resolution corresponds to temporal resolution""",
        default=1,# TODO make adjustable
        unit="s"
    )


    densities = SubSection(
        sub_section = Densities.m_def,
        repeats=True
    )
