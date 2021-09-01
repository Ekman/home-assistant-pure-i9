#!/bin/sh

#
# For easier development, copy the files to your Home Assistant and restart it
# See: https://community.home-assistant.io/t/error-when-trying-to-run-ha-snapshots-new-over-ssh/297808/3
#

HASS_HOST=${HASS_HOST:-$1}

scp -r custom_components/purei9/* "root@$HASS_HOST:~/config/custom_components/purei9" \
    && ssh "root@$HASS_HOST" 'source /etc/profile.d/homeassistant.sh && ha core restart' 1> /dev/null
