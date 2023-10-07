#!/usr/bin/env python3

import cv2
import depthai as dai

# Create pipeline
pipeline = dai.Pipeline()

# Define source and output
camRgb = pipeline.create(dai.node.ColorCamera)
camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_4_K)
camRgb.setBoardSocket(dai.CameraBoardSocket.CAM_A)
xoutRgb = pipeline.create(dai.node.XLinkOut)
camRgb.setIspScale(1,4) # 4K -> 720P
xoutRgb.setStreamName("rgb")

camLeft = pipeline.create(dai.node.ColorCamera)
camLeft.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1200_P)
camLeft.setBoardSocket(dai.CameraBoardSocket.CAM_B)
xoutLeft = pipeline.create(dai.node.XLinkOut)
camLeft.setIspScale(1,2) # 1200P -> 600P
xoutLeft.setStreamName("left")

camRight = pipeline.create(dai.node.ColorCamera)
camRight.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1200_P)
camRight.setBoardSocket(dai.CameraBoardSocket.CAM_C)
xoutRight = pipeline.create(dai.node.XLinkOut)
camRight.setIspScale(1,2) # 1200P -> 600P
xoutRight.setStreamName("right")

# Linking
camRgb.isp.link(xoutRgb.input)
camLeft.isp.link(xoutLeft.input)
camRight.isp.link(xoutRight.input)

controlRgb = pipeline.create(dai.node.XLinkIn)
controlLeft = pipeline.create(dai.node.XLinkIn)
controlRight = pipeline.create(dai.node.XLinkIn)

controlRgb.setStreamName('control-rgb')
controlLeft.setStreamName('control-left')
controlRight.setStreamName('control-right')

controlRgb.out.link(camRgb.inputControl)
controlLeft.out.link(camLeft.inputControl)
controlRight.out.link(camRight.inputControl)

# Connect to device and start pipeline
# with dai.Device(pipeline, usb2Mode=True) as device:
with dai.Device(pipeline) as device:
    print('Connected cameras: ', device.getConnectedCameras())
    # Print out usb speed
    print('Usb speed: ', device.getUsbSpeed().name)

    controlQueueRgb = device.getInputQueue('control-rgb')
    controlQueueLeft = device.getInputQueue('control-left')
    controlQueueRight = device.getInputQueue('control-right')

    ctrl = dai.CameraControl()
    ctrl.setManualWhiteBalance(5000)
    controlQueueRgb.send(ctrl)

    ctrl.setManualWhiteBalance(4000)
    controlQueueLeft.send(ctrl)
    controlQueueRight.send(ctrl)

    # Output queue will be used to get the rgb frames from the output defined above

    latestPacket = {}
    latestPacket["rgb"] = None
    latestPacket["left"] = None
    latestPacket["right"] = None

    queueEvents = device.getQueueEvents(("rgb", "left", "right"))

    while True:
        for queueName in queueEvents:
            packets = device.getOutputQueue(queueName).tryGetAll()
            if len(packets) > 0:
                latestPacket[queueName] = packets[-1]

        if latestPacket["rgb"] is not None:
            frameRgb = latestPacket["rgb"].getCvFrame()
            cv2.imshow("RGB", frameRgb)

        if latestPacket["left"] is not None:
            frameLeft = latestPacket["left"].getCvFrame()
            cv2.imshow("Left", frameLeft)

        if latestPacket["right"] is not None:
            frameRight = latestPacket["right"].getCvFrame()
            cv2.imshow("Right", frameRight)

        if cv2.waitKey(1) == ord('q'):
            break
