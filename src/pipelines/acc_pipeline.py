
class ACCPipeline:
    def __init__(self, sensor, config):
        self.sensor = sensor
        self.config = config

    def run(self):
        # stub
        preprocessor = None
        processor = None
