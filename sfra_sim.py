import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# --- Configuration ---
SPACE_SIZE = 50  # Optimized for smooth rendering on high-DPI displays (Mac/Retina)
TIME_WINDOW = 50
base_freq_history = [1.0] * TIME_WINDOW

# Initial Object Data (Informational Clusters)
objects = [
    {'pos': np.array([20.0, 20.0]), 'vel': np.array([0.8, 0.5]), 'mass': 1e16},
    {'pos': np.array([35.0, 35.0]), 'vel': np.array([-0.6, -0.8]), 'mass': 1.5e16}
]

# Figure Setup
fig = plt.figure(figsize=(14, 7), facecolor='#0a0a0a')
ax1 = plt.subplot(121) # Density Field Window
ax2 = plt.subplot(122) # Frequency Analytics Window

# Coordinate Grid
x, y = np.meshgrid(np.arange(SPACE_SIZE), np.arange(SPACE_SIZE))

# Density Field Visualization (using pcolormesh for Mac compatibility)
im = ax1.pcolormesh(x, y, np.zeros((SPACE_SIZE, SPACE_SIZE)), cmap='magma', shading='gouraud', vmin=0, vmax=1e15)
ax1.set_title("SFRA: Sequence Density Field", color='white', pad=20, fontsize=14)
ax1.set_aspect('equal')
ax1.axis('off')

# System Clock Rate Plot
line, = ax2.plot(range(TIME_WINDOW), base_freq_history, color='#00ffcc', lw=3)
ax2.set_facecolor('#0a0a0a')
ax2.set_ylim(0.2, 1.1)
ax2.set_title("System Clock Rate (Hz)", color='white', pad=20, fontsize=14)
ax2.set_xlabel("Processing Cycles (Steps)", color='#666')
ax2.set_ylabel("Clock Frequency", color='#666')
ax2.tick_params(colors='white')
ax2.grid(color='#222', linestyle='--')

# HUD Information Overlay
stats_text = ax1.text(2, 2, '', color='white', family='monospace', fontsize=12, fontweight='bold', transform=ax1.transData)

def animate(frame):
    global base_freq_history
    density = np.zeros((SPACE_SIZE, SPACE_SIZE))
    
    for obj in objects:
        obj['pos'] += obj['vel']
        
        # Collision Detection (Boundary Bounce)
        for i in range(2):
            if obj['pos'][i] <= 0 or obj['pos'][i] >= SPACE_SIZE:
                obj['vel'][i] *= -1
        
        # Sequence Density Calculation (Inverse Square Law Approximation)
        dist_sq = (x - obj['pos'][0])**2 + (y - obj['pos'][1])**2
        density += obj['mass'] / (dist_sq + 10)

    # Update Rendering Data
    im.set_array(density.ravel())
    
    # Calculate Computational Lag (The Hz Drop)
    max_density = np.max(density)
    current_hz = np.sqrt(1 - np.clip(max_density / 2e15, 0, 0.9))
    
    # Update History Graph
    base_freq_history.append(current_hz)
    base_freq_history.pop(0)
    line.set_ydata(base_freq_history)
    
    # Update Telemetry Display
    stats_text.set_text(
        f"CORE_STATE: ACTIVE\n"
        f"MAX_DENSITY: {max_density:.1e}\n"
        f"SYS_CLOCK: {current_hz:.4f} Hz"
    )
    
    return im, line, stats_text

# Animation Engine
# cache_frame_data=False prevents memory overflow warnings in terminal
ani = animation.FuncAnimation(fig, animate, interval=30, blit=False, cache_frame_data=False)

plt.tight_layout()
plt.show()
