#!/bin/sh

#
# For easier development, copy the files to your Home Assistant and restart it
#

HASS_HOST=${HASS_HOST:-$1}

scp -r custom_components/purei9/* "root@$HASS_HOST:~/config/custom_components/purei9" \
    && ssh "root@$HASS_HOST" 'source /etc/profile.d/homeassistant.sh && ha core restart 1> /dev/null'
