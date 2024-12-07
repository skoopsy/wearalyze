from src.visuals.plots import (
    plot_signal_detected_peaks,
    plot_detected_inflections,
    plot_scaleogram,
)

class VisualizationHandler:
    @staticmethod
    def visualize_and_save(detector_name, signal, results, section=None, save_path="visuals"):
        """Visualize and save outputs for a given detector."""
        if detector_name == "ampd":
            VisualizationHandler._visualize_ampd(signal, results, save_path)
        elif detector_name == "msptd":
            VisualizationHandler._visualize_msptd(signal, results, section, save_path)
        else:
            raise ValueError(f"Unknown detector for visualization: {detector_name}")

    @staticmethod
    def _visualize_ampd(signal, results, save_path):
        """Visualize and save AMPD outputs."""
        peaks = results["peaks"]
        plot_signal_detected_peaks(signal, peaks, "ampd")
        plt.savefig(f"{save_path}/ampd_detected_peaks.png")
        plt.close()

    @staticmethod
    def _visualize_msptd(signal, results, section, save_path):
        """Visualize and save MSPTD outputs."""
        peaks = results["peaks"]
        troughs = results["troughs"]
        maximagram = results["maximagram"]

        plot_detected_inflections(section, peaks, troughs)
        plt.savefig(f"{save_path}/msptd_detected_inflections.png")
        plt.close()

        plot_scaleogram(maximagram, "Local maxima scaleogram")
        plt.savefig(f"{save_path}/msptd_maxima_scaleogram.png")
        plt.close()
