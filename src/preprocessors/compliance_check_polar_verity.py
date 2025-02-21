class ComplianceCheckPolarVerity:

    def create_compliance_sections(self, data, config): 
        """
        Identify sections where device was worn for Polar Verity PPG data and
        split data into reasonable sized chunks for beat detection algos
        """
        #TODO Possible hardcode in the threshold as it should be linked to harware.
        threshold = config['ppg_preprocessing']['threshold']
        min_duration = config['ppg_preprocessing']['min_duration'] * 1000  # Convert to ms
        max_length = 60000

        #TODO Triple check the logic here!!!
        # Rows with ppg greater than threshold are marked as compliant
        data['above_threshold'] = data['ppg'] > threshold
        data['section_id'] = (data['above_threshold'] != data['above_threshold'].shift()).cumsum()
        sections = [df for _, df in data[data['above_threshold']].groupby('section_id')]
        
        valid_sections = []
        for section in sections:
            duration = section['timestamp_ms'].iloc[-1] - section['timestamp_ms'].iloc[0]
            if duration >= min_duration:
                if len(section) > max_length:
                    valid_sections.extend([section.iloc[i:i + max_length].copy() for i in range(0, len(section), max_length)])
                else:
                    valid_sections.append(section)

        for i, section in enumerate(valid_sections, start=1):
            section['section_id'] = i
            section.drop(columns=['above_threshold'], errors='ignore', inplace=True)

        return valid_sections
