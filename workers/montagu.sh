#!/bin/bash

export PACKAGEBUILDER_RSAKEY="/Users/dtenenba/dev/packagebuilder/.packagebuilder.private_key.rsa"


cd /Users/dtenenba/dev/packagebuilder/workers
pushd /Users/dtenenba/BBS/$2/bioc/montagu

. config.sh

popd


export BBS_USER="pkgbuild"
export SVN_USER="pkgbuild"
export SVN_PASS="buildpkg"


$BBS_PYTHON_CMD builder.py $1
 
