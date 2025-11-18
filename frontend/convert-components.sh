#!/bin/bash

TEMPLATE_DIR="../ui-clone-task-approval/src/components/ui"
TARGET_DIR="./src/components/ui"

# List of components to copy
components=(
  "separator"
  "avatar"
  "dropdown-menu"
  "tooltip"
  "sheet"
  "sidebar"
  "dialog"
  "scroll-area"
  "collapsible"
  "skeleton"
)

for comp in "${components[@]}"; do
  if [ -f "$TEMPLATE_DIR/$comp.tsx" ]; then
    echo "Converting $comp.tsx to $comp.jsx..."
    # Copy and convert tsx to jsx, remove type annotations
    sed -E '
      s/\.tsx/.jsx/g
      s/<([A-Z][a-zA-Z0-9]*)<([^>]+)>>/g
      s/: React\.[A-Za-z<>|&, ()]+//g
      s/: boolean//g
      s/: string//g
      s/: number//g
      s/React\.ComponentProps/React.ComponentPropsWithoutRef/g
      s/VariantProps<typeof [^>]+>//g
      s/<boolean \| undefined>//g
      s/ \& VariantProps<[^>]+>//g
    ' "$TEMPLATE_DIR/$comp.tsx" > "$TARGET_DIR/$comp.jsx"
  fi
done

echo "Done!"
