from manim import *
import numpy as np
from typing import List, Union, Callable, Optional
from numpy.typing import NDArray

class WaveFunction:
    """Represents a wave function with amplitude, frequency, and phase.
    
    Args:
        amplitude: Peak amplitude of the wave
        frequency: Frequency of oscillation in Hz
        phase: Phase offset in radians
    """
    def __init__(self, amplitude: float = 1.0, frequency: float = 1.0, phase: float = 0.0):
        if amplitude <= 0:
            raise ValueError("Amplitude must be positive")
        self.amplitude = amplitude
        self.frequency = frequency
        self.phase = phase
    
    def __call__(self, t: Union[float, NDArray]) -> Union[float, NDArray]:
        return self.amplitude * np.sin(self.frequency * t + self.phase)
    
    def __add__(self, other: 'WaveFunction') -> 'CombinedWaveFunction':
        return CombinedWaveFunction([self, other])

class CombinedWaveFunction(WaveFunction):
    """Represents a combination of multiple wave functions.
    
    Args:
        waves: List of WaveFunction objects to combine
    """
    def __init__(self, waves: List[WaveFunction]):
        if not waves:
            raise ValueError("Must provide at least one wave function")
        super().__init__()
        self.waves = waves
    
    def __call__(self, t: Union[float, NDArray]) -> Union[float, NDArray]:
        return sum(wave(t) for wave in self.waves)

class DataWave(WaveFunction):
    """Converts data into wave representation using frequency-shift keying (FSK).
    
    Args:
        data: Input data as string, bytes, or list of integers
        base_freq: Base frequency for FSK modulation
        samples_per_bit: Number of samples per data bit
    """
    def __init__(self, 
                 data: Union[str, bytes, List[int]], 
                 base_freq: float = 1.0,
                 samples_per_bit: int = 100):
        super().__init__()
        self.data = self._to_binary(data)
        if base_freq <= 0:
            raise ValueError("Base frequency must be positive")
        self.base_freq = base_freq
        self.samples_per_bit = samples_per_bit
        
    def _to_binary(self, data: Union[str, bytes, List[int]]) -> List[int]:
        if isinstance(data, str):
            return [int(b) for b in ''.join(format(ord(c), '08b') for c in data)]
        elif isinstance(data, bytes):
            return [int(b) for b in ''.join(format(b, '08b') for b in data)]
        elif isinstance(data, list):
            if not all(isinstance(x, int) and x in (0, 1) for x in data):
                raise ValueError("List must contain only binary values (0 or 1)")
            return data
        raise ValueError("Unsupported data type")
    
    def __call__(self, t: Union[float, NDArray]) -> Union[float, NDArray]:
        t = np.asarray(t)
        # Calculate bit index based on time and samples per bit
        bit_index = (t * self.samples_per_bit).astype(int) % len(self.data)
        # Use frequency-shift keying
        freq = self.base_freq * (2 if np.vectorize(lambda i: self.data[i])(bit_index) else 1)
        return self.amplitude * np.sin(freq * t + self.phase)

class FrequencyBandWave(VMobject):
    """A wave visualization that stays within frequency band boundaries.
    
    Args:
        wave_func: Wave function to visualize
        band_width: Width of the frequency band
        band_height: Height of the frequency band
        t_range: Time range for visualization [start, end]
        color: Color of the wave
    """
    def __init__(
        self,
        wave_func: Union[WaveFunction, Callable[[float], float]],
        band_width: float = 2*PI,
        band_height: float = 1.0,
        t_range: List[float] = [-8, 8],
        color: str = BLUE,
        **kwargs
    ):
        if band_width <= 0 or band_height <= 0:
            raise ValueError("Band width and height must be positive")
        if t_range[0] >= t_range[1]:
            raise ValueError("Invalid time range")
            
        super().__init__(**kwargs)
        self.wave_func = wave_func
        self.band_width = band_width
        self.band_height = band_height
        self.t_range = t_range
        
        self.band_rect = Rectangle(
            width=band_width,
            height=band_height,
            stroke_color=GRAY_B,
            stroke_width=2,
            fill_color=BLACK,
            fill_opacity=0.2
        )
        
        self.wave = self._create_wave(color)
        self.add(self.band_rect, self.wave)
    
    def _create_wave(self, color: str) -> ParametricFunction:
        """Creates a wave that stays within the frequency band."""
        def constrained_wave(t: float) -> NDArray:
            # Get raw wave value
            y = self.wave_func(t)
            # Constrain to band height
            y = np.clip(y, -self.band_height/2, self.band_height/2)
            return np.array([t, y, 0])
        
        return ParametricFunction(
            constrained_wave,
            t_range=self.t_range,
            color=color,
            stroke_width=2
        )
    
    def update_wave(self, wave_func: Union[WaveFunction, Callable[[float], float]]) -> None:
        """Updates the wave function and redraws the wave."""
        self.wave_func = wave_func
        self.remove(self.wave)
        self.wave = self._create_wave(self.wave.get_color())
        self.add(self.wave)

class ModulatedWave(WaveFunction):
    """Represents an amplitude/frequency modulated wave.
    
    Args:
        carrier_freq: Carrier wave frequency
        modulation_freq: Modulating signal frequency
        modulation_index: Modulation index/depth
        modulation_type: Type of modulation ('AM' or 'FM')
    """
    def __init__(
        self,
        carrier_freq: float = 10.0,
        modulation_freq: float = 1.0,
        modulation_index: float = 0.5,
        modulation_type: str = 'AM'
    ):
        super().__init__()
        if carrier_freq <= 0 or modulation_freq <= 0:
            raise ValueError("Frequencies must be positive")
        if modulation_index <= 0:
            raise ValueError("Modulation index must be positive")
            
        self.carrier_freq = carrier_freq
        self.modulation_freq = modulation_freq
        self.modulation_index = modulation_index
        self.modulation_type = modulation_type.upper()
        
        if self.modulation_type not in ['AM', 'FM']:
            raise ValueError("Modulation type must be 'AM' or 'FM'")
        
    def __call__(self, t: Union[float, NDArray]) -> Union[float, NDArray]:
        if self.modulation_type == 'AM':
            # Amplitude modulation
            modulation = 1 + self.modulation_index * np.sin(self.modulation_freq * t)
            return self.amplitude * modulation * np.sin(self.carrier_freq * t)
        else:  # FM
            # Frequency modulation
            phase = self.carrier_freq * t + self.modulation_index * \
                   np.sin(self.modulation_freq * t)
            return self.amplitude * np.sin(phase) 