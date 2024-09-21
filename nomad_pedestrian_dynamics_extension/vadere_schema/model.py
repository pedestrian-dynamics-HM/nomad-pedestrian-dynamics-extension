import numpy as np
from nomad.datamodel import ArchiveSection
from nomad.metainfo import Section, Quantity, SubSection


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
        sub_section=PsychologyModel.m_def, description="""Psychological model"""
    )

    time_step_size = Quantity(
        type=np.float64,
        description="""Time between two evaluations of the simulation loop.""",
        unit='s'
    )
