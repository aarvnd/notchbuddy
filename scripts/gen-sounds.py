#!/usr/bin/env python3
"""Synthesizes the 28 NotchBuddy UI sounds from scratch (Python stdlib only).

    python3 scripts/gen-sounds.py

Output: NotchBuddy/Resources/sounds/<name>.wav — stereo, 16-bit, 48 kHz, the
format SoundEngine.swift and the Windows build expect. Every sound is a small
additive/FM "toy" tone with its own envelope, so the set has one voice: soft
sine-based bodies, a touch of harmonics, short tails, no samples.
"""
import math, os, random, struct, wave

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "NotchBuddy/Resources/sounds")
SR = 48000
random.seed(7)


# ── Building blocks ──────────────────────────────────────────────────────────

def env(t, dur, a=0.005, d=0.08, s=0.6, r=0.12):
    """ADSR in seconds; release starts at dur - r."""
    if t < a:
        return t / a
    if t < a + d:
        return 1 - (1 - s) * (t - a) / d
    if t > dur - r:
        return max(0.0, s * (dur - t) / r)
    return s


def tone(dur, f0, f1=None, wave_mix=(1.0, 0.25, 0.08), vib=0.0, vib_hz=6.0,
         a=0.005, d=0.08, s=0.6, r=0.12, gain=0.5, pan=0.0, noise=0.0, bend="lin"):
    """One note sliding from f0 to f1. wave_mix = (fund, 2nd, 3rd) harmonics."""
    n = int(dur * SR)
    f1 = f0 if f1 is None else f1
    out = []
    phase = 0.0
    for i in range(n):
        t = i / SR
        u = t / dur
        if bend == "exp":
            f = f0 * (f1 / f0) ** u
        else:
            f = f0 + (f1 - f0) * u
        f *= 1 + vib * math.sin(2 * math.pi * vib_hz * t)
        phase += 2 * math.pi * f / SR
        v = (wave_mix[0] * math.sin(phase)
             + wave_mix[1] * math.sin(2 * phase)
             + wave_mix[2] * math.sin(3 * phase))
        if noise:
            v += noise * (random.random() * 2 - 1)
        v *= env(t, dur, a, d, s, r) * gain
        out.append((v * (1 - max(0, pan)), v * (1 + min(0, pan))))
    return out


def silence(dur):
    return [(0.0, 0.0)] * int(dur * SR)


def mix(*layers):
    n = max(len(l) for l in layers)
    out = [(0.0, 0.0)] * n
    for l in layers:
        for i, (L, R) in enumerate(l):
            a, b = out[i]
            out[i] = (a + L, b + R)
    return out


def seq(*parts):
    out = []
    for p in parts:
        out.extend(p)
    return out


def offset(samples, start):
    return silence(start) + samples


def soft_clip(v):
    return math.tanh(v * 1.2) / math.tanh(1.2)


def write(name, samples):
    path = os.path.join(OUT, f"{name}.wav")
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        frames = bytearray()
        for L, R in samples:
            frames += struct.pack("<hh", int(soft_clip(L) * 32000), int(soft_clip(R) * 32000))
        w.writeframes(bytes(frames))
    print(f"{name:10s} {len(samples) / SR:5.2f}s")


# ── The 28 sounds ────────────────────────────────────────────────────────────

def build():
    S = {}

    # tiny UI ticks
    S["tick"] = tone(0.07, 1900, 1700, a=0.001, d=0.03, s=0.2, r=0.03, gain=0.35)
    S["hover"] = tone(0.08, 1300, 1500, a=0.002, d=0.04, s=0.3, r=0.03, gain=0.3)
    S["blip"] = tone(0.10, 880, 1320, a=0.002, d=0.05, s=0.4, r=0.04, gain=0.45, bend="exp")

    # open / close: two-note slides, mirrored
    S["open"] = seq(tone(0.22, 523, 659, a=0.004, d=0.1, s=0.5, r=0.08, gain=0.45),
                    tone(0.28, 784, 1047, a=0.004, d=0.12, s=0.5, r=0.14, gain=0.4))
    S["close"] = seq(tone(0.20, 784, 659, a=0.004, d=0.1, s=0.5, r=0.08, gain=0.4),
                     tone(0.23, 523, 392, a=0.004, d=0.1, s=0.4, r=0.12, gain=0.35))

    # peek + greet: a little "boing" then a bright hello
    S["peek"] = tone(0.45, 330, 660, vib=0.03, vib_hz=12, a=0.01, d=0.15, s=0.5, r=0.2, gain=0.45, bend="exp")
    S["greet"] = mix(seq(tone(0.18, 659, a=0.005, d=0.08, s=0.6, r=0.06, gain=0.4, pan=-0.3),
                         tone(0.18, 880, a=0.005, d=0.08, s=0.6, r=0.06, gain=0.4, pan=0.3),
                         tone(0.39, 1047, 1175, vib=0.02, a=0.005, d=0.1, s=0.6, r=0.25, gain=0.45)),
                     offset(tone(0.3, 262, a=0.01, d=0.2, s=0.3, r=0.1, gain=0.2), 0.36))

    # states
    S["work"] = seq(tone(0.12, 440, a=0.003, d=0.06, s=0.5, r=0.04, gain=0.35),
                    tone(0.12, 554, a=0.003, d=0.06, s=0.5, r=0.04, gain=0.35),
                    tone(0.14, 659, a=0.003, d=0.06, s=0.5, r=0.08, gain=0.35))
    S["think"] = tone(0.44, 392, 494, vib=0.015, vib_hz=5, wave_mix=(1, 0.1, 0.0), a=0.05, d=0.15, s=0.6, r=0.2, gain=0.4)
    S["search"] = mix(tone(0.46, 700, 1400, wave_mix=(1, 0.05, 0.0), a=0.01, d=0.2, s=0.4, r=0.2, gain=0.3, bend="exp"),
                      tone(0.46, 1400, 700, wave_mix=(1, 0.05, 0.0), a=0.01, d=0.2, s=0.4, r=0.2, gain=0.3, bend="exp"))
    S["question"] = seq(tone(0.25, 587, 659, a=0.005, d=0.1, s=0.6, r=0.08, gain=0.4),
                        tone(0.45, 784, 988, vib=0.02, a=0.005, d=0.12, s=0.6, r=0.25, gain=0.42, bend="exp"))
    S["approval"] = mix(seq(tone(0.2, 740, a=0.004, d=0.1, s=0.6, r=0.06, gain=0.42),
                            tone(0.2, 740, a=0.004, d=0.1, s=0.6, r=0.06, gain=0.42),
                            tone(0.48, 988, 1109, vib=0.02, a=0.004, d=0.15, s=0.6, r=0.3, gain=0.42)),
                        offset(tone(0.4, 370, a=0.01, d=0.2, s=0.3, r=0.15, gain=0.18), 0.4))
    S["error"] = mix(tone(0.84, 220, 165, wave_mix=(1, 0.5, 0.3), vib=0.04, vib_hz=9, a=0.01, d=0.3, s=0.5, r=0.35, gain=0.4),
                     tone(0.5, 330, 247, wave_mix=(1, 0.4, 0.2), a=0.01, d=0.2, s=0.4, r=0.2, gain=0.25))
    S["finish"] = mix(seq(tone(0.16, 523, a=0.004, d=0.08, s=0.6, r=0.05, gain=0.4),
                          tone(0.16, 659, a=0.004, d=0.08, s=0.6, r=0.05, gain=0.4),
                          tone(0.16, 784, a=0.004, d=0.08, s=0.6, r=0.05, gain=0.4),
                          tone(0.68, 1047, 1047, vib=0.015, vib_hz=5, a=0.004, d=0.2, s=0.6, r=0.4, gain=0.45)),
                      offset(tone(0.7, 262, a=0.02, d=0.3, s=0.3, r=0.3, gain=0.2), 0.46))
    S["rate"] = seq(tone(0.3, 494, 440, wave_mix=(1, 0.3, 0.1), a=0.01, d=0.15, s=0.5, r=0.1, gain=0.38),
                    tone(0.37, 415, 349, wave_mix=(1, 0.3, 0.1), a=0.01, d=0.15, s=0.4, r=0.2, gain=0.35))
    S["sleep"] = tone(0.45, 523, 262, wave_mix=(1, 0.08, 0.0), a=0.05, d=0.2, s=0.5, r=0.2, gain=0.3, bend="exp")

    # emotes
    S["approve"] = seq(tone(0.25, 659, a=0.004, d=0.1, s=0.6, r=0.06, gain=0.42),
                       tone(0.35, 988, 1047, a=0.004, d=0.1, s=0.6, r=0.2, gain=0.42))
    S["annoyed"] = tone(0.59, 300, 180, wave_mix=(1, 0.6, 0.35), vib=0.06, vib_hz=14, a=0.005, d=0.2, s=0.5, r=0.25, gain=0.4)
    S["dizzy"] = tone(0.98, 600, 300, wave_mix=(1, 0.2, 0.05), vib=0.12, vib_hz=7, a=0.01, d=0.3, s=0.6, r=0.4, gain=0.38, bend="exp")
    S["love"] = mix(seq(tone(0.26, 784, a=0.004, d=0.1, s=0.6, r=0.08, gain=0.38, pan=-0.4),
                        tone(0.53, 1175, 1319, vib=0.03, vib_hz=5, a=0.004, d=0.15, s=0.6, r=0.3, gain=0.4, pan=0.4)),
                    offset(tone(0.45, 392, a=0.02, d=0.2, s=0.3, r=0.2, gain=0.18), 0.3))
    S["proud"] = seq(tone(0.2, 587, a=0.004, d=0.1, s=0.6, r=0.05, gain=0.4),
                     tone(0.2, 880, a=0.004, d=0.1, s=0.6, r=0.05, gain=0.4),
                     tone(0.46, 1175, 1175, vib=0.02, vib_hz=5, a=0.004, d=0.15, s=0.6, r=0.3, gain=0.42))
    S["wink"] = tone(0.21, 1047, 1568, a=0.002, d=0.08, s=0.4, r=0.08, gain=0.4, bend="exp")
    S["yawn"] = tone(0.73, 440, 220, wave_mix=(1, 0.15, 0.0), vib=0.02, vib_hz=4, a=0.15, d=0.2, s=0.6, r=0.3, gain=0.35, bend="exp")
    S["slap"] = mix(tone(0.12, 180, 60, wave_mix=(1, 0.5, 0.3), a=0.001, d=0.05, s=0.3, r=0.05, gain=0.6, bend="exp"),
                    tone(0.6, 0.0001, 0.0001, noise=0.5, a=0.001, d=0.08, s=0.05, r=0.4, gain=0.3))
    S["pop"] = tone(0.38, 300, 900, wave_mix=(1, 0.3, 0.1), a=0.001, d=0.08, s=0.3, r=0.25, gain=0.45, bend="exp")

    # file drop / chat
    S["attach"] = seq(tone(0.3, 392, 523, a=0.01, d=0.1, s=0.6, r=0.1, gain=0.4),
                      tone(0.6, 659, 784, vib=0.015, a=0.005, d=0.15, s=0.6, r=0.35, gain=0.4))
    S["gulp"] = tone(0.75, 500, 120, wave_mix=(1, 0.4, 0.15), a=0.01, d=0.3, s=0.5, r=0.3, gain=0.45, bend="exp")
    S["send"] = tone(0.48, 500, 1500, wave_mix=(1, 0.15, 0.0), a=0.005, d=0.15, s=0.5, r=0.25, gain=0.4, bend="exp")

    return S


def main():
    os.makedirs(OUT, exist_ok=True)
    sounds = build()
    assert len(sounds) == 28, len(sounds)
    for name in sorted(sounds):
        write(name, sounds[name])


if __name__ == "__main__":
    main()
