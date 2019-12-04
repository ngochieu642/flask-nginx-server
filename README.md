# Simple Server to calculate AB

## Some Definition

- Phase 0: When you keep `light down = 0`. Light up can receive any value
- Phase 1: When you keep `light up = 0`. Light Down can receive any value

## Calculate A, B

- This function calculates A,B for the following equation

  ```txt
  dim down = A*upSensor + b
  ```

GET

[Local Python](http://localhost:5000/calAB?light_down_mac=00124b00168ac785&photo_table_mac=00124b00168ac7d5&photo_facedown_mac=00124b00168ad1b6&photo_faceup_mac=00124b001684eed2&phase0_startTime=2019-11-19%2003:01:00&phase0_endTime=2019-11-19%2003:23:00&phase1_startTime=2019-11-19%2003:24:00&phase1_endTime=2019-11-19%2004:15:00&setPoint=250)

[Container](http://localhost:5555/calAB?light_down_mac=00124b00168ac785&photo_table_mac=00124b00168ac7d5&photo_facedown_mac=00124b00168ad1b6&photo_faceup_mac=00124b001684eed2&phase0_startTime=2019-11-19%2003:01:00&phase0_endTime=2019-11-19%2003:23:00&phase1_startTime=2019-11-19%2003:24:00&phase1_endTime=2019-11-19%2004:15:00&setPoint=250)

### Where

- light_down_mac: MAC of light down
- photo_table_mac: MAC of photo table
- photo_facedown_mac
- photo_faceup_mac
- phase0_startTime: start time of phase 0
- phase0_endTime: end time of phase 0
- phase1_startTime: start time of phase 1
- phase1_endTime: end time of phase 1
- setPoint: The value you want table photo to be

## Calculate Dim

- This function calculates the dim value of down light based on setPoint and up sensor

GET

[Local Python](http://localhost:5000/calDim?light_down_mac=00124b00168ac785&photo_table_mac=00124b00168ac7d5&photo_facedown_mac=00124b00168ad1b6&photo_faceup_mac=00124b001684eed2&phase0_startTime=2019-11-19%2003:01:00&phase0_endTime=2019-11-19%2003:23:00&phase1_startTime=2019-11-19%2003:24:00&phase1_endTime=2019-11-19%2004:15:00&setPoint=261&upValue=432)

[Container](http://localhost:5555/calDim?light_down_mac=00124b00168ac785&photo_table_mac=00124b00168ac7d5&photo_facedown_mac=00124b00168ad1b6&photo_faceup_mac=00124b001684eed2&phase0_startTime=2019-11-19%2003:01:00&phase0_endTime=2019-11-19%2003:23:00&phase1_startTime=2019-11-19%2003:24:00&phase1_endTime=2019-11-19%2004:15:00&setPoint=261&upValue=432)

### Where

- All Params are the same as above
- upValue: The value of the up sensor

## How to Run

- `cd app/` \
Choose to run on Local or using docker:
- `python app.py`: Port 5000
- `docker-compose up --build -d`: Port 5555

## Issue

- Could not query from the database yet.
- Temporary solution: Read Data from .csv file
