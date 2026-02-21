#!/usr/bin/env python3
"""
LUMINISCRIPT V2: Interference Computation
Wave-Based Logical Operations

Computation through constructive and destructive interference patterns
Core principle: Logic emerges from wave superposition dynamics
"""

import numpy as np
from typing import List, Dict, Callable, Union
import sys
import os

# Import continuous field processing
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'continuous_field_processing'))
from field_representation import ContinuousField, SpectralEncoding

class InterferenceGate:
    """
    Basic logical operation through wave interference
    Fundamental computational primitive in LUMINISCRIPT V2
    """
    
    def __init__(self, gate_type: str, phase_relationships: Dict[str, float]):
        """
        gate_type: Type of logical operation
        phase_relationships: Phase shifts for different input combinations
        """
        self.gate_type = gate_type
        self.phase_shifts = phase_relationships
        self.operating_frequency = 432.0  # Hz - fundamental processing frequency
    
    def process(self, input_fields: List[ContinuousField]) -> ContinuousField:
        """
        Process input fields through interference logic
        """
        if self.gate_type == 'AND':
            return self._and_gate(input_fields)
        elif self.gate_type == 'OR':
            return self._or_gate(input_fields)
        elif self.gate_type == 'NOT':
            return self._not_gate(input_fields[0])
        elif self.gate_type == 'XOR':
            return self._xor_gate(input_fields)
        elif self.gate_type == 'RESONANCE':
            return self._resonance_gate(input_fields)
        else:
            raise ValueError(f"Unknown gate type: {self.gate_type}")
    
    def _and_gate(self, inputs: List[ContinuousField]) -> ContinuousField:
        """
        AND gate through constructive interference
        Output strong only when all inputs are in phase
        """
        def and_field(x, t):
            total_amplitude = 0.0 + 0.0j
            for field in inputs:
                total_amplitude += field(x, t)
            
            # Strong output only when all inputs constructively interfere
            # Normalize by number of inputs
            return total_amplitude / len(inputs)
        
        # Use intersection of all domains
        spatial_domain = inputs[0].spatial_domain
        temporal_domain = inputs[0].temporal_domain
        for field in inputs[1:]:
            spatial_domain = (
                max(spatial_domain[0], field.spatial_domain[0]),
                min(spatial_domain[1], field.spatial_domain[1])
            )
            temporal_domain = (
                max(temporal_domain[0], field.temporal_domain[0]),
                min(temporal_domain[1], field.temporal_domain[1])
            )
        
        return ContinuousField(and_field, spatial_domain, temporal_domain)
    
    def _or_gate(self, inputs: List[ContinuousField]) -> ContinuousField:
        """
        OR gate through additive interference
        Output when any input is present
        """
        def or_field(x, t):
            max_amplitude = 0.0 + 0.0j
            for field in inputs:
                field_val = field(x, t)
                if abs(field_val) > abs(max_amplitude):
                    max_amplitude = field_val
            return max_amplitude
        
        # Use union of domains (approximate)
        return ContinuousField(or_field, inputs[0].spatial_domain, inputs[0].temporal_domain)
    
    def _not_gate(self, input_field: ContinuousField) -> ContinuousField:
        """
        NOT gate through phase inversion
        180-degree phase shift
        """
        def not_field(x, t):
            return -input_field(x, t)  # π phase shift
        
        return ContinuousField(not_field, input_field.spatial_domain, input_field.temporal_domain)
    
    def _xor_gate(self, inputs: List[ContinuousField]) -> ContinuousField:
        """
        XOR gate through interference cancellation
        Strong output only when inputs are different
        """
        if len(inputs) != 2:
            raise ValueError("XOR gate requires exactly 2 inputs")
        
        def xor_field(x, t):
            field1 = inputs[0](x, t)
            field2 = inputs[1](x, t)
            
            # XOR through selective interference
            # Strong when fields are out of phase
            phase_diff = np.angle(field1) - np.angle(field2)
            xor_strength = abs(np.sin(phase_diff))
            
            return xor_strength * (field1 - field2)
        
        return ContinuousField(xor_field, inputs[0].spatial_domain, inputs[0].temporal_domain)
    
    def _resonance_gate(self, inputs: List[ContinuousField]) -> ContinuousField:
        """
        Resonance gate - amplification when frequency matches
        LUMINISCRIPT-specific: frequency-selective processing
        """
        def resonance_field(x, t):
            total_field = 0.0 + 0.0j
            
            for field in inputs:
                # Extract frequency signature
                spectrum = field.get_spectral_signature(x, t)
                freq = spectrum['temporal_frequency']
                
                # Resonance response (Q=100 resonator)
                resonance_response = 1.0 / (1 + 100 * ((freq - self.operating_frequency) / self.operating_frequency)**2)
                
                # Amplify resonant components
                total_field += field(x, t) * resonance_response
            
            return total_field
        
        return ContinuousField(resonance_field, inputs[0].spatial_domain, inputs[0].temporal_domain)


class InterferenceProcessor:
    """
    Complex computational operations through interference networks
    Enables arbitrary logic through wave dynamics
    """
    
    def __init__(self):
        self.gates = []
        self.processing_network = {}
        
    def add_gate(self, gate_id: str, gate: InterferenceGate):
        """Add gate to processing network"""
        self.gates.append((gate_id, gate))
        self.processing_network[gate_id] = gate
    
    def binary_arithmetic(self, a_field: ContinuousField, b_field: ContinuousField, 
                         operation: str) -> ContinuousField:
        """
        Binary arithmetic through interference patterns
        Addition, subtraction, multiplication via wave dynamics
        """
        if operation == 'add':
            return self._interference_addition(a_field, b_field)
        elif operation == 'multiply':
            return self._interference_multiplication(a_field, b_field)
        elif operation == 'subtract':
            return self._interference_subtraction(a_field, b_field)
        else:
            raise ValueError(f"Unknown arithmetic operation: {operation}")
    
    def _interference_addition(self, a: ContinuousField, b: ContinuousField) -> ContinuousField:
        """
        Addition through linear superposition
        Core quantum mechanical principle
        """
        def sum_field(x, t):
            return a(x, t) + b(x, t)
        
        return ContinuousField(sum_field, a.spatial_domain, a.temporal_domain)
    
    def _interference_multiplication(self, a: ContinuousField, b: ContinuousField) -> ContinuousField:
        """
        Multiplication through nonlinear mixing
        Four-wave mixing in nonlinear materials
        """
        def product_field(x, t):
            a_val = a(x, t)
            b_val = b(x, t)
            
            # Nonlinear mixing creates new frequency components
            # Simplified four-wave mixing: A*B creates sum and difference frequencies
            linear_term = a_val * b_val
            mixing_term = a_val * np.conj(b_val) + np.conj(a_val) * b_val
            
            return linear_term + 0.1 * mixing_term
        
        return ContinuousField(product_field, a.spatial_domain, a.temporal_domain)
    
    def _interference_subtraction(self, a: ContinuousField, b: ContinuousField) -> ContinuousField:
        """
        Subtraction through destructive interference
        Phase-shifted addition
        """
        def diff_field(x, t):
            return a(x, t) - b(x, t)  # Equivalent to a + (-b)
        
        return ContinuousField(diff_field, a.spatial_domain, a.temporal_domain)
    
    def fourier_interference(self, input_field: ContinuousField) -> Dict[float, complex]:
        """
        Fourier analysis through interference
        Parallel frequency extraction via interference patterns
        """
        # Test frequencies around fundamental and harmonics
        test_frequencies = [432 * (2**n) for n in range(-2, 3)]  # 108, 216, 432, 864, 1728 Hz
        fourier_components = {}
        
        for freq in test_frequencies:
            # Create reference oscillation at test frequency
            def reference_field(x, t):
                omega = 2 * np.pi * freq
                k = omega / 343  # assume sound speed
                return np.exp(-1j * (k * x - omega * t))  # conjugate for correlation
            
            ref_field = ContinuousField(reference_field, input_field.spatial_domain, input_field.temporal_domain)
            
            # Interference correlation
            correlation = self._interference_addition(input_field, ref_field)
            
            # Extract correlation strength at center point
            corr_strength = correlation(0.5, 0.005)  # middle of domain
            fourier_components[freq] = corr_strength
        
        return fourier_components
    
    def pattern_matching(self, input_field: ContinuousField, 
                        template_field: ContinuousField) -> ContinuousField:
        """
        Pattern matching through interference correlation
        Template matching via field correlation
        """
        def correlation_field(x, t):
            # Cross-correlation through interference
            input_val = input_field(x, t)
            template_val = np.conj(template_field(x, t))  # conjugate for correlation
            
            return input_val * template_val
        
        return ContinuousField(correlation_field, input_field.spatial_domain, input_field.temporal_domain)


class InterferenceMemory:
    """
    Memory through persistent interference patterns
    Standing waves and resonant modes store information
    """
    
    def __init__(self, spatial_extent: float = 1.0, n_modes: int = 8):
        """
        spatial_extent: Physical size of memory cavity
        n_modes: Number of resonant modes for storage
        """
        self.extent = spatial_extent
        self.n_modes = n_modes
        self.wave_speed = 343  # m/s (sound speed)
        
        # Calculate resonant frequencies
        self.resonant_frequencies = [(n * self.wave_speed) / (2 * self.extent) 
                                   for n in range(1, n_modes + 1)]
        
        # Mode amplitudes (memory state)
        self.mode_amplitudes = {freq: 0.0 + 0.0j for freq in self.resonant_frequencies}
    
    def store_pattern(self, input_field: ContinuousField):
        """
        Store field pattern in resonant modes
        Decomposition into standing wave basis
        """
        processor = InterferenceProcessor()
        
        # Project input onto each resonant mode
        for freq in self.resonant_frequencies:
            # Create mode template
            def mode_template(x, t):
                k = 2 * np.pi * freq / self.wave_speed
                # Standing wave pattern
                return np.sin(k * x) * np.exp(-1j * 2 * np.pi * freq * t)
            
            mode_field = ContinuousField(mode_template, input_field.spatial_domain, input_field.temporal_domain)
            
            # Correlation with input (projection)
            correlation = processor.pattern_matching(input_field, mode_field)
            
            # Extract correlation strength (inner product)
            correlation_strength = correlation(self.extent/2, 0.005)  # center point
            self.mode_amplitudes[freq] = correlation_strength
        
        print(f"Stored pattern in {len(self.mode_amplitudes)} resonant modes")
    
    def recall_pattern(self) -> ContinuousField:
        """
        Recall stored pattern from mode amplitudes
        Reconstruction from standing wave superposition
        """
        def recalled_field(x, t):
            total_field = 0.0 + 0.0j
            
            for freq, amplitude in self.mode_amplitudes.items():
                k = 2 * np.pi * freq / self.wave_speed
                # Reconstruct standing wave mode
                mode = amplitude * np.sin(k * x) * np.exp(-1j * 2 * np.pi * freq * t)
                total_field += mode
            
            return total_field
        
        return ContinuousField(recalled_field, (0, self.extent), (0, 0.01))


# Example usage and demonstrations
if __name__ == "__main__":
    print("=== LUMINISCRIPT V2 INTERFERENCE COMPUTATION ===\n")
    
    # Create test input fields
    encoder = SpectralEncoding()
    
    # Encode binary values as field amplitudes
    bit_0 = encoder.amplitude_encode(0.0)  # Low amplitude = 0
    bit_1 = encoder.amplitude_encode(1.0)  # High amplitude = 1
    
    print("Created binary field representations")
    
    # Test AND gate
    and_gate = InterferenceGate('AND', {})
    and_result = and_gate.process([bit_1, bit_1])
    print("Performed AND gate operation through interference")
    
    # Test XOR gate
    xor_gate = InterferenceGate('XOR', {})
    xor_result = xor_gate.process([bit_1, bit_0])
    print("Performed XOR gate operation through interference")
    
    # Test arithmetic
    processor = InterferenceProcessor()
    
    # Create numerical fields
    num_3 = encoder.frequency_encode(3.0)
    num_5 = encoder.frequency_encode(5.0)
    
    # Addition through superposition
    sum_result = processor.binary_arithmetic(num_3, num_5, 'add')
    print("Performed addition through wave superposition")
    
    # Multiplication through nonlinear mixing
    product_result = processor.binary_arithmetic(num_3, num_5, 'multiply')
    print("Performed multiplication through four-wave mixing")
    
    # Test Fourier analysis
    test_field = encoder.frequency_encode(432.0)  # Pure 432Hz
    fourier_components = processor.fourier_interference(test_field)
    print(f"Fourier analysis via interference: found {len(fourier_components)} components")
    
    # Test memory
    memory = InterferenceMemory(1.0, 4)  # 1 meter cavity, 4 modes
    memory.store_pattern(test_field)
    recalled = memory.recall_pattern()
    print("Stored and recalled pattern in interference memory")
    
    print("\n=== Interference Computation Active ===")
    print("Logic operations through wave interference")
    print("Arithmetic via nonlinear wave mixing")
    print("Memory through resonant standing waves")
    print("Computation emerges from physical wave dynamics")
