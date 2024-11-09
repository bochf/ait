import pytest
from ait.fsm_importer import FsmImporter
from ait.fsm_exporter import FsmExporter
from ait.graph_wrapper import GraphWrapper
from unittest.mock import mock_open, patch
import io


def test_import_export_cycle():
    # Sample input data
    state_transitions = {
        "S1": {"1": "S2", "2": "S3"},
        "S2": {"1": "S1", "3": "S3"},
        "S3": {"2": "S1"},
    }
    state_list = {"S1": "State 1", "S2": "State 2", "S3": "State 3"}
    event_list = {"1": "Event 1", "2": "Event 2", "3": "Event 3"}
    transition_results = {
        "S1": {"1": "Result 1", "2": "Result 2"},
        "S2": {"1": "Result 3", "3": "Result 4"},
        "S3": {"2": "Result 5"},
    }

    # Create an instance of FsmImporter
    importer = FsmImporter()

    # Import the data
    imported_graph = importer.from_dicts(
        state_transitions, state_list, event_list, transition_results
    )

    # Create an instance of FsmExporter with the imported graph
    exporter = FsmExporter(imported_graph)

    # Export the data
    exported_data = exporter.to_dict()

    # Verify the exported data matches the original input
    assert exported_data[0] == state_transitions
    assert exported_data[1] == state_list
    assert exported_data[2] == event_list
    assert exported_data[3] == transition_results


def test_import_export_csv_cycle():
    # Sample CSV content
    state_transitions_csv = "S_source,E_1,E_2\nS1,S2,S3\nS2,S1,S3\nS3,,S1\n"
    states_csv = "Name,Detail\nS1,State 1\nS2,State 2\nS3,State 3\n"
    events_csv = "Name,Detail\n1,Event 1\n2,Event 2\n"
    transition_results_csv = (
        "S_source,E_1,E_2\nS1,Result1,Result2\nS2,Result3,Result4\nS3,,Result5\n"
    )

    # Mock the file reading
    with patch("builtins.open") as mock_open:
        mock_open.side_effect = [
            io.StringIO(state_transitions_csv),
            io.StringIO(states_csv),
            io.StringIO(events_csv),
            io.StringIO(transition_results_csv),
        ]

        # Create an instance of FsmImporter
        importer = FsmImporter()

        # Import the data
        imported_graph = importer.from_csv(
            "state_transitions.csv",
            "states.csv",
            "events.csv",
            "transition_results.csv",
        )

        # Create an instance of FsmExporter with the imported graph
        exporter = FsmExporter(imported_graph)

        # Export the data
        exported_data = exporter.to_dict()

        # Verify the exported data matches the original input
        assert exported_data[0] == {
            "S1": {"1": "S2", "2": "S3"},
            "S2": {"1": "S1", "2": "S3"},
            "S3": {"2": "S1"},
        }
        assert exported_data[1] == {"S1": "State 1", "S2": "State 2", "S3": "State 3"}
        assert exported_data[2] == {"1": "Event 1", "2": "Event 2"}
        assert exported_data[3] == {
            "S1": {"1": "Result1", "2": "Result2"},
            "S2": {"1": "Result3", "2": "Result4"},
            "S3": {"2": "Result5"},
        }


def test_importer_exporter_with_empty_data():
    # Test with empty data
    state_transitions = {}
    state_list = {}
    event_list = {}
    transition_results = {}

    # Create an instance of FsmImporter
    importer = FsmImporter()

    # Import the data
    imported_graph = importer.from_dicts(
        state_transitions, state_list, event_list, transition_results
    )

    # Create an instance of FsmExporter with the imported graph
    exporter = FsmExporter(imported_graph)

    # Export the data
    exported_data = exporter.to_dict()

    # Verify the exported data matches the original input
    assert exported_data[0] == state_transitions
    assert exported_data[1] == state_list
    assert exported_data[2] == event_list
    assert exported_data[3] == transition_results


def test_import_export_cycle_with_invalid_data():
    # Test with invalid data (e.g., missing states)
    state_transitions = {
        "S1": {"1": "S2"},
        "S2": {"1": "S1"},
        # "S3" is missing
    }
    state_list = {"S1": "State 1", "S2": "State 2"}
    event_list = {"1": "Event 1"}
    transition_results = {
        "S1": {"1": "Result 1"},
        "S2": {"1": "Result 2"},
    }

    # Create an instance of FsmImporter
    importer = FsmImporter()

    # Import the data
    imported_graph = importer.from_dicts(
        state_transitions, state_list, event_list, transition_results
    )

    # Create an instance of FsmExporter with the imported graph
    exporter = FsmExporter(imported_graph)

    # Export the data
    exported_data = exporter.to_dict()

    # Verify the exported data matches the original input
    assert exported_data[0] == {
        "S1": {"1": "S2"},
        "S2": {"1": "S1"},
    }
    assert exported_data[1] == state_list
    assert exported_data[2] == event_list
    assert exported_data[3] == transition_results


def test_import_export_cycle_with_invalid_event():
    # Test with an invalid event that does not exist in the state transitions
    state_transitions = {
        "S1": {"1": "S2"},
        "S2": {"2": "S3"},  # Event '2' does not exist in event_list
    }
    state_list = {"S1": "State 1", "S2": "State 2", "S3": "State 3"}
    event_list = {"1": "Event 1"}  # Missing event '2'
    transition_results = {
        "S1": {"1": "Result 1"},
        "S2": {"2": "Result 2"},
    }

    imported_graph = FsmImporter().from_dicts(
        state_transitions, state_list, event_list, transition_results
    )

    exported_data = FsmExporter(imported_graph).to_dict()

    assert exported_data[0] == state_transitions
    assert exported_data[1] == state_list
    assert exported_data[2] == event_list | {"2": ""}
    assert exported_data[3] == transition_results


def test_import_export_cycle_with_circular_transitions():
    # Test with circular transitions
    state_transitions = {
        "S1": {"1": "S2"},
        "S2": {"1": "S1"},  # Circular transition
    }
    state_list = {"S1": "State 1", "S2": "State 2"}
    event_list = {"1": "Event 1"}
    transition_results = {
        "S1": {"1": "Result 1"},
        "S2": {"1": "Result 2"},
    }

    imported_graph = FsmImporter().from_dicts(
        state_transitions, state_list, event_list, transition_results
    )

    exported_data = FsmExporter(imported_graph).to_dict()

    assert exported_data[0] == state_transitions
    assert exported_data[1] == state_list
    assert exported_data[2] == event_list
    assert exported_data[3] == transition_results


def test_export_without_detail():
    # Test exporting without detail
    state_transitions = {
        "S1": {"1": "S2"},
        "S2": {"1": "S3"},
        "S3": {"1": "S1"},
    }
    state_list = {"S1": "State 1", "S2": "State 2", "S3": "State 3"}
    event_list = {"1": "Event 1"}
    transition_results = {
        "S1": {"1": "Result 1"},
        "S2": {"1": "Result 2"},
        "S3": {"1": "Result 3"},
    }

    imported_graph = FsmImporter().from_dicts(
        state_transitions, state_list, event_list, transition_results
    )

    # Create an exporter with the imported graph
    exporter = FsmExporter(imported_graph)

    # Export without detail
    exported_data = exporter.to_dict()

    assert exported_data[0] == state_transitions
    assert exported_data[1] == state_list
    assert exported_data[2] == event_list
    assert exported_data[3] == transition_results
