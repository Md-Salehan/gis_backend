import json
import tempfile
from pathlib import Path

from django.http import FileResponse
from django.test import Client
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from playwright.sync_api import sync_playwright


PRINT_HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<title>Map Print</title>

<link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css"/>

<style>
  @page { size: A4 landscape; margin: 0; }
  html, body { margin: 0; padding: 0; }
  #map { width: 3508px; height: 2480px; }
</style>
</head>

<body>
<div id="map"></div>

<script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>

<script>
async function renderMap(payload) {
  try {
    const map = L.map("map", {
      zoomControl: false,
      attributionControl: false,
      preferCanvas: false
    });

    const tileLayer = L.tileLayer(payload.baseMap.url, {
      tileSize: 512,
      zoomOffset: -1,
      detectRetina: true
    }).addTo(map);

    map.setView(payload.viewport.center, payload.viewport.zoom);

    // track readiness: tiles + geojson layers
    let tilesLoaded = false;
    tileLayer.on('load', () => { tilesLoaded = true; });

    let pending = 0;

    for (const layer of payload.layers) {
      try {
        let geojson = null;

        // If server preloaded the geojson, use that directly
        if (layer.geojson) {
          geojson = layer.geojson;
        } else if (layer.geojsonUrl) {
          const res = await fetch(layer.geojsonUrl);
          if (!res.ok) throw new Error('Failed GeoJSON');
          geojson = await res.json();
        }

        if (!geojson) continue;

        pending++;

        L.geoJSON(geojson, {
          renderer: L.svg(),
          style: layer.style,
          pointToLayer: (f, latlng) =>
            L.circleMarker(latlng, {
              radius: layer.style.marker_size || 6,
              color: layer.style.stroke_color || "#000",
              fillColor: layer.style.fill_color || "#3388ff",
              fillOpacity: layer.style.fill_opacity ?? 0.9,
              weight: layer.style.stroke_width || 2
            })
        }).addTo(map).once('add', () => {
          pending = Math.max(0, pending - 1);
        });
      } catch (e) {
        console.error('Layer error:', e);
      }
    }

    // Wait until tilesLoaded and pending==0, or a fallback timeout
    const start = Date.now();
    const maxWait = 10000; // ms

    function checkReady() {
      if ((tilesLoaded || (Date.now() - start) > maxWait) && pending === 0) {
        window.__MAP_READY__ = true;
      } else {
        setTimeout(checkReady, 200);
      }
    }

    checkReady();

  } catch (e) {
    console.error("Render error:", e);
    window.__MAP_READY__ = "ERROR";
  }
}
</script>

</body>
</html>
"""


class PrintMapView(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request):
        payload = request.data
        # Prefetch GeoJSON for any layers that provide a relative `geojsonUrl`.
        # Use Django's test Client to avoid making blocking external HTTP calls
        # to the same server process.
        try:
            client = Client()
            for layer in payload.get("layers", []):
                geourl = layer.get("geojsonUrl")
                if geourl and geourl.startswith("/"):
                    try:
                        resp = client.get(geourl)
                        if resp.status_code == 200:
                            # store under `geojson` so the page can use it directly
                            try:
                                layer["geojson"] = resp.json()
                            except Exception:
                                layer["geojson"] = None
                        else:
                            layer["geojson"] = None
                    except Exception:
                        layer["geojson"] = None
        except Exception:
            # If anything goes wrong, continue without prefetching.
            pass

        # Use a persistent temp dir on Windows to avoid deletion clashes
        tmp_dir = tempfile.mkdtemp()
        tmp = Path(tmp_dir)
        html_path = tmp / "print.html"
        pdf_path = tmp / "map.pdf"

        try:
          html_path.write_text(PRINT_HTML, encoding="utf-8")

          with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto(f"file:///{html_path.as_posix()}", wait_until="load")

            # 🔑 Inject payload directly (NO fetch from file://)
            page.evaluate("payload => renderMap(payload)", payload)

            # ✅ Wait for explicit signal
            page.wait_for_function(
              "window.__MAP_READY__ === true",
              timeout=60000
            )

            page.pdf(
              path=str(pdf_path),
              format="A4",
              landscape=True,
              print_background=True,
              prefer_css_page_size=True
            )

            browser.close()

          if not pdf_path.exists() or pdf_path.stat().st_size < 1000:
            raise RuntimeError("PDF generation failed")

          # Return file response. Do NOT delete temp dir immediately on Windows
          # because the file handle may be open while the server streams it.
          return FileResponse(
            open(pdf_path, "rb"),
            content_type="application/pdf",
            filename="map.pdf"
          )
        except Exception:
          # Cleanup on error
          try:
            if pdf_path.exists():
              pdf_path.unlink()
            if html_path.exists():
              html_path.unlink()
            Path(tmp_dir).rmdir()
          except Exception:
            pass
          raise
