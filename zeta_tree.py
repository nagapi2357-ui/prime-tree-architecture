#!/usr/bin/env python3
"""
Zeta Tree — Prime Tree on the Critical Line
Day 9 (3²) — Adrian & Nagaπ

The critical line Re(s) = 1/2 is the gate of 2.
Primes enter the set through this gate at positions marked by zeta zeros.
Time is relative to each element: born at +, dies at −.

Three visualisations:
1. CRITICAL LINE TREE: trunk along Re(s)=1/2, primes enter at zeros,
   composites branch into Re>1/2 (give) or Re<1/2 (resist)
2. LIFE SPIRAL: each prime's ± journey shown as oscillation that
   spirals from entry to exit
3. RESONANCE MAP: overlay the tree's branch angles with zero spacings
   to see if the 45° convergence emerges from zero statistics
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch
from sympy import isprime, factorint, primerange
from scipy.special import zetac

OUT_DIR = '/Users/ClawdBot/.openclaw/workspace/projects/prime-tree'

# ─── First 30 non-trivial zeta zeros (imaginary parts) ───
# These are well-known to high precision
ZETA_ZEROS = [
    14.134725, 21.022040, 25.010858, 30.424876, 32.935062,
    37.586178, 40.918719, 43.327073, 48.005151, 49.773832,
    52.970321, 56.446248, 59.347044, 60.831779, 65.112544,
    67.079811, 69.546402, 72.067158, 75.704691, 77.144840,
    79.337375, 82.910381, 84.735493, 87.425275, 88.809111,
    92.491899, 94.651344, 95.870634, 98.831194, 101.317851,
]

# ─── RAS functions ───

def sopfr(n):
    return sum(p * e for p, e in factorint(n).items()) if n > 1 else 0

def bigomega(n):
    return sum(e for e in factorint(n).values()) if n > 1 else 0

def omega(n):
    return len(factorint(n)) if n > 1 else 0

def give_resist_ratio(n):
    if n <= 1: return 0
    p = sopfr(n)
    q = bigomega(n)
    return q / p if p > 0 else 0


# ═══════════════════════════════════════════════════════════════
# 1. CRITICAL LINE TREE
# ═══════════════════════════════════════════════════════════════

def plot_critical_line_tree(max_n=50, save_path=None):
    """
    The trunk IS the critical line Re(s) = 1/2.
    Primes are placed at zeta zero positions along the imaginary axis.
    Composites branch left (Re < 1/2, resist domain) or right (Re > 1/2, give domain).
    
    The gate of 2: everything passes through Re = 1/2.
    """
    fig, ax = plt.subplots(1, 1, figsize=(14, 16))
    
    primes = list(primerange(2, max_n + 1))
    
    # Map primes to zeta zeros (prime_k ↔ zero_k)
    prime_positions = {}
    for i, p in enumerate(primes):
        if i < len(ZETA_ZEROS):
            prime_positions[p] = (0.5, ZETA_ZEROS[i])  # On the critical line
        else:
            # Extrapolate for primes beyond our zero list
            prime_positions[p] = (0.5, ZETA_ZEROS[-1] + (i - len(ZETA_ZEROS) + 1) * 3.5)
    
    # Draw the critical line (the gate of 2)
    y_max = max(pos[1] for pos in prime_positions.values()) + 5
    ax.axvline(x=0.5, color='#FF5722', linewidth=3, alpha=0.3, zorder=1)
    ax.text(0.5, y_max + 2, 'Re(s) = ½\nThe Gate of 2', ha='center', va='bottom',
            fontsize=12, fontweight='bold', color='#FF5722', alpha=0.7)
    
    # Label domains
    ax.text(0.05, y_max + 1, '← RESIST\nRe(s) < ½\nPrime domain\n(Euler product)', 
            ha='left', va='top', fontsize=9, color='#1565C0', alpha=0.6,
            bbox=dict(boxstyle='round', facecolor='#BBDEFB', alpha=0.3))
    ax.text(0.95, y_max + 1, 'GIVE →\nRe(s) > ½\nComposite domain\n(Analytic continuation)', 
            ha='right', va='top', fontsize=9, color='#2E7D32', alpha=0.6,
            bbox=dict(boxstyle='round', facecolor='#C8E6C9', alpha=0.3))
    
    # Draw primes on the critical line
    for p, (x, y) in prime_positions.items():
        # Prime node
        ax.plot(x, y, 'o', color='#FF5722', markersize=12, markeredgecolor='#B71C1C',
               markeredgewidth=1.5, zorder=5)
        ax.annotate(f'{p}', (x, y), xytext=(-0.08, 0), textcoords='offset fontsize',
                   fontsize=10, fontweight='bold', color='#B71C1C', ha='right', zorder=6)
        
        # Mark the zero
        zero_idx = primes.index(p)
        if zero_idx < len(ZETA_ZEROS):
            ax.annotate(f't₀={ZETA_ZEROS[zero_idx]:.1f}', (x, y), 
                       xytext=(0.08, -0.02), textcoords='offset fontsize',
                       fontsize=7, color='#888', zorder=6)
    
    # Draw trunk connecting primes
    trunk_ys = sorted([pos[1] for pos in prime_positions.values()])
    ax.plot([0.5] * len(trunk_ys), trunk_ys, '-', color='#FF5722', linewidth=2, alpha=0.5, zorder=2)
    
    # Now place composites
    for n in range(4, max_n + 1):
        if isprime(n):
            continue
        
        factors = factorint(n)
        spf = min(factors.keys())
        gr = give_resist_ratio(n)
        bo = bigomega(n)
        om = omega(n)
        
        # Parent = largest prime ≤ n
        parent_p = max(p for p in primes if p <= n)
        parent_pos = prime_positions[parent_p]
        
        # Direction: composites with more "give" go RIGHT (Re > 1/2)
        # Composites with more "resist" go LEFT (Re < 1/2)
        # Distance from critical line = how far from balance
        
        # Use factor structure to determine side:
        # Even composites (factor of 2 = the gate itself) stay close to the line
        # Odd composites (no factor of 2) go further
        
        if spf == 2:
            # Even: goes to give side (right), but close to gate
            direction = 1
            distance = 0.05 + gr * 0.15
        elif spf == 3:
            # Factor of 3: goes to resist side (left)
            direction = -1
            distance = 0.05 + (1 - gr) * 0.15
        else:
            # Higher prime factors: further from gate
            direction = 1 if gr > 0.3 else -1
            distance = 0.08 + bo * 0.04
        
        # Y position: slightly below parent, stacked among siblings
        siblings = [i for i in range(parent_p + 1, n + 1) if not isprime(i)]
        sib_idx = siblings.index(n) if n in siblings else 0
        
        # Interpolate y between parent and next prime
        next_primes = [p for p in primes if p > parent_p]
        if next_primes:
            next_p = next_primes[0]
            next_pos = prime_positions.get(next_p, (0.5, parent_pos[1] + 5))
            frac = (sib_idx + 1) / (len(siblings) + 1)
            y = parent_pos[1] + frac * (next_pos[1] - parent_pos[1])
        else:
            y = parent_pos[1] + (sib_idx + 1) * 1.0
        
        x = 0.5 + direction * distance
        
        # Draw composite
        comp_colors = {1: '#BBDEFB', 2: '#C8E6C9', 3: '#FFF9C4'}
        color = comp_colors.get(om, '#CE93D8')
        size = 4 + bo * 2
        
        ax.plot(x, y, 's', color=color, markersize=size, markeredgecolor='#1565C0',
               markeredgewidth=0.5, alpha=0.7, zorder=4)
        
        if max_n <= 30:
            fstr = "×".join(str(p) + (f"^{e}" if e > 1 else "")
                          for p, e in sorted(factors.items()))
            ax.annotate(f'{n}', (x, y), xytext=(0.03 * direction, 0),
                       textcoords='offset fontsize', fontsize=6, color='#666', zorder=6)
        
        # Branch from critical line
        ax.plot([0.5, x], [y, y], '-', color=color, linewidth=0.5 + gr * 2, 
               alpha=0.4, zorder=1)
    
    # Draw the ± labels at top and bottom
    ax.annotate('+ ENTRY', (0.5, trunk_ys[0] - 3), ha='center', fontsize=11,
               fontweight='bold', color='#4CAF50',
               arrowprops=dict(arrowstyle='->', color='#4CAF50', lw=2),
               xytext=(0.5, trunk_ys[0] - 6))
    
    ax.set_title('Prime Tree on the Critical Line\n'
                 'Primes enter through Re(s)=½ (the gate of 2) at zeta zero positions\n'
                 'Composites branch into resist (left) or give (right) domains',
                 fontsize=13, fontweight='bold', pad=15)
    
    legend_elements = [
        Line2D([0], [0], color='#FF5722', linewidth=3, alpha=0.5, label='Critical line Re(s)=½'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#FF5722', markersize=10,
               markeredgecolor='#B71C1C', label='Prime (on the gate)'),
        Line2D([0], [0], marker='s', color='w', markerfacecolor='#C8E6C9', markersize=8, label='Composite (branched)'),
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=9, framealpha=0.9)
    
    ax.set_xlim(-0.1, 1.1)
    ax.set_ylabel('Im(s) — imaginary axis (time)', fontsize=11)
    ax.set_xlabel('Re(s) — real axis (resist ← ½ → give)', fontsize=11)
    ax.grid(True, alpha=0.15)
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
        print(f"Saved: {save_path}")
    plt.close()


# ═══════════════════════════════════════════════════════════════
# 2. LIFE SPIRAL — ± oscillation for each prime
# ═══════════════════════════════════════════════════════════════

def plot_life_spirals(save_path=None):
    """
    Each prime's journey through the set as a ± oscillation.
    Entry (+) through the gate of 2, oscillation (life), exit (−).
    
    The oscillation frequency = the prime itself.
    Larger primes oscillate faster (more information per unit time).
    The spiral tightens as primes get more rigid (G/R → 0).
    """
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    
    primes_to_show = [2, 3, 5, 7, 11, 13]
    
    for ax, p in zip(axes.flatten(), primes_to_show):
        # Time axis: entry to exit
        t = np.linspace(0, 2 * np.pi, 1000)
        
        # The oscillation: ± flipping at frequency proportional to the prime
        # Amplitude decays as the prime "gives" its energy to composites
        freq = p  # prime IS the frequency
        decay = np.exp(-t / (2 * np.pi))  # life decays toward exit
        
        # The ± oscillation
        plus_minus = np.cos(freq * t) * decay
        
        # The spiral: oscillation + forward movement through time
        x_spiral = plus_minus
        y_spiral = t
        
        # Color by phase: + = warm, − = cool
        colors = np.where(plus_minus > 0, '#FF5722', '#1565C0')
        
        # Draw as a continuous line with color gradient
        for i in range(len(t) - 1):
            color = '#FF5722' if plus_minus[i] > 0 else '#1565C0'
            alpha = 0.3 + 0.7 * (1 - t[i] / (2 * np.pi))
            ax.plot([x_spiral[i], x_spiral[i+1]], [y_spiral[i], y_spiral[i+1]],
                   '-', color=color, linewidth=1.5, alpha=alpha)
        
        # Gate of 2 (midline)
        ax.axvline(x=0, color='#FF5722', linewidth=1, alpha=0.2, linestyle='--')
        
        # Entry and exit markers
        ax.plot(x_spiral[0], y_spiral[0], '^', color='#4CAF50', markersize=12, zorder=5)
        ax.plot(x_spiral[-1], y_spiral[-1], 'v', color='#F44336', markersize=12, zorder=5)
        
        # 45° balance lines
        ax.axvline(x=np.cos(np.pi/4) * decay[0], color='#888', linewidth=0.5, 
                   linestyle=':', alpha=0.3)
        ax.axvline(x=-np.cos(np.pi/4) * decay[0], color='#888', linewidth=0.5,
                   linestyle=':', alpha=0.3)
        
        gr = give_resist_ratio(p)
        ax.set_title(f'Prime {p}\nfreq={p}, G/R={gr:.3f}', fontsize=10, fontweight='bold')
        ax.set_xlabel('± oscillation')
        ax.set_ylabel('time (relative)')
        ax.set_xlim(-1.3, 1.3)
        ax.grid(True, alpha=0.15)
    
    fig.suptitle('Life Spirals — Each Prime\'s ± Journey Through the Set\n'
                 '▲ Entry (+) through gate of 2 | ▼ Exit (−) back through gate\n'
                 'Red = + phase | Blue = − phase | Frequency = the prime itself',
                 fontsize=13, fontweight='bold', y=1.02)
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
        print(f"Saved: {save_path}")
    plt.close()


# ═══════════════════════════════════════════════════════════════
# 3. ZERO SPACING vs BRANCH ANGLE — the 45° connection
# ═══════════════════════════════════════════════════════════════

def plot_zero_spacing_analysis(save_path=None):
    """
    Analyse the spacings between consecutive zeta zeros and compare
    to the tree's 45° branch spacing.
    
    Key question: does the zero spacing statistics encode the 45° octave?
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Zero spacings
    spacings = np.diff(ZETA_ZEROS)
    mean_spacing = np.mean(spacings)
    
    # Convert spacings to angular measure
    # If we treat the mean spacing as one "period", what angle does each spacing represent?
    angular_spacings = (spacings / mean_spacing) * 360  # normalised to degrees per mean spacing
    
    # Also: ratio of consecutive spacings (like the tree's branch angle ratios)
    spacing_ratios = spacings[1:] / spacings[:-1]
    
    # ── Plot 1: Raw spacings ──
    ax = axes[0][0]
    ax.bar(range(len(spacings)), spacings, color='#90CAF9', edgecolor='#1565C0')
    ax.axhline(y=mean_spacing, color='#FF5722', linewidth=2, linestyle='--',
              label=f'Mean = {mean_spacing:.2f}')
    ax.axhline(y=2*np.pi/8, color='#4CAF50', linewidth=1.5, linestyle=':',
              label=f'2π/8 = {2*np.pi/8:.2f}')
    ax.set_xlabel('Zero index')
    ax.set_ylabel('Spacing (Δt)')
    ax.set_title('Consecutive Zero Spacings')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.2)
    
    # ── Plot 2: Angular spacings distribution ──
    ax = axes[0][1]
    ax.hist(angular_spacings, bins=15, color='#C8E6C9', edgecolor='#2E7D32', alpha=0.7)
    ax.axvline(x=360, color='#888', linewidth=1, linestyle='--', label='360° (1 mean)')
    ax.axvline(x=45, color='#FF5722', linewidth=2, linestyle='--', label='45° (octave)')
    ax.axvline(x=np.mean(angular_spacings), color='#2196F3', linewidth=2,
              label=f'Mean = {np.mean(angular_spacings):.1f}°')
    ax.set_xlabel('Angular spacing (°)')
    ax.set_ylabel('Count')
    ax.set_title('Zero Spacings as Angles\n(normalised to mean = 360°)')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.2)
    
    # ── Plot 3: Spacing ratios — do they cluster near 1 (GUE repulsion)? ──
    ax = axes[1][0]
    ax.scatter(range(len(spacing_ratios)), spacing_ratios, c='#FF5722', s=30, alpha=0.7)
    ax.axhline(y=1.0, color='#4CAF50', linewidth=2, linestyle='--', label='Ratio = 1 (uniform)')
    ax.axhline(y=np.sqrt(2), color='#9C27B0', linewidth=1, linestyle=':', 
              label=f'√2 = {np.sqrt(2):.3f} (45° in ratio)')
    ax.axhline(y=1/np.sqrt(2), color='#2196F3', linewidth=1, linestyle=':',
              label=f'1/√2 = {1/np.sqrt(2):.3f}')
    ax.set_xlabel('Zero pair index')
    ax.set_ylabel('Spacing ratio (Δt_{k+1} / Δt_k)')
    ax.set_title('Consecutive Spacing Ratios\n(GUE repulsion → avoids 0 and ∞)')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.2)
    
    # ── Plot 4: The critical line as tree ──
    ax = axes[1][1]
    
    # Draw critical line
    ax.axvline(x=0, color='#FF5722', linewidth=3, alpha=0.3)
    
    # Place zeros and show ± oscillation at each
    for i, t0 in enumerate(ZETA_ZEROS[:15]):
        # Each zero creates a ± ripple
        theta = np.linspace(-np.pi/2, np.pi/2, 50)
        amplitude = 0.3 / (1 + i * 0.1)  # decreasing amplitude
        x_ripple = amplitude * np.sin(8 * theta)  # 8-fold = octave
        y_ripple = t0 + theta * 0.5
        
        ax.plot(x_ripple, y_ripple, '-', color='#90CAF9', linewidth=0.8, alpha=0.5)
        ax.plot(0, t0, 'o', color='#FF5722', markersize=6, zorder=5)
        
        if i < 10:
            ax.annotate(f'γ_{i+1}={t0:.1f}', (0, t0), xytext=(0.35, 0),
                       textcoords='offset fontsize', fontsize=7, color='#888')
    
    # 45° lines from each zero
    for i in range(min(10, len(ZETA_ZEROS))):
        t0 = ZETA_ZEROS[i]
        # 45° line = slope of 1 in normalised coords
        dx = 0.4
        dy = dx  # 45° = equal run and rise
        ax.plot([0, dx], [t0, t0 + dy], '-', color='#4CAF50', linewidth=0.5, alpha=0.3)
        ax.plot([0, -dx], [t0, t0 + dy], '-', color='#1565C0', linewidth=0.5, alpha=0.3)
    
    ax.set_xlim(-0.8, 0.8)
    ax.set_xlabel('Re(s) − ½')
    ax.set_ylabel('Im(s)')
    ax.set_title('Zeros on Critical Line\nwith ± ripples and 45° branches')
    ax.grid(True, alpha=0.15)
    
    # Stats summary
    print(f"\n  Zero spacing statistics:")
    print(f"    Mean spacing:      {mean_spacing:.4f}")
    print(f"    2π/8 (octave):     {2*np.pi/8:.4f}")
    print(f"    Ratio mean/octave: {mean_spacing/(2*np.pi/8):.4f}")
    print(f"    Mean angular:      {np.mean(angular_spacings):.1f}°")
    print(f"    Std angular:       {np.std(angular_spacings):.1f}°")
    print(f"    Mean ratio:        {np.mean(spacing_ratios):.4f}")
    print(f"    cos(45°)=sin(45°)= {np.cos(np.pi/4):.4f} = 1/√2")
    
    fig.suptitle('Zeta Zero Spacings & the 45° Connection\n'
                 'Does the critical line encode the prime wheel octave?',
                 fontsize=13, fontweight='bold', y=1.02)
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
        print(f"  Saved: {save_path}")
    plt.close()


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║   ZETA TREE — Primes Entering Through the Gate of 2            ║")
    print("║   Day 9 (3²) — Adrian & Nagaπ                                  ║")
    print("╚══════════════════════════════════════════════════════════════════╝\n")
    
    print("1. Critical Line Tree (1..30)...")
    plot_critical_line_tree(30, save_path=f'{OUT_DIR}/zeta_tree_critical_30.png')
    
    print("2. Life Spirals...")
    plot_life_spirals(save_path=f'{OUT_DIR}/zeta_life_spirals.png')
    
    print("3. Zero Spacing Analysis...")
    plot_zero_spacing_analysis(save_path=f'{OUT_DIR}/zeta_spacing_analysis.png')
    
    print("\n✅ Done! 🌀")
