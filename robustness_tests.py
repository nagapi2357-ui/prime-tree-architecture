#!/usr/bin/env python3
"""
Prime Tree — Robustness Tests
Day 9 (3²) — Adrian & Nagaπ

Three tests to GND our results before write-up:

TEST 1: SPIRAL ROBUSTNESS
  Does the trunk spiral for ALL blending factors, or only specific ones?
  Sweep blending from 0.01 to 0.99 and measure curvature.
  If it always curves: structural. If only sometimes: artifact.

TEST 2: LOBE DEPTH SEPARATION
  Is the prime/composite lobe depth separation real or an m-fold artifact?
  Test with different symmetry formulas. If separation persists: structural.
  Also: randomise m-fold and see if separation survives.

TEST 3: GOLDEN ANGLE CONVERGENCE
  Does the self-evolving branching converge toward 137.508°?
  Measure the average angular spacing between successive composite branches
  as n → ∞. Compare to golden angle, random, and uniform.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sympy import isprime, factorint
from collections import defaultdict

OUT_DIR = '/Users/ClawdBot/.openclaw/workspace/projects/prime-tree'


# ─── Shared RAS functions ───

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


def ras_radial_profile(n, num_points=360, m_override=None):
    """RAS radial profile with optional m-fold override for testing."""
    if n <= 1:
        theta = np.linspace(0, 2 * np.pi, num_points, endpoint=False)
        return theta, np.ones(num_points)
    
    p = sopfr(n)
    q = bigomega(n)
    m = m_override if m_override is not None else max(omega(n) + 1, 1)
    
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


def find_lobes(theta, rho, min_depth=0.005):
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
    n = len(rho)
    peaks = []
    for i in range(n):
        prev_r = rho[(i - 1) % n]
        curr_r = rho[i]
        next_r = rho[(i + 1) % n]
        if curr_r > prev_r and curr_r > next_r:
            peaks.append((theta[i], curr_r))
    return peaks


# ═══════════════════════════════════════════════════════════════════════
# TEST 1: SPIRAL ROBUSTNESS
# ═══════════════════════════════════════════════════════════════════════

def test_spiral_robustness(max_n=100, save_path=None):
    """
    Sweep the trunk blending factor from 0.01 to 0.99.
    For each, grow the tree and measure total trunk curvature.
    Curvature = sum of absolute angle changes between successive trunk segments.
    """
    print("=" * 70)
    print("TEST 1: SPIRAL ROBUSTNESS")
    print("Does the trunk spiral for ALL blending factors?")
    print("=" * 70)
    
    blend_factors = np.linspace(0.01, 0.99, 50)
    curvatures = []
    total_rotations = []  # how many full turns
    directions = []  # does it always curve the same way?
    
    for blend in blend_factors:
        trunk_dir = -np.pi / 2
        trunk_step = 1.5
        cx, cy = 0, 0
        primes = []
        
        angles = []  # successive trunk directions
        
        for n in range(2, max_n + 1):
            if not isprime(n):
                continue
            
            primes.append(n)
            
            if len(primes) > 1:
                prev_prime = primes[-2]
                theta, rho = ras_radial_profile(prev_prime, 360)
                peaks = find_peaks(theta, rho)
                
                if peaks:
                    # Find dominant peak
                    best_peak = max(peaks, key=lambda p: p[1])
                    nudge_angle = best_peak[0] + trunk_dir - np.pi / 2
                    
                    # Signed angular difference
                    diff = (nudge_angle - trunk_dir) % (2 * np.pi)
                    if diff > np.pi:
                        diff -= 2 * np.pi
                    
                    trunk_dir += diff * blend
            
            angles.append(trunk_dir)
            cx += trunk_step * np.cos(trunk_dir)
            cy += trunk_step * np.sin(trunk_dir)
        
        # Measure curvature: sum of absolute angle changes
        if len(angles) > 1:
            deltas = np.diff(angles)
            # Wrap to [-π, π]
            deltas = (deltas + np.pi) % (2 * np.pi) - np.pi
            total_curv = np.sum(np.abs(deltas))
            total_rot = np.sum(deltas) / (2 * np.pi)
            sign = np.sign(np.sum(deltas))
        else:
            total_curv = 0
            total_rot = 0
            sign = 0
        
        curvatures.append(total_curv)
        total_rotations.append(total_rot)
        directions.append(sign)
    
    # Analysis
    always_curves = all(c > 0.1 for c in curvatures)
    same_direction = len(set(int(d) for d in directions if d != 0)) == 1
    
    print(f"\n  Blending range: 0.01 → 0.99 ({len(blend_factors)} values)")
    print(f"  Min curvature:  {min(curvatures):.4f} rad")
    print(f"  Max curvature:  {max(curvatures):.4f} rad")
    print(f"  Always curves:  {'YES ✅' if always_curves else 'NO ❌'}")
    print(f"  Same direction: {'YES ✅' if same_direction else 'MIXED ⚠️'}")
    print(f"  Min rotations:  {min(total_rotations):.2f} turns")
    print(f"  Max rotations:  {max(total_rotations):.2f} turns")
    
    # Does curvature scale linearly with blend? Or is there a natural value?
    from scipy import stats as sp_stats
    slope, intercept, r_value, p_value, std_err = sp_stats.linregress(blend_factors, curvatures)
    print(f"\n  Curvature vs blend: r²={r_value**2:.4f}, slope={slope:.4f}")
    print(f"  {'LINEAR ✅ — curvature proportional to blend (structural)' if r_value**2 > 0.95 else 'NON-LINEAR — interesting!'}")
    
    # Zero-blend extrapolation
    zero_curv = intercept
    print(f"  Extrapolated curvature at blend=0: {zero_curv:.4f}")
    print(f"  {'Non-zero at origin — inherent curvature exists!' if abs(zero_curv) > 0.01 else 'Zero at origin — curvature requires blending'}")
    
    # Plot
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    ax = axes[0]
    ax.plot(blend_factors, curvatures, 'o-', color='#FF5722', markersize=4)
    ax.axhline(y=0, color='grey', linestyle='--', alpha=0.3)
    ax.set_xlabel('Blending factor')
    ax.set_ylabel('Total curvature (rad)')
    ax.set_title('Curvature vs Blend Factor\n(>0 everywhere = structural spiral)')
    ax.grid(True, alpha=0.3)
    
    ax = axes[1]
    ax.plot(blend_factors, total_rotations, 'o-', color='#4CAF50', markersize=4)
    ax.axhline(y=0, color='grey', linestyle='--', alpha=0.3)
    ax.set_xlabel('Blending factor')
    ax.set_ylabel('Total rotations (turns)')
    ax.set_title('Full Rotations vs Blend\n(same sign = consistent direction)')
    ax.grid(True, alpha=0.3)
    
    # Show example trees at different blendings
    ax = axes[2]
    for blend, color, label in [(0.05, '#2196F3', '5%'), (0.15, '#FF9800', '15%'), 
                                  (0.50, '#4CAF50', '50%'), (0.95, '#9C27B0', '95%')]:
        trunk_dir = -np.pi / 2
        cx, cy = 0, 0
        primes_list = []
        xs, ys = [0], [0]
        
        for n in range(2, max_n + 1):
            if not isprime(n):
                continue
            primes_list.append(n)
            if len(primes_list) > 1:
                prev = primes_list[-2]
                theta, rho = ras_radial_profile(prev, 360)
                peaks = find_peaks(theta, rho)
                if peaks:
                    best_peak = max(peaks, key=lambda p: p[1])
                    nudge = best_peak[0] + trunk_dir - np.pi / 2
                    diff = (nudge - trunk_dir) % (2 * np.pi)
                    if diff > np.pi: diff -= 2 * np.pi
                    trunk_dir += diff * blend
            cx += 1.0 * np.cos(trunk_dir)
            cy += 1.0 * np.sin(trunk_dir)
            xs.append(cx)
            ys.append(cy)
        
        ax.plot(xs, ys, '-', color=color, linewidth=1.5, label=f'blend={label}', alpha=0.8)
    
    ax.set_aspect('equal')
    ax.legend(fontsize=9)
    ax.set_title('Trunk Shape at Different Blendings\n(all spiral, rate varies)')
    ax.grid(True, alpha=0.2)
    ax.axis('off')
    
    fig.suptitle('TEST 1: Spiral Robustness — Does the trunk always spiral?', 
                fontsize=13, fontweight='bold')
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
        print(f"\n  Saved: {save_path}")
    plt.close()
    
    return always_curves, same_direction


# ═══════════════════════════════════════════════════════════════════════
# TEST 2: LOBE DEPTH SEPARATION
# ═══════════════════════════════════════════════════════════════════════

def test_lobe_separation(max_n=100, save_path=None):
    """
    Is the prime/composite lobe depth separation structural or an m-fold artifact?
    
    Test A: Use the natural m = omega(n)+1
    Test B: Force m=2 for ALL numbers (remove symmetry variation)
    Test C: Force m=1 for ALL numbers (no symmetry at all)
    Test D: Random m for each number
    
    If separation persists in B,C,D: it's from sopfr/bigomega, not m-fold.
    """
    print("\n" + "=" * 70)
    print("TEST 2: LOBE DEPTH SEPARATION")
    print("Is prime/composite lobe depth from factorisation or m-fold artifact?")
    print("=" * 70)
    
    np.random.seed(42)
    
    tests = {
        'A: Natural m=ω+1': None,      # Use natural m
        'B: Forced m=2': 2,
        'C: Forced m=1': 1,
        'D: Forced m=3': 3,
    }
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes_flat = axes.flatten()
    
    results = {}
    
    for idx, (test_name, m_val) in enumerate(tests.items()):
        ax = axes_flat[idx]
        
        prime_depths = []
        comp_depths = []
        prime_ns = []
        comp_ns = []
        
        for n in range(2, max_n + 1):
            m_use = m_val  # None means natural
            theta, rho = ras_radial_profile(n, 720, m_override=m_use)
            lobes = find_lobes(theta, rho, min_depth=0.001)
            
            avg_depth = np.mean([l[1] for l in lobes]) if lobes else 0
            
            if isprime(n):
                prime_depths.append(avg_depth)
                prime_ns.append(n)
            else:
                comp_depths.append(avg_depth)
                comp_ns.append(n)
        
        # Statistical separation
        p_mean = np.mean(prime_depths) if prime_depths else 0
        c_mean = np.mean(comp_depths) if comp_depths else 0
        
        # Mann-Whitney U test (non-parametric)
        from scipy.stats import mannwhitneyu
        if prime_depths and comp_depths:
            stat, pval = mannwhitneyu(prime_depths, comp_depths, alternative='less')
            separated = pval < 0.01
        else:
            pval = 1.0
            separated = False
        
        results[test_name] = {
            'prime_mean': p_mean, 'comp_mean': c_mean,
            'p_value': pval, 'separated': separated
        }
        
        print(f"\n  {test_name}:")
        print(f"    Prime mean depth: {p_mean:.5f}")
        print(f"    Composite mean:   {c_mean:.5f}")
        print(f"    Ratio (C/P):      {c_mean/p_mean:.2f}x" if p_mean > 0 else "    Ratio: N/A")
        print(f"    Mann-Whitney p:   {pval:.2e}")
        print(f"    Separated:        {'YES ✅' if separated else 'NO ❌'}")
        
        # Plot
        ax.scatter(prime_ns, prime_depths, c='#FF5722', s=20, alpha=0.7, label='Primes', zorder=3)
        ax.scatter(comp_ns, comp_depths, c='#4CAF50', s=15, alpha=0.5, label='Composites', zorder=2)
        ax.axhline(y=p_mean, color='#FF5722', linestyle='--', alpha=0.5)
        ax.axhline(y=c_mean, color='#4CAF50', linestyle='--', alpha=0.5)
        
        status = '✅' if separated else '❌'
        ax.set_title(f'{test_name}\nP̄={p_mean:.4f} C̄={c_mean:.4f} p={pval:.1e} {status}')
        ax.set_xlabel('n')
        ax.set_ylabel('Avg lobe depth')
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
    
    all_separated = all(r['separated'] for r in results.values())
    print(f"\n  ═══ VERDICT: {'STRUCTURAL ✅ — separation persists across ALL m-fold choices' if all_separated else 'MIXED — separation depends on m-fold (needs investigation)'} ═══")
    
    fig.suptitle('TEST 2: Lobe Depth Separation — Structural or Artifact?\n'
                 f'{"ALL tests show separation → STRUCTURAL" if all_separated else "Results mixed"}',
                fontsize=13, fontweight='bold')
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
        print(f"  Saved: {save_path}")
    plt.close()
    
    return all_separated


# ═══════════════════════════════════════════════════════════════════════
# TEST 3: GOLDEN ANGLE CONVERGENCE
# ═══════════════════════════════════════════════════════════════════════

def test_golden_angle(max_n=500, save_path=None):
    """
    Measure the angular spacing between successive composite branches
    in the self-evolving tree. Does it converge to the golden angle?
    
    Method: For each composite, compute its branch angle relative to 
    the previous composite's branch angle. Track the running average.
    Compare to golden angle (137.508°), uniform (random), and 90°/120°.
    """
    print("\n" + "=" * 70)
    print("TEST 3: GOLDEN ANGLE CONVERGENCE")
    print("Does branch spacing converge to 137.508°?")
    print("=" * 70)
    
    GOLDEN_ANGLE = np.degrees(np.pi * (3 - np.sqrt(5)))  # ≈ 137.508°
    
    primes_so_far = []
    
    # Track composite branch angles
    comp_angles = []  # absolute branch angles
    comp_spacings = []  # successive angular differences
    comp_ns = []
    
    trunk_dir = -np.pi / 2
    trunk_positions = {1: (0, 0)}
    cx, cy = 0, 0
    
    for n in range(2, max_n + 1):
        if isprime(n):
            primes_so_far.append(n)
            
            # Trunk nudge (use blend=0.15 as default)
            if len(primes_so_far) > 1:
                prev = primes_so_far[-2]
                theta, rho = ras_radial_profile(prev, 360)
                peaks = find_peaks(theta, rho)
                if peaks:
                    best_peak = max(peaks, key=lambda p: p[1])
                    nudge = best_peak[0] + trunk_dir - np.pi / 2
                    diff = (nudge - trunk_dir) % (2 * np.pi)
                    if diff > np.pi: diff -= 2 * np.pi
                    trunk_dir += diff * 0.15
            
            cx += 1.5 * np.cos(trunk_dir)
            cy += 1.5 * np.sin(trunk_dir)
            trunk_positions[n] = (cx, cy)
        else:
            if not primes_so_far:
                continue
            
            # Compute branch angle from parent prime's RAS lobes
            parent_prime = max(p for p in primes_so_far if p <= n)
            theta, rho = ras_radial_profile(parent_prime, 360)
            lobes = find_lobes(theta, rho, min_depth=0.005)
            
            if lobes:
                siblings = [i for i in range(parent_prime + 1, n + 1) if not isprime(i)]
                sib_idx = siblings.index(n) if n in siblings else 0
                lobe = lobes[sib_idx % len(lobes)]
                branch_angle = np.degrees(lobe[0] + trunk_dir + np.pi / 2) % 360
            else:
                factors = factorint(n)
                spf = min(factors.keys())
                branch_angle = np.degrees(trunk_dir + np.pi / 2 * (1 if spf % 3 == 0 else -1)) % 360
            
            comp_angles.append(branch_angle)
            comp_ns.append(n)
            
            if len(comp_angles) > 1:
                spacing = (comp_angles[-1] - comp_angles[-2]) % 360
                if spacing > 180:
                    spacing = 360 - spacing
                comp_spacings.append(spacing)
    
    # Running average of spacings
    if comp_spacings:
        running_avg = np.cumsum(comp_spacings) / np.arange(1, len(comp_spacings) + 1)
        final_avg = running_avg[-1]
        
        # Also compute in windows
        window = 20
        windowed_avg = []
        windowed_x = []
        for i in range(window, len(comp_spacings)):
            windowed_avg.append(np.mean(comp_spacings[i-window:i]))
            windowed_x.append(comp_ns[i])
    else:
        running_avg = []
        final_avg = 0
        windowed_avg = []
        windowed_x = []
    
    print(f"\n  Composites analysed: {len(comp_spacings)}")
    print(f"  Mean spacing:       {final_avg:.2f}°")
    print(f"  Golden angle:       {GOLDEN_ANGLE:.2f}°")
    print(f"  Difference:         {abs(final_avg - GOLDEN_ANGLE):.2f}°")
    print(f"  Std dev:            {np.std(comp_spacings):.2f}°")
    
    # Compare to reference values
    refs = {
        'Golden angle': GOLDEN_ANGLE,
        '120° (3-fold)': 120,
        '90° (4-fold)': 90,
        '72° (5-fold)': 72,
        '60° (6-fold)': 60,
        '45° (8-fold)': 45,
    }
    
    print(f"\n  Distance to reference angles:")
    for name, ref in refs.items():
        dist = abs(final_avg - ref)
        marker = " ← CLOSEST" if dist == min(abs(final_avg - r) for r in refs.values()) else ""
        print(f"    {name:>20}: {dist:.2f}°{marker}")
    
    closest_ref = min(refs.items(), key=lambda x: abs(final_avg - x[1]))
    print(f"\n  Closest match: {closest_ref[0]} ({closest_ref[1]:.1f}°)")
    
    # Is it converging or stable?
    if len(running_avg) > 50:
        early = np.mean(comp_spacings[:25])
        late = np.mean(comp_spacings[-25:])
        trend = late - early
        print(f"\n  Early avg (first 25):  {early:.2f}°")
        print(f"  Late avg (last 25):    {late:.2f}°")
        print(f"  Trend:                 {'converging ↓' if trend < -1 else 'diverging ↑' if trend > 1 else 'stable ≈'} ({trend:+.2f}°)")
    
    # Plot
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Spacing distribution
    ax = axes[0][0]
    ax.hist(comp_spacings, bins=36, range=(0, 180), color='#90CAF9', 
            edgecolor='#1565C0', alpha=0.7)
    ax.axvline(x=GOLDEN_ANGLE, color='#4CAF50', linewidth=2, linestyle='--',
              label=f'Golden ({GOLDEN_ANGLE:.1f}°)')
    ax.axvline(x=final_avg, color='#FF5722', linewidth=2, linestyle='-',
              label=f'Mean ({final_avg:.1f}°)')
    ax.set_xlabel('Angular spacing (°)')
    ax.set_ylabel('Count')
    ax.set_title('Distribution of Branch Spacings')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    
    # Running average
    ax = axes[0][1]
    if running_avg is not None and len(running_avg) > 0:
        ax.plot(comp_ns[1:len(running_avg)+1], running_avg, '-', color='#FF5722', linewidth=1.5, label='Running avg')
    if windowed_avg:
        ax.plot(windowed_x, windowed_avg, '-', color='#2196F3', linewidth=1.5, alpha=0.7, label=f'Window avg ({window})')
    ax.axhline(y=GOLDEN_ANGLE, color='#4CAF50', linewidth=2, linestyle='--', label=f'Golden ({GOLDEN_ANGLE:.1f}°)')
    ax.axhline(y=90, color='#9C27B0', linewidth=1, linestyle=':', alpha=0.5, label='90°')
    ax.axhline(y=120, color='#FF9800', linewidth=1, linestyle=':', alpha=0.5, label='120°')
    ax.set_xlabel('n')
    ax.set_ylabel('Avg spacing (°)')
    ax.set_title('Convergence of Branch Spacing')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    
    # Polar scatter of branch angles
    ax = axes[1][0]
    ax_polar = fig.add_axes(ax.get_position(), polar=True)
    ax.remove()
    angles_rad = np.radians(comp_angles[:200])  # first 200
    ax_polar.scatter(angles_rad, range(len(angles_rad)), c=range(len(angles_rad)),
                    cmap='viridis', s=10, alpha=0.6)
    ax_polar.set_title('Branch Angles (polar)\nColour = sequence order', pad=15)
    
    # Spacing vs n
    ax = axes[1][1]
    ax.scatter(comp_ns[1:len(comp_spacings)+1], comp_spacings, s=8, c='#90CAF9', 
              alpha=0.5, zorder=2)
    ax.axhline(y=GOLDEN_ANGLE, color='#4CAF50', linewidth=2, linestyle='--', alpha=0.7)
    ax.axhline(y=final_avg, color='#FF5722', linewidth=1.5, alpha=0.7)
    ax.set_xlabel('n')
    ax.set_ylabel('Spacing to previous (°)')
    ax.set_title('Individual Branch Spacings')
    ax.grid(True, alpha=0.3)
    
    fig.suptitle(f'TEST 3: Golden Angle Convergence\n'
                 f'Mean spacing = {final_avg:.1f}° | Golden = {GOLDEN_ANGLE:.1f}° | '
                 f'Closest: {closest_ref[0]}',
                fontsize=13, fontweight='bold')
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
        print(f"\n  Saved: {save_path}")
    plt.close()
    
    return final_avg, GOLDEN_ANGLE


# ═══════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║   PRIME TREE — ROBUSTNESS TESTS                                ║")
    print("║   GND before write-up. Day 9 (3²)                              ║")
    print("╚══════════════════════════════════════════════════════════════════╝\n")
    
    # Test 1
    spiral_robust, spiral_direction = test_spiral_robustness(
        100, save_path=f'{OUT_DIR}/test1_spiral_robustness.png')
    
    # Test 2
    lobe_structural = test_lobe_separation(
        100, save_path=f'{OUT_DIR}/test2_lobe_separation.png')
    
    # Test 3
    mean_spacing, golden = test_golden_angle(
        500, save_path=f'{OUT_DIR}/test3_golden_angle.png')
    
    # Summary
    print("\n" + "═" * 70)
    print("SUMMARY")
    print("═" * 70)
    print(f"\n  TEST 1 — Spiral:      {'PASS ✅' if spiral_robust else 'FAIL ❌'} "
          f"(always curves: {spiral_robust}, same direction: {spiral_direction})")
    print(f"  TEST 2 — Lobe depth:  {'PASS ✅' if lobe_structural else 'FAIL ❌'} "
          f"(structural separation)")
    print(f"  TEST 3 — Golden:      Mean={mean_spacing:.1f}° vs Golden={golden:.1f}° "
          f"(Δ={abs(mean_spacing-golden):.1f}°)")
    
    ready = spiral_robust and lobe_structural
    print(f"\n  {'🌿 READY TO WRITE UP' if ready else '⚠️  NEEDS MORE INVESTIGATION'}")
    print()
