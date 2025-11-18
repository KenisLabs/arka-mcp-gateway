#!/bin/bash

# Fix sidebar.jsx - remove type declarations and type annotations
perl -i -pe '
  s/^type\s+\w+\s*=\s*\{[^}]*$//;
  s/^\s*\w+:?\s*"[^"]*"\s*\|?\s*"[^"]*"\s*$//;
  s/^\s*\w+:?\s*(boolean|string|number)\s*$//;
  s/^\s*\w+:?\s*\([^)]*\)\s*=>\s*\w+\s*$//;
  s/^\}$// if ($. >= 35 && $. <= 43);
  s/<SidebarContextProps \| null>//' src/components/ui/sidebar.jsx

# Fix remaining TypeScript annotations in function parameters
perl -i -0777 -pe 's/\{([^}]*)\}:\s*React\.ComponentProps<[^>]*>/\{$1\}/gs' src/components/ui/*.jsx
perl -i -0777 -pe 's/\n\}:\s*React\.ComponentProps<[^>]*>/\n/gs' src/components/ui/*.jsx
perl -i -0777 -pe 's/\}\{\s*\w+\?[\s\S]*?\}\)/\}\)/gs' src/components/ui/*.jsx
perl -i -0777 -pe 's/const\s+(\w+)\s*=\s*React\.createContext<[^>]*>/const $1 = React.createContext/gs' src/components/ui/*.jsx
perl -i -0777 -pe 's/React\.JSX\.Element/any/g' src/components/ui/*.jsx
perl -i -0777 -pe 's/React\.ElementRef<[^>]*>/any/g' src/components/ui/*.jsx
perl -i -0777 -pe 's/React\.ComponentPropsWithoutRef<[^>]*>/any/g' src/components/ui/*.jsx
perl -i -0777 -pe 's/ & VariantProps<[^>]*>//g' src/components/ui/*.jsx

echo "Fixed TypeScript syntax errors"
