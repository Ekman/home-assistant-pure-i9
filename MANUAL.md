# Manual

The integration supports the basic commands: start, stop, pause and return to dock. Additionally, you can set fan speed
and view the dustbin status. This integration is not clever and does not try to implement features of its own, it simply
passes data back and forth to the Pure i9 API.

## Fan speed

For older vacuums there's two fan speeds and for newer three.

### Pure i9.2

For the newer models the name of the fan speeds are:

| Name |
| --- |
| QUIET |
| SMART |
| POWER |

### Pure i9

For the older models the name of the fan speeds are:

| Name |
| --- |
| ECO |
| POWER |

## Dustbin

You can read the dustbin status of the vacuum using the attribute `dustbin`. The values of the dustbin can be:

| Name | Description |
| --- | --- |
| UNSET | No information available |
| CONNECTED | The vacuum is ready to be used |
| EMPTY | There is no dustin connected |
| FULL | It's full and needs to be removed and emptied |
