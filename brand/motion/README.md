# VIABLE motion library

Five distinct 10-second loops, each travelling VIABLE → VBL → VIABLE. V bridge also passes through the standalone V. 01 Signature reproduces the current website choreography. All letters use the exact approved Soft paths; no extra V is attached to VIABLE.

- SVG / white SVG: lightweight vector web masters, transparent background, reduced-motion fallback.
- MP4: 960×300, 15 fps, white background, one complete loop. Set loop in the player if needed.
- GIF: 640×200, white background, looping preview. GIF is not the preferred web format and cannot obey reduced-motion settings on its own.
- index.html: gallery with pause/replay and offscreen/hidden-tab pausing. Open via a local HTTP server or the hosted gallery.
- ../icons: standalone V, VBL and VIABLE, blue/white SVG and transparent PNG.
- source/build.py: reproducible generator; requires rsvg-convert, Pillow, imageio-ffmpeg.

Use only one moving logo on a customer page. Keep the existing homepage animation unless a replacement is deliberately selected. VIABLE is the full company name; VBL is the short form. V is a separate icon for favicons, avatars, app icons and limited-space placements.

SVG uses browser ease-in-out interpolation; raster previews approximate easing with smoothstep. Artwork, states and timing are the same. Reduced motion leaves a static VIABLE wordmark. Static PNG/SVG alternatives are included.
