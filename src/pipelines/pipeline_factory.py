from .ppg_pipeline import PPGPipeline
from .acc_pipeline import ACCPipeline

class PipelineFactory:
    SENSOR_PIPELINES = {
        "ppg": PPGPipeline,
        "acc": ACCPipeline
    }

    @staticmethod
    def get_pipeline(sensor_type: str, config):
        """ Returns pipeline for given sensor type """
        
        pipeline_class = PipelineFactory.SENSOR_PIPELINES.get(sensor_type)
        
        if not pipeline_class:
            return None 
        return pipeline_class(config)
