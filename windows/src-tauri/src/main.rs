// NotchBuddy runs without a console window: Buddy is the whole UI.
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

fn main() {
    notchbuddy_lib::run()
}
