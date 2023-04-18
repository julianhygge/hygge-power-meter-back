# Hygge Power Meter Subscriber

## To build image and run container
1. docker build . -t power-meter
2. docker run --name hygge-power-meter --network queue-network -v /home/hygge-ev-user/code/hygge-power-meter-back/hyggepowermeter:/powermeter/hyggepowermeter power-meter


