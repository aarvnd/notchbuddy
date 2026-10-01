# NotchBuddy — guide for AI coding agents

NotchBuddy is a native macOS app: Buddy, a small animated character living in the MacBook notch, shows Claude Code sessions and a few integrations, and lets the user approve, answer, chat and drop files from the notch.

## Where things are
- `NotchBuddy/Sources/App/` — all Swift code. `NotchBuddy/Resources/sounds/` — the 28 WAV sounds. `NotchBuddy/project.yml` — XcodeGen project (never edit the `.xcodeproj` by hand).
- `docs/SPEC.md`, `docs/INTEGRATIONS.md` — behaviour, views, states, integrations (in French).
- `design/prototype/notch-buddy.html` — original prototype of the island and the character, the visual source of truth for layout and timings.
- `docs/*.html` — the GitHub Pages site (privacy, terms, support, legal notice).

## Build
```
cd NotchBuddy && xcodegen && xcodebuild -scheme NotchBuddy -configuration Debug build
```

## Rules
- Swift 6, SwiftUI + AppKit. No third-party dependencies unless truly unavoidable. The character is drawn in code (`Canvas` + `TimelineView`), no Rive/Lottie/images.
- Secrets live in the Keychain, never on disk or in git.
- No telemetry. Network calls only to services the user configured.
- Never block Claude Code: if the app doesn't answer, the hook exits immediately.
- Never overwrite `~/.claude/settings.json`: dated backup, merge, show the diff, write only after the user confirms.
- Never send an email or approve a Claude Code permission without an explicit click.
- Performance: 0 % CPU when the island is hidden.
- Keep the bundle identifier `codes.arvind.NotchBuddy` (Keychain items, preferences and permissions depend on it).
- Visual changes must keep the prototype's layout and timings. Character colors come from `BuddyConst` (Swift) and `engine.ts` (Windows); keep both in sync.
- Icon and sounds are generated: `python3 scripts/gen-icons.py`, `python3 scripts/gen-sounds.py`. Edit the scripts, not the files.
- This project started as a fork of Coucou by Louis Raillé (MIT). Keep the original copyright line in `LICENSE`; never reintroduce the Coucou/Mochi names, icon, sounds or media (they are not MIT-licensed).
