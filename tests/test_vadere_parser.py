import os.path
from logging import Logger

from nomad.client import parse
from nomad.datamodel import EntryArchive
from nomad_pedestrian_dynamics_extension.vadere_parser import *

def test_vadere_parser_without_matching():
    """
    Tests the parsing algorithm without matching.
    """
    archive = EntryArchive()
    data_path = os.path.join(os.path.dirname(__file__), "data", "basic_2_density_discrete_ca_2024-08-05_12-33-49.69" , "postvis.traj")

    # choose the parser manually
    parser = VadereParser()
    parser.parse(data_path, archive, logger = Logger("Matching_test"))

    sim = archive.data
    assert len(sim.model) == 4 #TODO: needs to be update after finalizing the structure
    assert len(sim.output) == 1

    archive.m_to_dict()


def test_entry_point_configuration():
    """
    Tests whether the correct parser is selected depending on the mainfile and the matching criteria.
    This requires that the entry point is correctly specified in pyproject.toml and nomad_pedestrian_dynamics_extension/__init__
    """

    data_path = os.path.join(os.path.dirname(__file__), "data", "basic_2_density_discrete_ca_2024-09-23_15-52-24.887" , "basic_2_density_discrete_ca.scenario")
    archive = parse(data_path)

    from nomad.client import normalize_all

    # run all normalizers
    normalize_all(archive[0])

    print(archive[0].m_to_dict())









