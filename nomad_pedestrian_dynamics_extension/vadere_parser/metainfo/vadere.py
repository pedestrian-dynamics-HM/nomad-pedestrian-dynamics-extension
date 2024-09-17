

import numpy as np
from nomad.datamodel import ArchiveSection
from nomad.datamodel.metainfo.workflow import Workflow
from nomad.metainfo import Datetime, Package, Quantity, Reference, Section, SubSection

m_package = Package(name='vadere_nomadmetainfo_json', description='None')


class Model(ArchiveSection):
    m_def = Section()

    n_atoms = Quantity(
        type=np.int32, description="""Number of atoms in the model system."""
    )

    labels = Quantity(
        type=str, shape=['n_atoms'], description="""Labels of the atoms."""
    )

    positions = Quantity(
        type=np.float64, shape=['n_atoms', 3], description="""Positions of the atoms."""
    )

    lattice = Quantity(
        type=np.float64,
        shape=[3, 3],
        description="""Lattice vectors of the model system.""",
    )

    locomotion_model = Quantity(
        type = str, description="""Name of the locomotion model"""
    )



class Output(ArchiveSection):
    m_def = Section()

    model = Quantity(
        type=Reference(Model), description="""Reference to the model system."""
    )

    energy = Quantity(
        type=np.float64,
        unit='eV',
        description="""Value of the total energy of the system.""",
    )


class Simulation(ArchiveSection):
    m_def = Section()

    code_name = Quantity(
        type=str, description="""Name of the code used for the simulation."""
    )

    code_version = Quantity(type=str, description="""Version of the code.""")

    date = Quantity(type=Datetime, description="""Execution date of the simulation.""")

    model = SubSection(sub_section=Model, repeats=True)

    output = SubSection(sub_section=Output, repeats=True)


# We extend the existing common definition of section Workflow
class ExampleWorkflow(Workflow):
    # We alter the default base class behavior to add all definitions to the existing
    # base class instead of inheriting from the base class
    m_def = Section(extends_base_section=True)

    # We define an additional example quantity. Use the prefix x_<parsername>_ to denote
    # non common quantities.
    x_example_magic_value = Quantity(
        type=int, description='The magic value from a magic source.'
    )


m_package.__init_metainfo__()