import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# --- Configuration ---
SPACE_SIZE = 50
TIME_WINDOW = 50
base_freq_history = [1.0] * TIME_WINDOW

# Initial Clusters
objects = [
    {'pos': np.array([15.0, 15.0]), 'vel': np.array([0.5, 0.4]), 'mass': 1e16},
    {'pos': np.array([35.0, 35.0]), 'vel': np.array([-0.4, -0.6]), 'mass': 1.5e16}
]

# Interaction State
interaction = {'pos': None, 'type': None, 'strength': 0}

def on_click(event):
    if event.inaxes == ax1:
        interaction['pos'] = np.array([event.xdata, event.ydata])
        # 1 = Left Click (Dilution), 3 = Right Click (Focus)
        interaction['type'] = 'dilution' if event.button == 1 else 'focus'
        interaction['strength'] = 5e16 if event.button == 1 else 8e16

def on_release(event):
    interaction['pos'] = None
    interaction['type'] = None

# Setup Figure
fig = plt.figure(figsize=(14, 7), facecolor='#0a0a0a')
ax1 = plt.subplot(121)
ax2 = plt.subplot(122)

fig.canvas.mpl_connect('button_press_event', on_click)
fig.canvas.mpl_connect('button_release_event', on_release)

x, y = np.meshgrid(np.arange(SPACE_SIZE), np.arange(SPACE_SIZE))
im = ax1.pcolormesh(x, y, np.zeros((SPACE_SIZE, SPACE_SIZE)), cmap='magma', shading='gouraud', vmin=0, vmax=1e15)
ax1.set_title("SFRA: Interactive Sequence Field", color='white', pad=20)
ax1.axis('off')

line, = ax2.plot(range(TIME_WINDOW), base_freq_history, color='#00ffcc', lw=3)
ax2.set_facecolor('#0a0a0a')
ax2.set_ylim(0.1, 1.1)
ax2.set_title("System Clock Rate (Hz)", color='white', pad=20)
ax2.tick_params(colors='white')
ax2.grid(color='#222', linestyle='--')

stats_text = ax1.text(2, 2, '', color='white', family='monospace', fontsize=11, fontweight='bold')
pointer, = ax1.plot([], [], 'o', markeredgewidth=2, markersize=15, fillstyle='none')

def animate(frame):
    global base_freq_history
    density = np.zeros((SPACE_SIZE, SPACE_SIZE))
    
    # Process Interaction (Wedge Logic)
    if interaction['pos'] is not None:
        dist_sq = (x - interaction['pos'][0])**2 + (y - interaction['pos'][1])**2
        if interaction['type'] == 'focus':
            density += interaction['strength'] / (dist_sq + 5)
            pointer.set_data([interaction['pos'][0]], [interaction['pos'][1]])
            pointer.set_color('#ff4444')
        else:
            density -= interaction['strength'] / (dist_sq + 10) # Negative density effect
            pointer.set_data([interaction['pos'][0]], [interaction['pos'][1]])
            pointer.set_color('#4444ff')
    else:
        pointer.set_data([], [])

    # Process Objects
    for obj in objects:
        # If focusing, objects gravitate towards the wedge
        if interaction['pos'] is not None and interaction['type'] == 'focus':
            dir_vec = interaction['pos'] - obj['pos']
            obj['vel'] += (dir_vec / (np.linalg.norm(dir_vec) + 1)) * 0.1
        
        obj['pos'] += obj['vel']
        for i in range(2):
            if obj['pos'][i] <= 0 or obj['pos'][i] >= SPACE_SIZE:
                obj['vel'][i] *= -1
        
        dist_sq = (x - obj['pos'][0])**2 + (y - obj['pos'][1])**2
        density += obj['mass'] / (dist_sq + 10)

    # Normalize and Update
    density_clipped = np.clip(density, 0, 2e15)
    im.set_array(density_clipped.ravel())
    
    max_d = np.max(density_clipped)
    current_hz = np.sqrt(1 - np.clip(max_d / 2.5e15, 0, 0.95))
    
    base_freq_history.append(current_hz)
    base_freq_history.pop(0)
    line.set_ydata(base_freq_history)
    
    status = interaction['type'].upper() if interaction['type'] else "BALANCED"
    stats_text.set_text(f"STATE: {status}\nMAX_D: {max_d:.1e}\nCLOCK: {current_hz:.4f} Hz")
    
    return im, line, stats_text, pointer

ani = animation.FuncAnimation(fig, animate, interval=30, blit=False, cache_frame_data=False)
plt.tight_layout()
plt.show()
