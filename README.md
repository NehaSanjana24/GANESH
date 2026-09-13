# Lord Ganesha Cosmic Particle Animation

A real-time particle animation that uses OpenCV, NumPy, and Pygame to form a Lord Ganesha image from more than 79,000 glowing particles.

## Requirements

- Python 3.10 or newer
- OpenCV
- NumPy
- Pygame

Install the dependencies with:

```powershell
python -m pip install opencv-python numpy pygame
```

## Run

Open PowerShell in this folder and run:

```powershell
python main.py
```

You can also launch the engine directly:

```powershell
python ganesha_anim.py
```

The image asset must be named `ganesh.png` and remain in the same folder as the Python files.

## Test Mode

Run a short 60-frame validation without leaving the test window open:

```powershell
python ganesha_anim.py --test-run
```

## Controls

| Key or action | Effect |
|---|---|
| `Space` or left click | Converge particles or trigger an explosion |
| `R` | Scatter and reset the animation |
| `C` | Cycle color themes |
| `S` | Toggle the swirl vortex |
| `+` / `-` | Increase or decrease particle size |
| `H` | Toggle the help overlay |
| `Esc` or `Q` | Quit |

## Files

- `main.py` - Application launcher
- `ganesha_anim.py` - Particle simulation, rendering, audio, and controls
- `ganesh.png` - Transparent source image used for particle targets
