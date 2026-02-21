#!/usr/bin/env python3
"""Experiment 001: Interference Logic Gate (Simulation)

This simulates two input waves and checks if superposition can create
AND-like behavior using a simple energy threshold.
"""
import numpy as np

def signal(t: np.ndarray, freq: float, phase: float) -> np.ndarray:
    return np.sin(2 * np.pi * freq * t + phase)


def energy(x: np.ndarray) -> float:
    return float(np.mean(x ** 2))


def run():
    freq = 5.0
    t = np.linspace(0, 1, 2000, endpoint=False)

    cases = {
        "00": (np.pi, np.pi),
        "01": (np.pi, 0.0),
        "10": (0.0, np.pi),
        "11": (0.0, 0.0),
    }

    energies = {}
    for label, (phi_a, phi_b) in cases.items():
        a = signal(t, freq, phi_a)
        b = signal(t, freq, phi_b)
        out = a + b
        energies[label] = energy(out)

    high = energies["11"]
    low = max(energies["00"], energies["01"], energies["10"])
    threshold = (high + low) / 2

    print("Output energies:")
    for label in sorted(energies):
        print(f"  {label}: {energies[label]:.6f}")

    print(f"\nSuggested threshold: {threshold:.6f}")
    print("Classification (energy > threshold => 1):")
    for label in sorted(energies):
        bit = int(energies[label] > threshold)
        print(f"  {label} -> {bit}")


if __name__ == "__main__":
    run()
