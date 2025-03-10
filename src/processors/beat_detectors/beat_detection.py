from src.processors.periodic_peak_detectors.factory import PeakDetectorFactory
import pandas as pd
import matplotlib.pyplot as plt

class HeartBeatDetector:
    def __init__(self, config: dict):
        """
        Args:
            config (dict)
        """
    
        self.beat_detector_name = config["ppg_processing"]["beat_detector"]
        self.verbosity = config['outputs']['print_verbosity']
    
    def process_sections(self, sections: list()):
        """
        Main processing methods to detect and and mark heart (quasi-periodic) beats
        Args:
            sections (list of pd.Dataframe): List of preprocessed dataframes with sections of heart beats, typically sectioned due to compliance and so are combined here, may give an option to combine or keep separate later.
        Returns:
            pd.DataFrame: Combined annotated sections
            list of pd.DataFrame: List of individual heart beats based on trough segmentation.
        """
        # Instantiate beat detector method from config
        beat_detector = PeakDetectorFactory.create(self.beat_detector_name)
        annotated_sections = []
        all_beats = [] 
        
        for section_id, section in enumerate(sections):
            section = section.reset_index(drop=True).copy()
            
            # Detect troughs (inverted signal as it will detect "peaks"    
            signal = section.filtered_value * -1
            detector_results = beat_detector.detect(signal)
            troughs = detector_results["peaks"]

            if self.verbosity > 1:
                print(f"Troughtd detected: {len(troughs)}")
            
            # Annotate the sections with info
            section = self._annotate_heart_beats(section, troughs, section_id)
            
            # Combine sections
            annotated_sections.append(section)
            
            # Additional storage of indiviually segmented beats if needed
            segmented_beats = [
                section[section['beat'] == beat_id].copy()
                for beat_id in section['beat'].unique() if beat_id != -1
            ]
            all_beats.extend(segmented_beats)

            if self.verbosity >= 1:
                print(f"Processed section {section_id+1} / {len(sections)}")
        
        combined_sections = pd.concat(annotated_sections, ignore_index=True)
    
        return combined_sections, all_beats

    def _annotate_heart_beats(self, section: pd.DataFrame, troughs: list(), section_id: int):
        """
        Annotates a section with detected heart beats, troughs, peaks, and section id
        Args:
            section (pd.DataFrame): Single PPG section
            troughs (list of int): Index of detected troughs
            section_id (int): ID of the current section

        Returns:
            pd.DataFrame: Annoted sections
        """

        # Initialise columns
        section['section_id'] = section_id
        section['beat'] = -1
        section['is_beat_peak'] = False
        section['is_beat_trough'] = False

        # Flag troughs
        section.loc[section.loc[troughs].index, 'is_beat_trough'] = True

        # Annotate beats and flag peaks
        for beat_id, (start, end) in enumerate(zip(troughs[:-1], troughs[1:])):
            
            # Assign beat ID to rows
            section.loc[start:end, 'beat'] = beat_id

            # Detect peak within beat
            beat_data = section.iloc[start:end]
            peak_idx = beat_data['filtered_value'].idxmax()
            section.loc[peak_idx, 'is_beat_peak'] = True

        if self.verbosity > 1:
            print(f"Unique beats found: {section.beat.nunique()}")

        return section

