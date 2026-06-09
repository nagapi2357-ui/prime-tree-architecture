#!/usr/bin/env python3
"""
Self-Evolving Prime Tree — v3
Day 9 (3²) — Adrian & Nagaπ

THE PRINCIPLE: The shape IS the instruction.
  factorisation → RAS boundary → lobe positions → branching angles → tree growth

No human-imposed degrees. The number tells you where to grow.

Each number's RAS shape has lobes (minima in the radial profile).
These lobes ARE the branch attachment points. Primes have smooth
boundaries (few/shallow lobes = rigid, few branches). Composites
have deep lobes (flexible, many branches).

The tree grows by:
1. Start at Source (1)
2. For each n, compute its RAS shape
3. Find the lobe positions (local minima of r(θ))
4. These lobes are where child branches attach
5. The DEPTH of each lobe = how far the branch reaches
6. The tree literally grows from its own mathematics
"""

import sys
sys.path.insert(0, '/Users/ClawdBot/.openclaw/workspace/projects/rational-superformula')

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, FancyArrowPatch
from matplotlib.lines import Line2D
from sympy import isprime, factorint
from collections import defaultdict

OUT_DIR = '/Users/ClawdBot/.openclaw/workspace/projects/prime-tree'


# ─── RAS Core (overflow-safe) ───

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


def ras_radial_profile(n, num_points=360):
    """
    Compute the RAS radial profile r(θ) for number n.
    Returns (theta, rho) arrays — the polar boundary.
    """
    if n <= 1:
        theta = np.linspace(0, 2 * np.pi, num_points, endpoint=False)
        return theta, np.ones(num_points)
    
    p = sopfr(n)
    q = bigomega(n)
    m = max(omega(n) + 1, 1)
    
    # Cap exponents for numerical stability
    max_exp = 12
    if p + q > max_exp:
        scale = max_exp / (p + q)
        p_vis = max(p * scale, 0.5)
        q_vis = max(q * scale, 0.5)
    else:
        p_vis = max(p, 0.5)
        q_vis = max(q, 0.5)
    
    theta = np.linspace(0, 2 * np.pi, num_points, endpoint=False)
    m_theta = m * theta
    
    cos_part = np.abs(np.cos(m_theta)) ** p_vis
    sin_part = np.abs(np.sin(m_theta)) ** q_vis
    
    rho = (cos_part + sin_part) ** (-1.0 / (p_vis + q_vis))
    
    rho_max = np.max(rho)
    if rho_max > 0:
        rho = rho / rho_max
    
    return theta, rho


def find_lobes(theta, rho, min_depth=0.01):
    """
    Find lobe positions = local MINIMA in the radial profile.
    These are the "valleys" in the shape — the natural branch attachment points.
    
    Returns list of (angle, depth) tuples.
    depth = 1 - rho_at_minimum (deeper valley = stronger branch signal)
    """
    n = len(rho)
    lobes = []
    
    for i in range(n):
        prev_r = rho[(i - 1) % n]
        curr_r = rho[i]
        next_r = rho[(i + 1) % n]
        
        if curr_r < prev_r and curr_r < next_r:
            depth = 1.0 - curr_r
            if depth >= min_depth:
                lobes.append((theta[i], depth, curr_r))
    
    return lobes


def find_peaks(theta, rho):
    """
    Find peak positions = local MAXIMA in the radial profile.
    These are the "tips" — the growth points / apical meristems.
    """
    n = len(rho)
    peaks = []
    
    for i in range(n):
        prev_r = rho[(i - 1) % n]
        curr_r = rho[i]
        next_r = rho[(i + 1) % n]
        
        if curr_r > prev_r and curr_r > next_r:
            peaks.append((theta[i], curr_r))
    
    return peaks


# ─── Self-Evolving Tree Engine ───

class PrimeTree:
    """
    Self-evolving tree where RAS shapes determine branching.
    
    Growth rules:
    - Primes go on the trunk (main stem) — their smooth shape means
      few/shallow lobes → few branch points → structural rigidity
    - Composites branch FROM the trunk at lobe positions of their
      parent prime's shape
    - Branch LENGTH = lobe depth × give/resist ratio
    - Branch ANGLE = lobe angle (from RAS, no human input)
    """
    
    def __init__(self, max_n=30):
        self.max_n = max_n
        self.nodes = {}  # n → (x, y, is_prime, parent_n)
        self.edges = []  # (n1, n2, weight)
        self.primes = []
        self.trunk_direction = -np.pi / 2  # grow downward initially
        self.trunk_step = 1.5
        
    def grow(self):
        """Grow the tree from 1 to max_n."""
        # Source
        self.nodes[1] = (0, 0, False, None)
        cx, cy = 0, 0
        
        for n in range(2, self.max_n + 1):
            if isprime(n):
                self._grow_prime(n, cx, cy)
                cx, cy = self.nodes[n][:2]
            else:
                self._grow_composite(n)
    
    def _grow_prime(self, n, parent_x, parent_y):
        """
        Grow a prime node on the trunk.
        Direction evolves based on the PREVIOUS prime's RAS shape —
        the peak direction of the parent determines trunk growth direction.
        """
        self.primes.append(n)
        
        if len(self.primes) > 1:
            # Use previous prime's RAS to find the dominant growth direction
            prev_prime = self.primes[-2]
            theta, rho = ras_radial_profile(prev_prime, 360)
            peaks = find_peaks(theta, rho)
            
            if peaks:
                # Find peak closest to current trunk direction
                # This makes the trunk "follow" the shape's preferred direction
                best_peak = min(peaks, 
                    key=lambda p: abs(self._angle_diff(p[0] + self.trunk_direction, self.trunk_direction)))
                
                # Blend: mostly continue straight, but nudge toward peak
                nudge = self._angle_diff(best_peak[0] + self.trunk_direction - np.pi/2, 
                                          self.trunk_direction) * 0.15
                self.trunk_direction += nudge
        
        # Step along trunk
        new_x = parent_x + self.trunk_step * np.cos(self.trunk_direction)
        new_y = parent_y + self.trunk_step * np.sin(self.trunk_direction)
        
        self.nodes[n] = (new_x, new_y, True, self.primes[-2] if len(self.primes) > 1 else 1)
        parent = self.primes[-2] if len(self.primes) > 1 else 1
        self.edges.append((parent, n, 1.0))
    
    def _grow_composite(self, n):
        """
        Grow a composite node as a branch.
        The branch emerges from the RAS lobe of its nearest prime parent.
        Angle = lobe angle, Length = lobe depth × flex factor.
        """
        factors = factorint(n)
        spf = min(factors.keys())
        
        # Find parent prime (largest prime ≤ n)
        parent_prime = max([p for p in self.primes if p <= n], default=2)
        parent_pos = self.nodes[parent_prime][:2]
        
        # Get parent prime's RAS lobes
        theta, rho = ras_radial_profile(parent_prime, 360)
        lobes = find_lobes(theta, rho, min_depth=0.005)
        
        if not lobes:
            # Very smooth shape (large prime) — minimal branching
            # Use a small offset perpendicular to trunk
            angle = self.trunk_direction + np.pi / 2 * (1 if spf % 3 == 0 else -1)
            depth = 0.3
        else:
            # Which lobe does this composite attach to?
            # Composites are assigned to lobes based on their factorisation
            # Use the composite's index among siblings to pick a lobe
            siblings = [i for i in range(parent_prime + 1, n + 1) if not isprime(i)]
            sib_idx = siblings.index(n) if n in siblings else 0
            
            lobe = lobes[sib_idx % len(lobes)]
            angle = lobe[0] + self.trunk_direction + np.pi / 2  # orient relative to trunk
            depth = lobe[1]
        
        # Branch length scales with:
        # - lobe depth (how much the shape "invites" branching there)
        # - give/resist ratio (how flexible this composite is)
        # - bigomega (complexity = more reach)
        gr = give_resist_ratio(n)
        bo = bigomega(n)
        branch_length = (0.5 + depth * 2.0) * (0.5 + gr) * (0.7 + bo * 0.15)
        
        new_x = parent_pos[0] + branch_length * np.cos(angle)
        new_y = parent_pos[1] + branch_length * np.sin(angle)
        
        self.nodes[n] = (new_x, new_y, False, parent_prime)
        self.edges.append((parent_prime, n, gr))
    
    @staticmethod
    def _angle_diff(a, b):
        """Signed angular difference."""
        d = (a - b) % (2 * np.pi)
        if d > np.pi:
            d -= 2 * np.pi
        return d
    
    def plot(self, save_path=None, show_shapes=True, show_lobe_analysis=True):
        """Plot the self-evolving tree."""
        
        if show_lobe_analysis:
            fig = plt.figure(figsize=(20, 14))
            gs = fig.add_gridspec(2, 3, height_ratios=[2, 1], hspace=0.3, wspace=0.3)
            ax_tree = fig.add_subplot(gs[0, :])
            ax_lobe_count = fig.add_subplot(gs[1, 0])
            ax_lobe_depth = fig.add_subplot(gs[1, 1])
            ax_shapes = fig.add_subplot(gs[1, 2])
        else:
            fig, ax_tree = plt.subplots(1, 1, figsize=(16, 12))
        
        # ── Draw tree ──
        
        # Edges first
        for n1, n2, weight in self.edges:
            if n1 in self.nodes and n2 in self.nodes:
                x1, y1 = self.nodes[n1][:2]
                x2, y2 = self.nodes[n2][:2]
                is_trunk = self.nodes[n2][2]  # n2 is prime
                
                if is_trunk:
                    ax_tree.plot([x1, x2], [y1, y2], '-', color='#FF5722', 
                               linewidth=3, alpha=0.6, zorder=2)
                else:
                    # Branch thickness from G/R
                    lw = 0.5 + weight * 4
                    ax_tree.plot([x1, x2], [y1, y2], '-', color='#81C784',
                               linewidth=lw, alpha=0.4, zorder=1)
        
        # Nodes with RAS shapes
        for n, (x, y, is_p, parent) in self.nodes.items():
            if n == 1:
                ax_tree.plot(x, y, '*', color='gold', markersize=22,
                           markeredgecolor='#FF8F00', markeredgewidth=2, zorder=10)
                ax_tree.annotate('1\nSource', (x, y), xytext=(0.3, 0.2),
                               textcoords='offset fontsize', fontsize=9,
                               color='#FF8F00', fontweight='bold', zorder=11)
                continue
            
            if show_shapes:
                theta, rho = ras_radial_profile(n, 200)
                
                # Scale shape to node
                if is_p:
                    scale = 0.45
                    fill_color = '#FFCDD2'
                    edge_color = '#B71C1C'
                    lw = 2.0
                else:
                    gr = give_resist_ratio(n)
                    scale = 0.2 + gr * 0.5
                    om = omega(n)
                    fill_colors = {1: '#BBDEFB', 2: '#C8E6C9', 3: '#FFF9C4'}
                    fill_color = fill_colors.get(om, '#CE93D8')
                    edge_color = '#1565C0'
                    lw = 1.0
                
                sx = rho * np.cos(theta) * scale + x
                sy = rho * np.sin(theta) * scale + y
                
                ax_tree.fill(sx, sy, color=fill_color, alpha=0.75, zorder=5)
                ax_tree.plot(sx, sy, color=edge_color, linewidth=lw, zorder=5)
                
                # Mark lobes on composites
                if not is_p and self.max_n <= 30:
                    lobes = find_lobes(theta, rho, min_depth=0.02)
                    for lobe_angle, lobe_depth, lobe_r in lobes[:4]:
                        lx = lobe_r * np.cos(lobe_angle) * scale + x
                        ly = lobe_r * np.sin(lobe_angle) * scale + y
                        ax_tree.plot(lx, ly, '.', color='#E65100', markersize=3, zorder=6)
            else:
                if is_p:
                    ax_tree.plot(x, y, 'o', color='#FF5722', markersize=12, zorder=5)
                else:
                    ax_tree.plot(x, y, 's', color='#90CAF9', markersize=8, zorder=4)
            
            # Labels
            if is_p:
                ax_tree.annotate(str(n), (x, y), xytext=(0.5, 0.1),
                               textcoords='offset fontsize', fontsize=10,
                               fontweight='bold', color='#B71C1C', zorder=7)
            elif self.max_n <= 50:
                factors = factorint(n)
                fstr = "×".join(str(p) + (f"^{e}" if e > 1 else "")
                              for p, e in sorted(factors.items()))
                ax_tree.annotate(f'{n}', (x, y), xytext=(0.3, -0.2),
                               textcoords='offset fontsize', fontsize=7,
                               color='#666', zorder=7)
        
        ax_tree.set_title(
            f'Self-Evolving Prime Tree (1..{self.max_n})\n'
            f'RAS shape → lobe positions → branching angles\n'
            f'The number IS the instruction. No degrees imposed.',
            fontsize=13, fontweight='bold', pad=10)
        
        legend_elements = [
            Line2D([0], [0], marker='*', color='w', markerfacecolor='gold', markersize=15, label='Source (1)'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor='#FFCDD2', markersize=12,
                   markeredgecolor='#B71C1C', markeredgewidth=1.5, label='Prime (resist/rigid trunk)'),
            Line2D([0], [0], marker='s', color='w', markerfacecolor='#C8E6C9', markersize=10,
                   markeredgecolor='#1565C0', label='Composite (give/flex branch)'),
            Line2D([0], [0], marker='.', color='#E65100', markersize=8, label='Lobe (branch attachment)'),
        ]
        ax_tree.legend(handles=legend_elements, loc='upper right', fontsize=9, framealpha=0.9)
        ax_tree.set_aspect('equal')
        ax_tree.axis('off')
        
        # ── Analysis panels ──
        if show_lobe_analysis:
            # Lobe count by number
            ns = list(range(2, self.max_n + 1))
            lobe_counts = []
            lobe_depths_avg = []
            
            for n in ns:
                theta, rho = ras_radial_profile(n, 360)
                lobes = find_lobes(theta, rho, min_depth=0.005)
                lobe_counts.append(len(lobes))
                lobe_depths_avg.append(np.mean([l[1] for l in lobes]) if lobes else 0)
            
            prime_mask = [isprime(n) for n in ns]
            comp_mask = [not isprime(n) for n in ns]
            
            # Panel 1: Lobe count
            ax_lobe_count.bar([n for n, ip in zip(ns, prime_mask) if ip],
                             [lc for lc, ip in zip(lobe_counts, prime_mask) if ip],
                             color='#FFCDD2', edgecolor='#B71C1C', label='Primes')
            ax_lobe_count.bar([n for n, ip in zip(ns, comp_mask) if ip],
                             [lc for lc, ip in zip(lobe_counts, comp_mask) if ip],
                             color='#C8E6C9', edgecolor='#2E7D32', label='Composites')
            ax_lobe_count.set_xlabel('n')
            ax_lobe_count.set_ylabel('Number of lobes')
            ax_lobe_count.set_title('Lobe Count\n(branch attachment points)')
            ax_lobe_count.legend(fontsize=8)
            ax_lobe_count.grid(True, alpha=0.3)
            
            # Panel 2: Average lobe depth
            ax_lobe_depth.scatter([n for n, ip in zip(ns, prime_mask) if ip],
                                [ld for ld, ip in zip(lobe_depths_avg, prime_mask) if ip],
                                c='#FF5722', s=40, label='Primes', zorder=3)
            ax_lobe_depth.scatter([n for n, ip in zip(ns, comp_mask) if ip],
                                [ld for ld, ip in zip(lobe_depths_avg, comp_mask) if ip],
                                c='#4CAF50', s=25, label='Composites', zorder=3)
            ax_lobe_depth.set_xlabel('n')
            ax_lobe_depth.set_ylabel('Avg lobe depth')
            ax_lobe_depth.set_title('Lobe Depth = Branch Strength\n(deeper = stronger branch signal)')
            ax_lobe_depth.legend(fontsize=8)
            ax_lobe_depth.grid(True, alpha=0.3)
            
            # Panel 3: Key shapes with lobes marked
            key_nums = [2, 6, 7, 12, 15, 30]
            for idx, kn in enumerate(key_nums):
                r_idx, c_idx = divmod(idx, 3)
                cx = c_idx * 2.8
                cy = -r_idx * 2.8
                
                theta, rho = ras_radial_profile(kn, 360)
                sx = rho * np.cos(theta) * 1.0 + cx
                sy = rho * np.sin(theta) * 1.0 + cy
                
                color = '#FFCDD2' if isprime(kn) else '#C8E6C9'
                edge = '#B71C1C' if isprime(kn) else '#2E7D32'
                ax_shapes.fill(sx, sy, color=color, alpha=0.6)
                ax_shapes.plot(sx, sy, color=edge, linewidth=1.5)
                
                # Mark lobes
                lobes = find_lobes(theta, rho, min_depth=0.005)
                for la, ld, lr in lobes:
                    lx = lr * np.cos(la) * 1.0 + cx
                    ly = lr * np.sin(la) * 1.0 + cy
                    ax_shapes.plot(lx, ly, 'o', color='#E65100', markersize=5, zorder=6)
                    # Draw branch line from lobe outward
                    bx = (lr + ld * 0.8) * np.cos(la) * 1.0 + cx
                    by = (lr + ld * 0.8) * np.sin(la) * 1.0 + cy
                    ax_shapes.plot([lx, bx], [ly, by], '-', color='#E65100', 
                                 linewidth=1, alpha=0.6)
                
                # Mark peaks (growth tips)
                peaks = find_peaks(theta, rho)
                for pa, pr in peaks:
                    px = pr * np.cos(pa) * 1.0 + cx
                    py = pr * np.sin(pa) * 1.0 + cy
                    ax_shapes.plot(px, py, '^', color='#1B5E20', markersize=4, zorder=6)
                
                factors = factorint(kn) if kn > 1 else {}
                fstr = "×".join(str(p) + (f"^{e}" if e > 1 else "")
                              for p, e in sorted(factors.items())) if factors else ""
                label = f"{kn}" if isprime(kn) else f"{kn}={fstr}"
                ax_shapes.text(cx, cy - 1.4, f"{label}\n{len(lobes)} lobes", 
                             ha='center', fontsize=8, fontweight='bold' if isprime(kn) else 'normal')
            
            ax_shapes.set_aspect('equal')
            ax_shapes.axis('off')
            ax_shapes.set_title('Lobe Analysis\n● lobes (branch) ▲ peaks (growth)')
        
        fig.suptitle(
            '"Each species is an experimental set architecture"\n'
            'The shape IS the branching instruction — Day 9 (3²)',
            fontsize=14, fontweight='bold', y=1.01)
        
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
            print(f"Saved: {save_path}")
        plt.close()


# ─── Lobe Analysis Table ───

def lobe_analysis_table(max_n=30):
    """Print detailed lobe analysis for each number."""
    print(f"{'n':>3} {'P?':>3} {'ω':>2} {'Ω':>2} {'sopfr':>5} {'m-sym':>5} "
          f"{'Lobes':>5} {'Peaks':>5} {'AvgDepth':>8} {'MaxDepth':>8} {'G/R':>6}")
    print("─" * 80)
    
    for n in range(1, max_n + 1):
        theta, rho = ras_radial_profile(n, 360)
        lobes = find_lobes(theta, rho, min_depth=0.005)
        peaks = find_peaks(theta, rho)
        
        avg_depth = np.mean([l[1] for l in lobes]) if lobes else 0
        max_depth = max([l[1] for l in lobes]) if lobes else 0
        
        mark = " ●" if isprime(n) else "  "
        m = max(omega(n) + 1, 1)
        gr = give_resist_ratio(n)
        
        print(f"{n:>3}{mark} {omega(n):>2} {bigomega(n):>2} {sopfr(n):>5} {m:>5} "
              f"{len(lobes):>5} {len(peaks):>5} {avg_depth:>8.4f} {max_depth:>8.4f} {gr:>6.3f}")


# ─── Main ───

if __name__ == '__main__':
    print("=" * 80)
    print("SELF-EVOLVING PRIME TREE — LOBE ANALYSIS")
    print("The shape IS the instruction")
    print("=" * 80)
    print()
    
    lobe_analysis_table(30)
    
    print("\n\n📊 Growing self-evolving trees...\n")
    
    # Small tree with full analysis
    print("1. Tree 1..30 with lobe analysis...")
    tree30 = PrimeTree(30)
    tree30.grow()
    tree30.plot(save_path=f'{OUT_DIR}/self_evolving_tree_30.png', 
                show_shapes=True, show_lobe_analysis=True)
    
    # Larger tree
    print("2. Tree 1..60 (structure)...")
    tree60 = PrimeTree(60)
    tree60.grow()
    tree60.plot(save_path=f'{OUT_DIR}/self_evolving_tree_60.png',
                show_shapes=True, show_lobe_analysis=True)
    
    # Large tree — shapes off for clarity
    print("3. Tree 1..100 (dots)...")
    tree100 = PrimeTree(100)
    tree100.grow()
    tree100.plot(save_path=f'{OUT_DIR}/self_evolving_tree_100.png',
                 show_shapes=False, show_lobe_analysis=True)
    
    print("\n✅ Done! The tree grew itself. 🌿")
