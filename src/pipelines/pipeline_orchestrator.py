from .pipeline_factory import PipelineFactory
from src.data_model.study_data import StudyData

class PipelineOrchestrator:
    """
    Orchestrates pipeline execution per subject/session/sensor
    """
    def __init__(self, study_data: StudyData, config):
        self.study_data = study_data
        self.config = config

    def run(self):
        for subject_id, subject in self.study_data.subjects.items():
            print(f"\n[PipelineOrchestrator] Processing subject: {subject_id}")
            
            for session_name, session_data in subject.sessions.items():
                print(f"[PipelineOrchestrator] Processing session: {session_name}")

                for sensor_type, sensor_df in session_data.sensors.items():
                    print(f"[PipelineOrchestrator] Processing sensor: {sensor_type}")

                
                    pipeline = PipelineFactory.get_pipeline(sensor_type, 
                                                            self.config
                    )

                    if pipeline is None:
                        print(f"[PipelineOrchestrator] No pipeline for {sensor_type}, skipping.")
                        continue
                    processed_data, processed_features = pipeline.run(sensor_df)
                    
                    session_data.processed[f"{sensor_type}_processed"] = processed_data
                    session_data.processed[f"{sensor_type}_features"] = processed_features 


