import pytest
import pandas as pd

from data_model.study_data import StudyData, Subject, SessionData, EpochData


@pytest.fixture
def empty_study_data():
    """
    Returns an empty StudyData instance for further use in tests.
    """
    return StudyData()


@pytest.fixture
def sample_subject():
    """
    Returns a Subject object with no sessions.
    """
    return Subject(subject_id="subj_01")


@pytest.fixture
def sample_session():
    """
    Returns a SessionData object with empty sensor data and epochs.
    """
    session = SessionData(session_name="session_A", subject_id="subj_01")
    return session


@pytest.fixture
def sample_epoch():
    """
    Returns an EpochData object with no features.
    """
    return EpochData(epoch_id="epoch_01", start_time=0.0, end_time=60.0)


def test_studydata_initial_state(empty_study_data):
    """
    Test that a newly created StudyData instance has an empty subjects dict.
    """
    assert isinstance(empty_study_data, StudyData)
    assert len(empty_study_data.subjects) == 0
    assert "StudyData(subjects=[])" in repr(empty_study_data), \
        "The __repr__ should indicate empty subjects list."


def test_studydata_add_subject(empty_study_data, sample_subject):
    """
    Test adding a Subject to the StudyData.
    """
    empty_study_data.add_subject(sample_subject)
    assert "subj_01" in empty_study_data.subjects
    assert empty_study_data.get_subject("subj_01") is sample_subject


def test_studydata_get_non_existent_subject(empty_study_data):
    """
    Test that getting a non-existent subject returns None (as implemented).
    """
    assert empty_study_data.get_subject("non_existent") is None


def test_subject_creation(sample_subject):
    """
    Test that a newly created Subject has the correct ID and an empty sessions dict.
    """
    assert sample_subject.subject_id == "subj_01"
    assert isinstance(sample_subject.sessions, dict)
    assert len(sample_subject.sessions) == 0
    rep = repr(sample_subject)
    assert "Subject(id=subj_01," in rep
    assert "sessions=[]" in rep


def test_subject_add_session(sample_subject, sample_session):
    """
    Test adding SessionData to a Subject and retrieving it.
    """
    sample_subject.add_session("session_A", sample_session)
    assert "session_A" in sample_subject.sessions
    # Retrieving:
    retrieved_session = sample_subject.get_session("session_A")
    assert retrieved_session is sample_session


def test_subject_get_non_existent_session(sample_subject):
    """
    Test that getting a non-existent session returns None.
    """
    assert sample_subject.get_session("missing_session") is None


def test_sessiondata_creation(sample_session):
    """
    Test that a newly created SessionData has the correct session name, subject ID,
    and empty containers for sensors, processed data, and epochs.
    """
    assert sample_session.session_name == "session_A"
    assert sample_session.subject_id == "subj_01"
    assert isinstance(sample_session.sensors, dict)
    assert len(sample_session.sensors) == 0
    assert isinstance(sample_session.processed, dict)
    assert len(sample_session.processed) == 0

    assert hasattr(sample_session, "epochs"), \
        "SessionData should have an attribute 'epochs'."
    assert isinstance(sample_session.epochs, dict)

    rep = repr(sample_session)
    assert "SessionData(subject=subj_01, session=session_A," in rep


def test_sessiondata_add_sensor_data(sample_session):
    """
    Test adding sensor DataFrame to a SessionData instance.
    """
    # Create a small DataFrame
    df = pd.DataFrame({"time": [0, 1, 2], "value": [10, 20, 30]})
    sample_session.add_sensor_data("ppg", df)

    assert "ppg" in sample_session.sensors
    retrieved_df = sample_session.get_sensor_data("ppg")
    pd.testing.assert_frame_equal(df, retrieved_df)


def test_sessiondata_get_non_existent_sensor(sample_session):
    """
    Test that retrieving non-existent sensor data returns an empty DataFrame.
    """
    df = sample_session.get_sensor_data("ecg")
    assert df.empty


def test_sessiondata_add_epoch(sample_session, sample_epoch):
    """
    Test that an epoch can be added and retrieved from a session.
    """
    sample_session.add_epoch(sample_epoch)
    assert "epoch_01" in sample_session.epochs
    retrieved_epoch = sample_session.get_epoch("epoch_01")
    assert retrieved_epoch is sample_epoch


def test_sessiondata_get_non_existent_epoch(sample_session):
    """
    Test getting an epoch that does not exist.
    """
    assert sample_session.get_epoch("no_epoch") is None


def test_epochdata_creation(sample_epoch):
    """
    Test the creation of EpochData and its attributes.
    """
    assert sample_epoch.epoch_id == "epoch_01"
    assert sample_epoch.start_time == 0.0
    assert sample_epoch.end_time == 60.0
    assert isinstance(sample_epoch.sensor_features, dict)
    assert len(sample_epoch.sensor_features) == 0
    assert isinstance(sample_epoch.cross_sensor_features, dict)
    assert len(sample_epoch.cross_sensor_features) == 0

    rep = repr(sample_epoch)
    assert "EpochData(id=epoch_01, time=[0.0, 60.0]," in rep


def test_epochdata_add_sensor_features(sample_epoch):
    """
    Test adding sensor features to an EpochData object.
    """
    features_ppg = {"avg_hr": 75, "peak_count": 5}
    sample_epoch.add_sensor_features("ppg", features_ppg)

    assert "ppg" in sample_epoch.sensor_features
    assert sample_epoch.sensor_features["ppg"]["avg_hr"] == 75
    assert sample_epoch.sensor_features["ppg"]["peak_count"] == 5

    # Add more features to the same sensor, ensuring it merges
    more_features_ppg = {"sdnn": 42}
    sample_epoch.add_sensor_features("ppg", more_features_ppg)
    assert sample_epoch.sensor_features["ppg"]["sdnn"] == 42


def test_epochdata_cross_sensor_features(sample_epoch):
    """
    Test adding cross-sensor features (e.g., artifacts, synergy metrics, etc.).
    """
    sample_epoch.cross_sensor_features["motion_artifact"] = True
    assert sample_epoch.cross_sensor_features["motion_artifact"] is True
