# Comfort-zone boundary explorer -- static site, no backend.
#
#   docker build -t czb-explorer tools/czb_explorer
#   docker run --rm -p 8080:80 czb-explorer
#   -> http://localhost:8080
#
# The page is fully client-side; nginx only serves files, so this image
# deploys anywhere a container runs (or the folder can be dropped onto any
# static host as-is).

FROM nginx:alpine

COPY index.html czb_math.js reference.js /usr/share/nginx/html/

# Container hygiene: unprivileged nginx would need extra config; the default
# alpine image is acceptable for an internal tool. Health check for
# orchestrators:
HEALTHCHECK --interval=30s --timeout=3s \
  CMD wget -q -O /dev/null http://localhost/ || exit 1
