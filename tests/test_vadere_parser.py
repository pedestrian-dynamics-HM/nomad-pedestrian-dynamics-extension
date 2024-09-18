import os.path
from logging import Logger

import pytest
from nomad.client import normalize_all, parse
from nomad.datamodel import EntryArchive
import sys


from nomad_pedestrian_dynamics_extension.vadere_parser import *

def test_vadere_parser_without_matching():
    archive = EntryArchive()
    logger = Logger("test")

    data_path = os.path.join(os.path.dirname(__file__), "data", "basic_2_density_discrete_ca_2024-08-05_12-33-49.69" , "postvis.traj")

    # choose the parser manually
    parser = VadereParser()
    parser.parse(data_path, archive, logger)

    sim = archive.data
    assert len(sim.model) == 4 #TODO: needs to be update after finalizing the structure
    assert len(sim.output) == 1


def test_vadere_parser_with_matching():


    data_path = os.path.join(os.path.dirname(__file__), "data", "basic_2_density_discrete_ca_2024-08-05_12-33-49.69" , "postvis.traj")

    # match and run the parser
    archive = parse(data_path)
    # run all normalizers
    normalize_all(archive)

    # get the 'main section' section_run as a metainfo object
    section_run = archive.section_run[0]

    # get the same data as JSON serializable Python dict
    python_dict = section_run.m_to_dict()




