# Changelog

## Unreleased

- Project renamed to **NotchBuddy**, character renamed to **Buddy**. New bundle identifier `codes.arvind.NotchBuddy` (App Store build: `codes.arvind.NotchBuddyAppStore`), new Keychain service, hook files now in `~/.claude/notchbuddy/`, hook payload field renamed to `notchbuddy_agent`, Windows pipe renamed to `\\.\pipe\notchbuddy-<sid>`.
- New app icon, menu bar icon and 28 sounds, all generated in code (`scripts/gen-icons.py`, `scripts/gen-sounds.py`). New lavender body palette for Buddy.
- Based on Coucou 0.1.1 by Louis Raillé (MIT). Everything Coucou had at that point is carried over: compact island on notch-less screens, hook socket hardening, chat model picker, Windows build, third-party agent pills.
