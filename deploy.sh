#!/bin/sh -e

#
# For easier development, copy the files to your Home Assistant and restart it
# See: https://community.home-assistant.io/t/error-when-trying-to-run-ha-snapshots-new-over-ssh/297808/3
#

HASS_HOST=${1:-"$HASS_HOST"}

if [ -z "$HASS_HOST" ]; then
    echo "Missing Home Assistant IP" >&2
    exit 1
fi

echo "Connecting to Home Assistant at IP \"$HASS_HOST\""

scp -r custom_components/purei9/* "root@$HASS_HOST:~/config/custom_components/purei9"
ssh "root@$HASS_HOST" 'source /etc/profile.d/homeassistant.sh && ha core restart' 1> /dev/null
