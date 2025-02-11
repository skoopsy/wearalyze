from src.loaders.config_loader import get_config
from src.loaders.loader_orchestrator import LoaderOrchestrator
from src.checkpoints.checkpoint_manager import CheckpointManager
from src.data_model.subject_factory import create_subjects_from_nested_dicts
from src.pipelines.pipeline_orchestrator import PipelineOrchestrator
from src.visuals.plots import Plots

import matplotlib.pyplot as plt
import pandas as pd
import os
import pyarrow.feather as feather # Hopefully can remove in prod

#TODO add tests for all the extra classes fromt the past week! 12/12/2024

def main():
    # Parse cmd line args and load config
    config = get_config()

    load_checkpoint = config["checkpoint"]["load"]["status"]
    l_checkpoint_id = config["checkpoint"]["load"]["checkpoint_id"]
    save_checkpoint = config["checkpoint"]["save"]["status"]
    s_checkpoint_id = config["checkpoint"]["save"]["checkpoint_id"]
    
    checkpoint_mgr = CheckpointManager(config=config)
    
    if not load_checkpoint:

        load_orchestrator = LoaderOrchestrator(config)
        all_data = load_orchestrator.load_all()

        if verbosity:
            print("Data loading complete. Loaded subjects:")
            for subject in all_data.keys():
                print(f" {subject}")

    if save_checkpoint and s_checkpoint_id == 1:
        checkpoint_mgr.save(all_data)   

    if load_checkpoint and l_checkpoint_id == 1:
        all_data = checkpoint_mgr.load()
    
    subjects = create_subjects_from_nested_dicts(all_data)
   
    breakpoint()
 
    pipeline_orchestrator = PipelineOrchestrator(subjects, config)
    pipeline_orchestrator.run()

    """
    Old plotting, need to integrate it into the pipelines and config

    #Plots.ppg_series(resampled_sections[3].ppg)
    #Plots.ppg_series_compare_datetime(sections[0].reset_index(), resampled_sections[0]) 

    # Plot entire compliance sections
    #Plots.plot_ppg_sections_vs_time(filtered_sections)
    
    
    if debug_plots:
        # Plot some basic SQI results
        sqi_bpms = data[data.sqi_bpm_plausible == True] 
        sqi_bpms_peaks = sqi_bpms[sqi_bpms.is_beat_peak == True]
        rows = len(sqi_bpms_peaks)
        plot_txt = f"SQI: Avg BPM, Totals Heart Beats: str({rows})"
        Plots.group_hr_distribution(sqi_bpms_peaks, bins=50, title_append=plot_txt)
        
        sqi_ibis = sqi_bpms[sqi_bpms.sqi_ibi_max == True]
        rows = len(sqi_ibis[sqi_ibis.is_beat_peak == True])
        plot_txt = f"SQI: IBI Max, Totals Heart Beats: str({rows})"
        Plots.group_hr_distribution(sqi_ibis, bins=50, title_append=plot_txt)

        sqi_ibi_ratio = sqi_ibis[sqi_ibis.sqi_ibi_ratio_group == True]
        rows = len(sqi_ibi_ratio[sqi_ibi_ratio.is_beat_peak == True ])
        plot_txt = f"SQI: IBI Max/Min, Total Hear Beats: str({rows})"
        Plots.group_hr_distribution(sqi_ibi_ratio, bins = 50, title_append=plot_txt)

    for i in range( 2600, 2700, 1):
        Plots.plot_beat_with_features_deriv(data, beat_features, i)
    """
if __name__ == "__main__":
    main()
