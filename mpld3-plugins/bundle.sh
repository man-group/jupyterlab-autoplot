#!/bin/bash
set -e

if [[ $1 == "test" ]]
then
    DIR=bundles_test
else
    DIR=bundles
fi

rm -rf $DIR || true
mkdir -p $DIR

# loop through plugins
for name in interactiveLegend rangeSelectorButtons saveImageButtons timeSeriesTooltip
do
    echo "Bundling $name.js"

    # copy main.js file (unless testing) without header (i.e. the 'use strict')
    if [[ $1 != "test" ]]
    then
        tail -n +2 build/$name/main.js > $DIR/$name.js
    else
        touch $DIR/$name.js
    fi

    # append other files without header (i.e. the 'use strict')
    for aux in build/$name/*.js
    do  
        if [[ $aux != *"main.js" ]]
        then
            tail -n +2 $aux >> $DIR/$name.js
        fi
    done
done