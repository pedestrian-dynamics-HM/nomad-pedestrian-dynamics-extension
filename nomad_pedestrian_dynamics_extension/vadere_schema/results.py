from nomad.datamodel import Results
from nomad.metainfo import Section, SubSection

from nomad_pedestrian_dynamics_extension.vadere_schema.macroscopic_quantities import MacroscopicResults
from nomad_pedestrian_dynamics_extension.vadere_schema.microscopic_quantities import MicroscopicResults
from nomad_pedestrian_dynamics_extension.vadere_schema.properties import VadereProperties


class VadereResults(Results):

    m_def = Section()

    properties = SubSection(sub_section=VadereProperties.m_def, description="""Scenario specific properties""")

    microscopic_results = SubSection(sub_section=MicroscopicResults.m_def,description="""Microscopic results such as trajectories.""")

    macroscopic_results = SubSection(sub_section=MacroscopicResults.m_def,  description="""Macroscopic results such as densities or flow.""")
