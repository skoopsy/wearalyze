from .pipeline_factory import PipelineFactory

class PipelineOrchestrator:
    
    def __init__(self, subjects, config):
        self.subjects = subjects
        self.config = config

    def run(self):
        """ 
        Runs pipeline for each sensor, for each condition, for each subject
        """
        for subject in self.subjects:
            print(f"\n[PipelineOrchestrator] Processing subject: {subject.subject_id}")
            
            for condition_name, condition in subject.conditions.items():
                print(f"[PipelineOrchestrator] Processing condition: {condition_name}")

                for sensor_type, sensor in condition.sensors.items():
                    print(f"[PipelineOrchestrator] Processing sensor: {sensor_type}")

                
                    pipeline = PipelineFactory.get_pipeline(sensor_type, 
                                                            sensor, 
                                                            self.config
                    )
                    pipeline.run()
                    # Add try except back in
                    try:
                        a = None
                    except ValueError as e:
                        print(f"{e} - No pipeline found for sensor: {sensor_type}")

