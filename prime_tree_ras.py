#!/usr/bin/env python3
"""
Prime Tree + RAS Integration — v2
Day 9 (3²) — Adrian & Nagaπ

Each node in the tree gets its RAS boundary shape as a cross-section.
Primes = smooth/circular (resist). Composites = lobed (give/flex).

Angle Evolution: branching angle at each composite is determined by
the prime-ratio vocabulary available at that point in the sequence.

Natural Biofication: maps number-theoretic branching to plant morphology.
"""

import sys
sys.path.insert(0, '/Users/ClawdBot/.openclaw/workspace/projects/rational-superformula')

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from matplotlib.lines import Line2D
from sympy import isprime, factorint

OUT_DIR = '/Users/ClawdBot/.openclaw/workspace/projects/prime-tree'


# ─── RAS core (self-contained, overflow-safe) ───

def sopfr(n):
    return sum(p * e for p, e in factorint(n).items()) if n > 1 else 0

def bigomega(n):
    return sum(e for e in factorint(n).values()) if n > 1 else 0

def omega(n):
    return len(factorint(n)) if n > 1 else 0


def ras_shape(n, num_points=300):
    """
    Generate normalised RAS boundary (x, y) for number n.
    Overflow-safe: caps exponents for visualisation while preserving shape character.
    """
    if n <= 1:
        # Source = perfect circle
        theta = np.linspace(0, 2 * np.pi, num_points)
        return np.cos(theta), np.sin(theta)
    
    p = sopfr(n)   # "resist" exponent
    q = bigomega(n)  # "give" exponent
    m = max(omega(n) + 1, 1)  # symmetry fold
    
    # Cap exponents to prevent overflow but preserve ratios
    max_exp = 10
    if p + q > max_exp:
        scale = max_exp / (p + q)
        p_vis = max(p * scale, 0.5)
        q_vis = max(q * scale, 0.5)
    else:
        p_vis = max(p, 0.5)
        q_vis = max(q, 0.5)
    
    theta = np.linspace(0, 2 * np.pi, num_points, endpoint=False)
    
    # m-fold symmetry applied to angle
    m_theta = m * theta
    
    # RAS deformation: resist (cos) vs give (sin)
    # Primes: high p, low q → cos dominates → smooth/circular
    # Composites: higher q relative to p → sin lobes emerge
    cos_part = np.abs(np.cos(m_theta)) ** p_vis
    sin_part = np.abs(np.sin(m_theta)) ** q_vis
    
    rho = (cos_part + sin_part) ** (-1.0 / (p_vis + q_vis))
    
    # Normalise to unit
    rho_max = np.max(rho)
    if rho_max > 0:
        rho = rho / rho_max
    
    x = rho * np.cos(theta)
    y = rho * np.sin(theta)
    
    return x, y


def give_resist_ratio(n):
    """
    Give/Resist ratio: q/p = bigomega/sopfr.
    Low = rigid/prime-like (resist). High = flexible/composite (give).
    This is the "flex factor" of a branch.
    """
    if n <= 1:
        return 0
    p = sopfr(n)
    q = bigomega(n)
    return q / p if p > 0 else 0


# ─── Angle Evolution Engine ───

def evolving_angle(n, primes_so_far):
    """
    Compute branching angle for composite n based on the ratio vocabulary
    available from primes currently in the set.
    
    The angle is determined by the RATIOS between n's factors and the
    cumulative prime structure — not by any fixed degree system.
    
    Returns angle in radians.
    """
    if len(primes_so_far) == 0:
        return 0
    
    factors = factorint(n)
    
    # Method: angle = sum of (factor / prime_harmonic) * (position_in_set / total_primes)
    # This makes the angle vocabulary grow as new primes join
    
    harmonic = sum(1.0 / p for p in primes_so_far)
    
    # Each factor contributes an angular component based on its ratio to the harmonic
    angle = 0
    for p, e in factors.items():
        # Where does this factor sit in the known primes?
        if p in primes_so_far:
            idx = primes_so_far.index(p)
            # Ratio position: how far through the known vocabulary
            ratio_pos = (idx + 1) / len(primes_so_far)
        else:
            ratio_pos = 1.0  # beyond known — maximum angle
        
        # Each factor adds: its ratio contribution × multiplicity
        angle += ratio_pos * e / harmonic
    
    # Scale to useful angular range (0 to π)
    # The harmonic sum grows with ln(ln(n)), giving gradual expansion
    angle = (angle % 1.0) * np.pi
    
    return angle


def golden_angle_test(n, primes_so_far):
    """
    Test: does the evolving angle converge toward the golden angle (137.508°)?
    The golden angle = π(3-√5) ≈ 2.3999... rad
    Plants use this for optimal packing.
    """
    GOLDEN_ANGLE = np.pi * (3 - np.sqrt(5))  # ≈ 2.3999 rad ≈ 137.508°
    
    evolving = evolving_angle(n, primes_so_far)
    return evolving, GOLDEN_ANGLE, abs(evolving - GOLDEN_ANGLE)


# ─── Gallery: RAS shapes 1..N ───

def plot_ras_gallery(max_n=30, save_path=None):
    """
    Botanical identification chart: each number's RAS shape.
    Colour-coded by type. Shows give/resist ratio.
    """
    cols = 6
    rows = (max_n + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 2.8, rows * 2.8))
    
    fig.suptitle('RAS Shape Gallery — "Natural Biofication"\n'
                 'Each number\'s boundary from prime factorisation\n'
                 'Resist (primes=rigid) vs Give (composites=flexible)',
                 fontsize=13, fontweight='bold', y=1.01)
    
    for i in range(rows * cols):
        r, c = divmod(i, cols)
        ax = axes[r][c] if rows > 1 else axes[c]
        
        n = i + 1
        if n > max_n:
            ax.axis('off')
            continue
        
        x, y = ras_shape(n)
        
        # Colour by type
        if n == 1:
            fill_color, edge_color = 'gold', '#FF8F00'
        elif isprime(n):
            fill_color, edge_color = '#FFCDD2', '#B71C1C'
        else:
            om = omega(n)
            fill_colors = {1: '#BBDEFB', 2: '#C8E6C9', 3: '#FFF9C4'}
            fill_color = fill_colors.get(om, '#E1BEE7')
            edge_color = '#1565C0'
        
        ax.fill(x, y, color=fill_color, alpha=0.75)
        ax.plot(x, y, color=edge_color, linewidth=1.8)
        
        # Add unit circle reference (dashed)
        theta_ref = np.linspace(0, 2 * np.pi, 100)
        ax.plot(np.cos(theta_ref) * 0.3, np.sin(theta_ref) * 0.3, 
                '--', color='#ccc', linewidth=0.5, alpha=0.5)
        
        # Labels
        if n == 1:
            title = "1\nSource"
        elif isprime(n):
            gr = give_resist_ratio(n)
            title = f"{n}  PRIME\nG/R={gr:.2f}"
        else:
            factors = factorint(n)
            fstr = "×".join(str(p) + (f"^{e}" if e > 1 else "")
                          for p, e in sorted(factors.items()))
            gr = give_resist_ratio(n)
            title = f"{n} = {fstr}\nG/R={gr:.2f}"
        
        is_p = n == 1 or isprime(n)
        ax.set_title(title, fontsize=8, fontweight='bold' if is_p else 'normal',
                    color='#B71C1C' if isprime(n) else ('#FF8F00' if n == 1 else '#333'),
                    pad=3)
        
        ax.set_xlim(-1.3, 1.3)
        ax.set_ylim(-1.3, 1.3)
        ax.set_aspect('equal')
        ax.axis('off')
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
        print(f"Saved: {save_path}")
    plt.close()


# ─── Angle Evolution Visualisation ───

def plot_angle_evolution(max_n=100, save_path=None):
    """
    Track how the branching angle evolves as primes enter the set.
    Compare to golden angle. Does the tree converge on phyllotaxis?
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    GOLDEN_ANGLE = np.pi * (3 - np.sqrt(5))
    GOLDEN_DEG = np.degrees(GOLDEN_ANGLE)
    
    primes_so_far = []
    
    # Track data
    ns = []
    angles_rad = []
    angles_deg = []
    gr_ratios = []
    harmonic_sums = []
    is_prime_list = []
    flex_factors = []
    
    for n in range(2, max_n + 1):
        if isprime(n):
            primes_so_far.append(n)
        
        if not isprime(n) and n > 3:
            ang = evolving_angle(n, primes_so_far)
            ns.append(n)
            angles_rad.append(ang)
            angles_deg.append(np.degrees(ang))
            gr_ratios.append(give_resist_ratio(n))
            harmonic_sums.append(sum(1.0 / p for p in primes_so_far))
            is_prime_list.append(False)
            flex_factors.append(give_resist_ratio(n))
    
    ns = np.array(ns)
    angles_deg = np.array(angles_deg)
    gr_ratios = np.array(gr_ratios)
    
    # ── Plot 1: Angle evolution ──
    ax = axes[0][0]
    colors = ['#90CAF9' if not ip else '#FF5722' for ip in is_prime_list]
    ax.scatter(ns, angles_deg, c=colors, s=15, alpha=0.7, zorder=3)
    ax.axhline(y=GOLDEN_DEG, color='#4CAF50', linestyle='--', linewidth=2, 
              label=f'Golden angle ({GOLDEN_DEG:.1f}°)', zorder=2)
    ax.axhline(y=120, color='#FF9800', linestyle=':', linewidth=1, label='120° (3-fold)', alpha=0.5)
    ax.axhline(y=90, color='#9C27B0', linestyle=':', linewidth=1, label='90° (4-fold)', alpha=0.5)
    ax.axhline(y=72, color='#2196F3', linestyle=':', linewidth=1, label='72° (5-fold)', alpha=0.5)
    ax.set_xlabel('n')
    ax.set_ylabel('Branching angle (°)')
    ax.set_title('Angle Evolution\nDo composites converge on golden angle?')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    
    # ── Plot 2: Give/Resist ratio distribution ──
    ax = axes[0][1]
    all_gr = [(n, give_resist_ratio(n), isprime(n)) for n in range(2, max_n + 1)]
    prime_gr = [(n, gr) for n, gr, ip in all_gr if ip]
    comp_gr = [(n, gr) for n, gr, ip in all_gr if not ip]
    
    if comp_gr:
        ax.scatter([c[0] for c in comp_gr], [c[1] for c in comp_gr], 
                  c='#90CAF9', s=20, alpha=0.6, label='Composites (flex)', zorder=2)
    if prime_gr:
        ax.scatter([c[0] for c in prime_gr], [c[1] for c in prime_gr],
                  c='#FF5722', s=30, alpha=0.8, label='Primes (rigid)', zorder=3)
    
    ax.set_xlabel('n')
    ax.set_ylabel('Give/Resist ratio (Ω/sopfr)')
    ax.set_title('Flex Factor: Give vs Resist\nPrimes resist (low), Composites flex (high)')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    
    # ── Plot 3: RAS shapes for key numbers ──
    ax = axes[1][0]
    key_numbers = [2, 3, 5, 6, 7, 8, 10, 12, 15, 24, 30]
    n_shapes = len(key_numbers)
    cols_s = 4
    rows_s = (n_shapes + cols_s - 1) // cols_s
    
    for idx, kn in enumerate(key_numbers):
        r_idx, c_idx = divmod(idx, cols_s)
        cx = c_idx * 2.5
        cy = -r_idx * 2.5
        
        x, y = ras_shape(kn, num_points=300)
        # Scale and offset
        x = x * 0.9 + cx
        y = y * 0.9 + cy
        
        if isprime(kn):
            ax.fill(x, y, color='#FFCDD2', alpha=0.7)
            ax.plot(x, y, color='#B71C1C', linewidth=1.5)
        else:
            ax.fill(x, y, color='#C8E6C9', alpha=0.7)
            ax.plot(x, y, color='#2E7D32', linewidth=1.5)
        
        factors = factorint(kn) if kn > 1 else {}
        fstr = "×".join(str(p) + (f"^{e}" if e > 1 else "")
                      for p, e in sorted(factors.items())) if factors else "src"
        label = f"{kn}" if isprime(kn) else f"{kn}={fstr}"
        ax.text(cx, cy - 1.15, label, ha='center', fontsize=7, fontweight='bold' if isprime(kn) else 'normal')
    
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('Key RAS Shapes\nRed=Prime (resist/rigid)  Green=Composite (give/flex)')
    
    # ── Plot 4: Harmonic sum growth vs branching spread ──
    ax = axes[1][1]
    if harmonic_sums and angles_deg is not None and len(angles_deg) > 0:
        ax.scatter(harmonic_sums, angles_deg, c=gr_ratios, cmap='RdYlGn_r', 
                  s=20, alpha=0.7, zorder=3)
        cbar = plt.colorbar(ax.collections[0], ax=ax, shrink=0.8)
        cbar.set_label('Give/Resist ratio', fontsize=9)
    
    ax.axhline(y=GOLDEN_DEG, color='#4CAF50', linestyle='--', linewidth=2, alpha=0.7)
    ax.set_xlabel('Prime harmonic sum H(p)')
    ax.set_ylabel('Branching angle (°)')
    ax.set_title('Harmonic Growth vs Angle\nDoes expanding vocabulary → golden angle?')
    ax.grid(True, alpha=0.3)
    
    fig.suptitle('Prime Tree — Angle Evolution & Give/Resist Analysis\n'
                 '"Each species is an experimental set architecture" — Day 9',
                 fontsize=14, fontweight='bold', y=1.02)
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
        print(f"Saved: {save_path}")
    plt.close()


# ─── RAS Tree (fixed) ───

def plot_ras_tree(max_n=24, save_path=None):
    """Visual tree where each node is drawn as its RAS shape."""
    fig, ax = plt.subplots(1, 1, figsize=(14, max(16, max_n * 0.6)))
    
    trunk_x = 0
    trunk_y = 0
    node_positions = {}
    primes_so_far = []
    
    comp_color_map = {1: '#BBDEFB', 2: '#C8E6C9', 3: '#FFF9C4'}
    
    for n in range(1, max_n + 1):
        if n == 1:
            node_positions[1] = (0, 0)
            ax.plot(0, 0, '*', color='gold', markersize=25, markeredgecolor='#FF8F00',
                   markeredgewidth=1.5, zorder=10)
            ax.annotate('1 (Source)', (0, 0), xytext=(0.5, 0.1), fontsize=10,
                       color='#FF8F00', fontweight='bold')
            trunk_y -= 1.4
            continue
        
        prime = isprime(n)
        
        if prime:
            primes_so_far.append(n)
            pos = (trunk_x, trunk_y)
            node_positions[n] = pos
            
            # Draw RAS shape at this position
            x, y = ras_shape(n, num_points=200)
            x = x * 0.4 + pos[0]
            y = y * 0.4 + pos[1]
            ax.fill(x, y, color='#FFCDD2', alpha=0.8, zorder=5)
            ax.plot(x, y, color='#B71C1C', linewidth=1.5, zorder=5)
            
            ax.annotate(f'{n}', pos, xytext=(0.5, 0), textcoords='offset fontsize',
                       fontsize=11, fontweight='bold', color='#B71C1C', zorder=6)
            
            # Trunk edge
            if len(primes_so_far) > 1:
                pp = node_positions[primes_so_far[-2]]
                ax.plot([pp[0], pos[0]], [pp[1], pos[1]], '-', color='#FF5722',
                       linewidth=3, alpha=0.5, zorder=1)
            elif 1 in node_positions:
                pp = node_positions[1]
                ax.plot([pp[0], pos[0]], [pp[1], pos[1]], '-', color='#FFA726',
                       linewidth=2.5, alpha=0.5, zorder=1)
            
            trunk_y -= 1.4
            
        else:
            factors = factorint(n)
            spf = min(factors.keys())
            om = omega(n)
            bo = bigomega(n)
            
            # Evolving angle!
            if len(primes_so_far) > 0:
                ang = evolving_angle(n, primes_so_far)
            else:
                ang = np.pi / 4
            
            # Direction based on smallest factor: 2=left, 3=right, else by 6k±1
            if spf == 2:
                direction = -1
            elif spf == 3:
                direction = 1
            else:
                direction = -1 if (spf + 1) % 6 == 0 else 1
            
            # Distance by complexity, angle modulated by evolution
            radius = 0.8 + bo * 0.35
            x_offset = direction * radius * np.cos(ang * 0.5)
            y_offset = -radius * np.sin(ang * 0.5) * 0.3
            
            nearest_prime = max([p for p in primes_so_far if p <= n], default=2)
            parent_pos = node_positions.get(nearest_prime, (0, trunk_y))
            
            composites_since = [i for i in range(nearest_prime + 1, n + 1) if not isprime(i)]
            stack_idx = composites_since.index(n) if n in composites_since else 0
            y_stack = -0.45 * stack_idx
            
            pos = (parent_pos[0] + x_offset, parent_pos[1] + y_offset + y_stack)
            node_positions[n] = pos
            
            # Draw RAS shape
            comp_color = comp_color_map.get(om, '#CE93D8')
            sx, sy = ras_shape(n, num_points=150)
            scale = 0.25 + give_resist_ratio(n) * 0.3  # more flex = bigger shape
            sx = sx * scale + pos[0]
            sy = sy * scale + pos[1]
            ax.fill(sx, sy, color=comp_color, alpha=0.7, zorder=4)
            ax.plot(sx, sy, color='#1565C0', linewidth=0.8, zorder=4)
            
            fstr = "×".join(str(p) + (f"^{e}" if e > 1 else "")
                          for p, e in sorted(factors.items()))
            gr = give_resist_ratio(n)
            ax.annotate(f'{n}={fstr}', pos, xytext=(0.4, -0.1), textcoords='offset fontsize',
                       fontsize=7, color='#555', zorder=6)
            
            # Branch edge
            ax.plot([parent_pos[0], pos[0]], [parent_pos[1], pos[1]], '-',
                   color='#90CAF9', linewidth=0.8 + gr * 3, alpha=0.5, zorder=1)
    
    ax.set_title(f'Prime Tree with RAS Shapes (1..{max_n})\n'
                 f'Shape = factorisation boundary | Size = flex factor (give/resist)\n'
                 f'Rigid primes (red) on trunk | Flexible composites (coloured) branch',
                 fontsize=13, fontweight='bold', pad=15)
    
    legend_elements = [
        Line2D([0], [0], marker='*', color='w', markerfacecolor='gold', markersize=15, label='1 (Source)'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#FFCDD2', markersize=12,
               markeredgecolor='#B71C1C', label='Prime (resist/rigid)'),
        Line2D([0], [0], marker='s', color='w', markerfacecolor='#BBDEFB', markersize=10, label='Composite ω=1 (p^k)'),
        Line2D([0], [0], marker='s', color='w', markerfacecolor='#C8E6C9', markersize=10, label='Composite ω=2'),
        Line2D([0], [0], marker='s', color='w', markerfacecolor='#FFF9C4', markersize=10, label='Composite ω=3'),
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=10, framealpha=0.9)
    
    ax.set_aspect('equal')
    ax.axis('off')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
        print(f"Saved: {save_path}")
    plt.close()


# ─── Main ───

if __name__ == '__main__':
    print("=" * 80)
    print("PRIME TREE — PLANT MORPHOLOGY TABLE")
    print("=" * 80)
    print()
    
    print(f"{'n':>3} {'P?':>3} {'sopfr':>5} {'Ω':>3} {'ω':>3} {'G/R':>6} {'m-sym':>5} {'Flex':>8} {'Plant Analogy'}")
    print("─" * 90)
    
    for n in range(1, 31):
        p = isprime(n)
        sf = sopfr(n)
        bo = bigomega(n)
        om = omega(n)
        m = max(om + 1, 1)
        gr = give_resist_ratio(n)
        
        if n == 1:
            flex = "source"
            analogy = "seed / origin point"
        elif p:
            flex = "RIGID"
            analogy = f"structural stem (p={n})"
        elif om == 1:
            factors = factorint(n)
            base = list(factors.keys())[0]
            exp = list(factors.values())[0]
            flex = f"linear"
            if base == 2:
                analogy = f"bamboo internode (2^{exp})"
            elif base == 3:
                analogy = f"clover/trefoil (3^{exp})"
            else:
                analogy = f"repeat-{base} (whorl)"
        else:
            factors = factorint(n)
            flex = f"FLEX-{om}"
            if 2 in factors and 3 in factors and 5 in factors:
                analogy = "compound inflorescence (2×3×5)"
            elif 2 in factors and 3 in factors:
                analogy = "compound leaf (dicot)"
            elif 5 in factors:
                analogy = "flower/petal structure"
            elif 7 in factors:
                analogy = "emergence branch (novel)"
            else:
                analogy = "multi-fork branch"
        
        mark = " ●" if p else "  "
        print(f"{n:>3}{mark} {sf:>5} {bo:>3} {om:>3} {gr:>6.3f} {m:>5}  {flex:>8}  {analogy}")
    
    print("\n\n📊 Generating visualisations...\n")
    
    # Gallery
    print("1. RAS Gallery (1..30)...")
    plot_ras_gallery(30, save_path=f'{OUT_DIR}/ras_gallery_30.png')
    
    # Tree with RAS shapes
    print("2. RAS Tree (1..30)...")
    plot_ras_tree(30, save_path=f'{OUT_DIR}/prime_tree_ras_30.png')
    
    # Angle evolution analysis
    print("3. Angle Evolution (1..100)...")
    plot_angle_evolution(100, save_path=f'{OUT_DIR}/angle_evolution_100.png')
    
    print("\n✅ Done! 🌿")
