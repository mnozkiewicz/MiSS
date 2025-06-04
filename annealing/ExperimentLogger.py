from .AnnealingConfig import AnnealingConfig
from pydantic import BaseModel, Field
from typing import List

import numpy as np
import matplotlib.pyplot as plt

class ExperimentLogger(BaseModel):
    config: AnnealingConfig
    temperature: List[float] = Field(default_factory=list)
    energy: List[float] = Field(default_factory=list)
    best_energy: float = Field(default=float("inf"))
    best_solution: List[int] = Field(default_factory=list)

    def record_step(
            self, 
            temperature: float, 
            energy_value: float, 
            solution_state: np.ndarray
        ) -> None:

        self.temperature.append(temperature)
        self.energy.append(energy_value)

        if energy_value < self.best_energy:
            self.best_energy = energy_value
            self.best_solution = list(solution_state)

    def plot(self):
        fig, ax1 = plt.subplots(figsize=(8, 5))  # Set default figure size

        # Plot temperature (left y-axis)
        ax1.plot(self.temperature, label='Temperature', color='tab:red')
        ax1.set_ylabel('Temperature', color='tab:red')
        ax1.tick_params(axis='y', labelcolor='tab:red')
        ax1.grid(True, which='both', linestyle='--', linewidth=0.5)  # Add grid

        # Plot energy (right y-axis)
        ax2 = ax1.twinx()
        ax2.plot(self.energy, label='Energy', color='tab:blue')
        ax2.set_ylabel('Energy', color='tab:blue')
        ax2.tick_params(axis='y', labelcolor='tab:blue')

        # Title and x-axis limits
        ax1.set_title("Energy and Temperature During Simulated Annealing")
        ax1.set_xlim(0, self.config.epochs * self.config.steps_per_epoch)

        # Combine legends
        lines_1, labels_1 = ax1.get_legend_handles_labels()
        lines_2, labels_2 = ax2.get_legend_handles_labels()
        ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper right')

        plt.tight_layout()
        plt.show()