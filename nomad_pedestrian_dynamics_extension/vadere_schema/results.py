from nomad.metainfo import Section, SubSection
from nomad.datamodel import ArchiveSection, Results

from nomad_pedestrian_dynamics_extension.vadere_schema.macroscopic_quantities import MacroscopicResults
from nomad_pedestrian_dynamics_extension.vadere_schema.microscopic_quantities import MicroscopicResults
from nomad_pedestrian_dynamics_extension.vadere_schema.properties import ScenarioProperties


class VadereResults(Results):

    m_def = Section(description="""This section contain scenario-specific properties, microscopic and macroscopic results""")

    properties = SubSection(sub_section=ScenarioProperties.m_def,
                            description="""Scenario specific properties""")

    microscopic_results = SubSection(sub_section=MicroscopicResults.m_def,
                                     description="""Microscopic results such as trajectories.""")

    macroscopic_results = SubSection(sub_section=MacroscopicResults.m_def,
                                     description="""Macroscopic results such as densities or flow. The results are derived quantities.""")

