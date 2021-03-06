#!/usr/bin/env bash

# TODO: Switch to common error handler
err_handler() {
    echo "Error on line $1"
}

trap 'err_handler $LINENO' ERR

# Fail fast (err_handler above will be invoked)
# Exit immediately if a command exits with a non-zero status.
set -o errexit
# Treat unset variables as an error when substituting.
set -o nounset


# FIXME: This script is based on <BBS git repo>/3.3/config.sh .  Neither system should 
#         include this informatino by default.  Instead, it should be kept elsewhere
#         and imported on an as needed basis.

#. ../nodes/$BBS_NODE_HOSTNAME/local-settings.sh

# With StrictHostKeyChecking=no, ssh will automatically add new host keys
# to the user known hosts files (so it doesn't get stalled waiting for an
# answer when not run interactively).
export BBS_SSH_CMD="ssh"
#export BBS_SSH_CMD="$BBS_SSH_CMD -qi $BBS_RSAKEY -o StrictHostKeyChecking=no"
BBS_RSYNC_CMD="rsync"
export BBS_RSYNC_CMD="$BBS_RSYNC_CMD -rl --delete --exclude='.svn'"
export BBS_RSYNC_RSH_CMD="$BBS_RSYNC_CMD -e '$BBS_SSH_CMD'"



###
###  zin2 values:
###	BBS_HOME: 
###		Config location: /home/biocbuild/BBS/nodes/zin2/local-settings.sh
###		Value: /home/biocbuild/BBS
###	BBS_R_HOME: 
###		Config location: /home/biocbuild/BBS/3.3/bioc/zin2/config.sh
###		Value: /home/biocbuild/bbs-3.3-bioc/R
###

export BBS_HOME=/Users/dtenenba/dev/github/BBS-gitsvn
export BBS_R_HOME=/Library/Frameworks/R.framework/Versions/Current/Resources
export BBS_HOME=/Users/dtenenba/dev/github/BBS-gitsvn
export BBS_R_HOME=/Library/Frameworks/R.framework/Versions/Current/Resources/


export BBS_R_CMD="$BBS_R_HOME/bin/R"
export BBS_BIOC_VERSION="3.3"
export BBS_MODE="bioc"
export BBS_BIOC_VERSIONED_REPO_PATH="$BBS_BIOC_VERSION/$BBS_MODE"
export BBS_STAGE2_R_SCRIPT="$BBS_HOME/$BBS_BIOC_VERSIONED_REPO_PATH/STAGE2.R"
export BBS_NON_TARGET_REPOS_FILE="$BBS_HOME/$BBS_BIOC_VERSIONED_REPO_PATH/non_target_repos.txt"

# FIXME: The Single Package Builder (SPB) is failing without these.  
#         Why are each of these needed?
export BBS_CENTRAL_BASEURL="http://zin2/BBS/$BBS_BIOC_VERSIONED_REPO_PATH"


# 'R CMD check' variables
# -----------------------

export _R_CHECK_TIMINGS_="0"
export _R_CHECK_EXECUTABLES_=false
export _R_CHECK_EXECUTABLES_EXCLUSIONS_=false
