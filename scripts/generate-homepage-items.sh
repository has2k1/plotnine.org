#!/usr/bin/env bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOMEPAGE_DIR="${SCRIPT_DIR}/../source/homepage"

# Compile Tailwind CSS
npx @tailwindcss/cli -i "${HOMEPAGE_DIR}/input.css" -o "${HOMEPAGE_DIR}/homepage.min.css" --minify

# Render banner
uv run jinja2 "${HOMEPAGE_DIR}/banner/template.jinja" "${HOMEPAGE_DIR}/banner/items.yaml" > "${HOMEPAGE_DIR}/banner/output.html"

# Render features
uv run jinja2 "${HOMEPAGE_DIR}/features/template.jinja" "${HOMEPAGE_DIR}/features/items.yaml" > "${HOMEPAGE_DIR}/features/output.html"

# Process Python code chunks for features
for python_file in "${HOMEPAGE_DIR}"/features/code/*.py; do
  echo Processing "${python_file}...";
  html_file="${HOMEPAGE_DIR}/features/html/$(basename "${python_file}").html"

  # cat "${python_file}" | \
  # sed 's/#skip//g' | \
  sed 's/#skip//g' < "${python_file}" | \
  uv run pygmentize -f html -l python | \
  sed 's|"err">!!!</span>|"tw:opacity-50">|g;s|<span class="err">???||g;' | \
  sed -re 's^(ggplot|aes|geom_smooth|geom_point|facet_wrap|scale_y_continuous|coord_fixed|labs|theme_tufte|theme)^<a style="color: inherit; text-underline-offset: 0.3em;" href="/reference/\1.html">\1</a>^g' > "$html_file"
done

# Create thumbnails
for img in "${HOMEPAGE_DIR}"/banner/img/highlights/*.png; do
  filename="${HOMEPAGE_DIR}/banner/img/thumbnails/$(basename "${img}")"
  echo Processing "${filename}...";
  magick "${img}" -resize '228x140^>' -strip "${filename}"
done

# Render plot images for the features
for python_file in "${HOMEPAGE_DIR}"/features/code/*.py; do
  id=$(basename "${python_file::-3}")
  "$SCRIPT_DIR/create-feature-img.sh" "${id}"
done
