
# uses https://github.com/norwoodj/helm-docs for automatically generating the README.md.

docker run --rm --volume "$(pwd):/helm-docs" -u $(id -u) jnorwood/helm-docs:v1.14.2 --chart-to-generate . -t ./README.md.gotmpl -t ./_templates.gotmpl  --chart-search-root=.