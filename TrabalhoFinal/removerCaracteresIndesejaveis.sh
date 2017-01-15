#!/bin/bash
echo "substituindo * por ' '"
$(find $1 -type f -exec sed -i "s/*/ /g" {} \;)
echo "substituindo -- por ' '"
$(find $1 -type f -exec sed -i "s/--/ /g" {} \;)
