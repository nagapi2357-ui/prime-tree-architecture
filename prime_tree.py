#!/usr/bin/env python3
"""
Prime Binary Tree — Three Branching Models
Day 9 (3² = new page) — Adrian & Nagaπ

Models:
  1. Torsion Bridge: ±1 from 6k → left/right twist from spine
  2. Mod 24 Wheel: 8 coprime residues mod 24 → octave spokes
  3. Harmonic Ratio: angle evolves with accumulated prime harmonic sum

Usage:
  python prime_tree.py [--max N] [--mode torsion|mod24|harmonic|all] [--visual]
"""

import math
import argparse
from collections import defaultdict

# ─── Primality & factorisation ───

def is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return False
        i += 6
    return True

def smallest_prime_factor(n):
    if n < 2: return n
    if n % 2 == 0: return 2
    if n % 3 == 0: return 3
    i = 5
    while i * i <= n:
        if n % i == 0: return i
        if n % (i + 2) == 0: return i + 2
        i += 6
    return n

def prime_factors(n):
    """Return list of prime factors with multiplicity."""
    factors = []
    while n > 1:
        p = smallest_prime_factor(n)
        factors.append(p)
        n //= p
    return factors

def primes_up_to(n):
    return [i for i in range(2, n + 1) if is_prime(i)]

# ─── ASCII Tree ───

def ascii_tree(max_n, mode='torsion'):
    """
    Simple ASCII visualisation.
    Main trunk runs down the left. Primes get a dot on the trunk.
    Composites branch right, with depth = number of prime factors.
    """
    lines = []
    lines.append(f"  Prime Tree (1..{max_n}) — mode: {mode}")
    lines.append(f"  {'─' * 40}")
    
    primes_so_far = []
    harmonic_sum = 0.0
    
    for n in range(1, max_n + 1):
        if n == 1:
            lines.append(f"  {'●':>3}  1 (source)")
            continue
        
        prime = is_prime(n)
        
        if prime:
            primes_so_far.append(n)
            harmonic_sum += 1.0 / n
            
            # Torsion: which side of 6k?
            if n == 2:
                torsion_label = "even prime"
            elif n == 3:
                torsion_label = "odd prime"
            else:
                k = (n + 1) / 6
                if abs(k - round(k)) < 0.01:
                    torsion_label = f"6k-1 (k={int(round(k))})"
                else:
                    torsion_label = f"6k+1 (k={int(round((n-1)/6))})"
            
            mod24_label = f"mod24={n % 24}"
            harm_label = f"H={harmonic_sum:.3f}"
            
            if mode == 'torsion':
                info = torsion_label
            elif mode == 'mod24':
                info = mod24_label
            elif mode == 'harmonic':
                info = harm_label
            else:
                info = f"{torsion_label} | {mod24_label} | {harm_label}"
            
            lines.append(f"  ● {n:>3} PRIME  [{info}]")
        else:
            factors = prime_factors(n)
            depth = len(factors)
            branch = "─" * depth + "○"
            factor_str = "×".join(str(f) for f in factors)
            
            # Show how this composite relates to its factors
            if mode == 'torsion':
                # Composite torsion = inherited from smallest factor
                spf = factors[0]
                if spf == 2:
                    info = "even"
                elif spf == 3:
                    info = "triple"
                else:
                    k = (spf + 1) / 6
                    if abs(k - round(k)) < 0.01:
                        info = f"←{spf}(6k-1)"
                    else:
                        info = f"←{spf}(6k+1)"
            elif mode == 'mod24':
                info = f"mod24={n % 24}"
            elif mode == 'harmonic':
                info = f"H={harmonic_sum:.3f}"
            else:
                info = f"mod24={n % 24} | H={harmonic_sum:.3f}"
            
            indent = "  │" + " " * 2
            lines.append(f"{indent}{branch} {n:>3} = {factor_str}  [{info}]")
    
    # Summary
    p_count = len(primes_so_far)
    lines.append(f"\n  Primes: {p_count}/{max_n}  Harmonic sum: {harmonic_sum:.4f}")
    if primes_so_far:
        lines.append(f"  ln(ln({max_n})) = {math.log(math.log(max_n)):.4f}" if max_n > 1 else "")
    
    return "\n".join(lines)


# ─── Visual Plot (matplotlib) ───

def compute_tree_positions(max_n, mode='torsion'):
    """
    Compute (x, y) for each number, plus edges to parent/factors.
    Returns: nodes dict {n: (x, y, is_prime, factors)}, edges list [(n1, n2)]
    """
    nodes = {}
    edges = []
    primes_so_far = []
    harmonic_sum = 0.0
    
    # Trunk goes along y-axis (downward)
    trunk_y = 0
    trunk_x = 0
    
    # Track prime positions on trunk
    prime_positions = {}
    
    for n in range(1, max_n + 1):
        prime = is_prime(n)
        
        if prime:
            primes_so_far.append(n)
            harmonic_sum += 1.0 / n
        
        if n == 1:
            nodes[1] = (0, 0, False, [])
            trunk_y -= 1
            continue
        
        if prime:
            # Prime goes on the trunk
            nodes[n] = (trunk_x, trunk_y, True, [])
            prime_positions[n] = (trunk_x, trunk_y)
            
            # Edge from previous trunk node
            prev_trunk = max([k for k in nodes if nodes[k][2] or k == 1], default=1)
            edges.append((prev_trunk, n))
            trunk_y -= 1
            
        else:
            # Composite branches from trunk
            factors = prime_factors(n)
            spf = factors[0]
            depth = len(factors)
            
            if mode == 'torsion':
                # Branch direction based on 6k±1 of smallest prime factor
                if spf == 2:
                    direction = -1  # left
                elif spf == 3:
                    direction = 1   # right
                else:
                    # 6k-1 → left, 6k+1 → right
                    if (spf + 1) % 6 == 0:
                        direction = -1
                    else:
                        direction = 1
                
                branch_x = trunk_x + direction * depth * 0.5
                branch_y = trunk_y
                
            elif mode == 'mod24':
                # Branch angle = (n mod 24) / 24 * 2π, mapped to one of 8 spokes
                residue = n % 24
                # Map to angle
                angle = (residue / 24.0) * 2 * math.pi
                radius = depth * 0.6
                branch_x = trunk_x + radius * math.cos(angle)
                branch_y = trunk_y + radius * math.sin(angle) * 0.3  # squash vertically
                
            elif mode == 'harmonic':
                # Branch angle evolves with harmonic sum
                # Use harmonic sum as a scaling factor for the spread
                angle = (n * harmonic_sum) % (2 * math.pi)
                # Alternate sides based on factor parity
                side = 1 if sum(factors) % 2 == 0 else -1
                radius = depth * 0.4 * (1 + harmonic_sum * 0.3)
                branch_x = trunk_x + side * radius * abs(math.cos(angle))
                branch_y = trunk_y + radius * math.sin(angle) * 0.2
            
            nodes[n] = (branch_x, branch_y, False, factors)
            
            # Edge from nearest prime factor on trunk
            if spf in prime_positions:
                edges.append((spf, n))
            else:
                # Edge from trunk
                nearest_prime = max([p for p in primes_so_far if p <= n], default=1)
                edges.append((nearest_prime, n))
            
            trunk_y -= 0.3  # composites advance trunk slightly
    
    return nodes, edges


def plot_tree(max_n, mode='all', save_path=None):
    """Plot the prime tree visually."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    
    modes = ['torsion', 'mod24', 'harmonic'] if mode == 'all' else [mode]
    
    fig, axes = plt.subplots(1, len(modes), figsize=(7 * len(modes), max(12, max_n * 0.4)))
    if len(modes) == 1:
        axes = [axes]
    
    fig.suptitle(f'Prime Binary Tree — Numbers 1..{max_n}\nDay 9 (3²) — Branching Modes Compared', 
                 fontsize=14, fontweight='bold', y=0.98)
    
    mode_descriptions = {
        'torsion': 'Torsion Bridge\n(±1 from 6k → left/right)',
        'mod24': 'Mod 24 Wheel\n(8 coprime spokes)',
        'harmonic': 'Harmonic Ratio\n(evolving with prime sum)',
    }
    
    for ax, m in zip(axes, modes):
        nodes, edges = compute_tree_positions(max_n, m)
        
        # Draw edges
        for n1, n2 in edges:
            if n1 in nodes and n2 in nodes:
                x1, y1 = nodes[n1][0], nodes[n1][1]
                x2, y2 = nodes[n2][0], nodes[n2][1]
                color = '#cccccc' if not nodes[n2][2] else '#2196F3'
                lw = 1.5 if nodes[n2][2] else 0.5
                ax.plot([x1, x2], [y1, y2], color=color, linewidth=lw, alpha=0.6, zorder=1)
        
        # Draw nodes
        for n, (x, y, is_p, factors) in nodes.items():
            if is_p:
                ax.scatter(x, y, s=120, c='#FF5722', edgecolors='#B71C1C', 
                          linewidths=1.5, zorder=3, marker='o')
                ax.annotate(str(n), (x, y), textcoords="offset points", 
                           xytext=(8, 0), fontsize=8, fontweight='bold', color='#B71C1C')
            elif n == 1:
                ax.scatter(x, y, s=200, c='gold', edgecolors='#FF8F00',
                          linewidths=2, zorder=3, marker='*')
                ax.annotate('1\n(source)', (x, y), textcoords="offset points",
                           xytext=(10, -5), fontsize=7, color='#FF8F00')
            else:
                # Composite — size by number of factors
                size = 30 + len(factors) * 15
                ax.scatter(x, y, s=size, c='#90CAF9', edgecolors='#1565C0',
                          linewidths=0.5, zorder=2, marker='s', alpha=0.7)
                if max_n <= 50:
                    factor_str = "×".join(str(f) for f in factors)
                    ax.annotate(f'{n}', (x, y), textcoords="offset points",
                               xytext=(6, 0), fontsize=6, color='#555')
        
        ax.set_title(mode_descriptions[m], fontsize=11, pad=10)
        ax.set_aspect('equal' if m == 'mod24' else 'auto')
        ax.axis('off')
    
    # Legend
    prime_patch = mpatches.Patch(color='#FF5722', label='● Prime (trunk)')
    comp_patch = mpatches.Patch(color='#90CAF9', label='■ Composite (branch)')
    source_patch = mpatches.Patch(color='gold', label='★ Source (1)')
    fig.legend(handles=[source_patch, prime_patch, comp_patch], 
              loc='lower center', ncol=3, fontsize=10, frameon=False)
    
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
        print(f"Saved: {save_path}")
    
    plt.close()


# ─── Main ───

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Prime Binary Tree')
    parser.add_argument('--max', type=int, default=30, help='Max number (default 30)')
    parser.add_argument('--mode', choices=['torsion', 'mod24', 'harmonic', 'all'], 
                       default='all', help='Branching mode')
    parser.add_argument('--visual', action='store_true', help='Generate visual plot')
    parser.add_argument('--output', type=str, default=None, help='Output image path')
    args = parser.parse_args()
    
    # Always show ASCII first
    if args.mode == 'all':
        for m in ['torsion', 'mod24', 'harmonic']:
            print(ascii_tree(args.max, m))
            print()
    else:
        print(ascii_tree(args.max, args.mode))
    
    # Visual plot
    if args.visual:
        out = args.output or f'/Users/ClawdBot/.openclaw/workspace/projects/prime-tree/prime_tree_{args.max}.png'
        plot_tree(args.max, args.mode, save_path=out)
