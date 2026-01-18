import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# --- Настройки ---
SPACE_SIZE = 50 # Уменьшим размер для более быстрой отрисовки на Mac
TIME_WINDOW = 50
base_freq_history = [1.0] * TIME_WINDOW

# Начальные данные объектов
objects = [
    {'pos': np.array([20.0, 20.0]), 'vel': np.array([0.8, 0.5]), 'mass': 1e16},
    {'pos': np.array([35.0, 35.0]), 'vel': np.array([-0.6, -0.8]), 'mass': 1.5e16}
]

fig = plt.figure(figsize=(14, 7), facecolor='#0a0a0a')
ax1 = plt.subplot(121)
ax2 = plt.subplot(122)

# Сетка
x, y = np.meshgrid(np.arange(SPACE_SIZE), np.arange(SPACE_SIZE))

# Используем 'pcolormesh' вместо 'imshow' - он надежнее на Mac
im = ax1.pcolormesh(x, y, np.zeros((SPACE_SIZE, SPACE_SIZE)), cmap='magma', shading='gouraud', vmin=0, vmax=1e15)
ax1.set_title("SFRA: Sequence Density Field", color='white', pad=20)
ax1.set_aspect('equal')
ax1.axis('off')

# График частоты
line, = ax2.plot(range(TIME_WINDOW), base_freq_history, color='#00ffcc', lw=3)
ax2.set_facecolor('#0a0a0a')
ax2.set_ylim(0.2, 1.1)
ax2.set_title("System Clock Rate (Hz)", color='white', pad=20)
ax2.tick_params(colors='white')
ax2.grid(color='#222', linestyle='--')

# HUD Текст
stats_text = ax1.text(2, 2, '', color='white', family='monospace', fontsize=12, fontweight='bold', transform=ax1.transData)

def animate(frame):
    global base_freq_history
    density = np.zeros((SPACE_SIZE, SPACE_SIZE))
    
    for obj in objects:
        obj['pos'] += obj['vel']
        # Отскок
        for i in range(2):
            if obj['pos'][i] <= 0 or obj['pos'][i] >= SPACE_SIZE:
                obj['vel'][i] *= -1
        
        # Математика плотности
        dist_sq = (x - obj['pos'][0])**2 + (y - obj['pos'][1])**2
        density += obj['mass'] / (dist_sq + 10)

    # Обновление данных (принудительное для pcolormesh)
    im.set_array(density.ravel())
    
    # Расчет Hz
    max_density = np.max(density)
    current_hz = np.sqrt(1 - np.clip(max_density / 2e15, 0, 0.9))
    
    base_freq_history.append(current_hz)
    base_freq_history.pop(0)
    line.set_ydata(base_freq_history)
    
    stats_text.set_text(
        f"CORE_STATE: ACTIVE\n"
        f"MAX_DENSITY: {max_density:.1e}\n"
        f"SYS_CLOCK: {current_hz:.4f} Hz"
    )
    
    return im, line, stats_text

# Используем cache_frame_data=False чтобы убрать твою ошибку из терминала
ani = animation.FuncAnimation(fig, animate, interval=30, blit=False, cache_frame_data=False)

plt.tight_layout()
plt.show()
