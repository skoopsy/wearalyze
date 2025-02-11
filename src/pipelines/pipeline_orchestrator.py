from .ppg_pipeline import PPGPipeline
from .acc_pipeline import ACCPipeline
from src.utils.config_loader import get_config

class PipelineOrchestrator:
    SENSOR_PIPELINES = {
        "ppg": PPGPipeline,
        "acc": ACCPipeline
    }
    
    def __init__(self, subjects, config):
        self.subjects = subjects
        self.config = config

    def run(self):
        for subject in self.subjects:
            print(f"\n[PipelineOrchestrator] Processing subject: {subject.subject_id}")
            
            for condition_name, condition in subject.conditions.items():
                print(f"    Processing condition: {condition_name}")

                for sensor_type, sensor in condition.sensors.items():
                    print(f"    Processing sensor: {sensor_type}")

                    if sensor_type in self.SENSOR_PIPELINES:
                        pipeline = self.SENSOR_PIPELINES[sensor_type](sensor, self.config)
                        pipeline.run()
                    else:
                        raise ValueError(f"No pipeline found for sensor: {sensor_type}")

