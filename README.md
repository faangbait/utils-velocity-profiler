# velocity-profiler

Linux port of Digi-Sense 20250-16 Anemometer

Reads Anemometer data
Runs motors to move anemometer further down a track (away from wind source)
Stops motors and takes readings when checkpoint is reached (flips physical roller switch)
Reverses motors when end-of-track reached (flips physical toggle switch)

Wiring is pretty simple. Requires RC debounce circuit on both switches; software also debounces to some degree, but both are better.

Gears and wheels were 3D printed.
