# Experiments

## Experiment 001: Interference Logic Gate (Simulation)
### Goal
Test whether two input waves can produce a deterministic boolean output.

### Tooling (free)
- Python 3 + NumPy + Matplotlib
- Run locally from terminal (no lab gear needed)

### Setup
- Two input signals: A and B
- Represent each as sinusoidal wave with controllable phase:
  - A: sin(2πft + φA)
  - B: sin(2πft + φB)
- Output field: A + B (superposition)
- Decision rule: Output energy above threshold => 1, else 0

### Procedure
1. Choose frequency f and time window.
2. Define four input cases (A,B):
   - 00: φA=π, φB=π (destructive)
   - 01: φA=π, φB=0
   - 10: φA=0, φB=π
   - 11: φA=0, φB=0 (constructive)
3. Compute output energy for each case.
4. Select threshold to separate outcomes.
5. Map to a gate (e.g., AND if only 11 is above threshold).

### Metrics
- Output energy per input case
- Separation margin between low/high outputs
- Sensitivity to ±Δφ noise

### Expected Outcome
- With appropriate threshold, superposition reproduces AND-like behavior.

### Next
- If it works, test XOR via phase inversion and nonlinear mix.

## Experiment 002: Noise Robustness (Simulation)
### Goal
Quantify stability of gate under phase noise.

### Procedure
- Add random phase noise Δφ ~ U(-ε, +ε)
- Repeat 1000 trials per input case
- Measure classification accuracy

### Success Criteria
- ≥ 95% accuracy at ε = 0.1π
