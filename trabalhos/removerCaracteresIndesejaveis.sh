#!/bin/bash


echo "substituindo apóstrofe diferente por apóstrofe comum"
$(find $1 -type f -exec sed -i "s/’/'/g" {} \;)
echo "substituindo '–' por espaço"
$(find $1 -type f -exec sed -i 's/–/ /g' {} \;)
echo "substituindo '—' por espaço(não é o mesmo)"
$(find $1 -type f -exec sed -i 's/—/ /g' {} \;)
echo "substituindo aspas especiais por espaço"
$(find $1 -type f -exec sed -i 's/”/ /g' {} \;)
echo "substituindo bolinha por espaço"
$(find $1 -type f -exec sed -i 's/•/ /g' {} \;)
echo "substituindo 'ː' estranho por ':'"
$(find $1 -type f -exec sed -i 's/ː/ /g' {} \;)
echo "substituindo '“' estranho por aspas"
$(find $1 -type f -exec sed -i 's/“/ /g' {} \;)
