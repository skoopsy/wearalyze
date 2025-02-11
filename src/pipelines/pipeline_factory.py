from .ppg_pipeline import PPGPipeline
from .acc_pipeline import ACCPipeline

class PipelineFactory:
    SENSOR_PIPELINES = {
        "ppg": PPGPipeline,
        "acc": ACCPipeline
    }

    @staticmethod
    def get_pipeline(sensor_type, sensor, config):
        """ Returns pipeline for given sensor type """
        
        pipeline_class = PipelineFactory.SENSOR_PIPELINES.get(sensor_type)
        
        if not pipeline_class:
            raise ValueError(f"[PipelineFactory] Unsupported sensor type: {sensor_type}")
        
        return pipeline_class(sensor, config)
