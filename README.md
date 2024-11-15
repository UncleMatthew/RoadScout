RoadScout

    RoadScout is a machine vision project designed to track vehicles in real-time using YOLO (You Only Look Once) object detection and SORT (Simple Online and Realtime Tracking). It records vehicle data and exports it to a spreadsheet for analysis. This tool is ideal for traffic monitoring, vehicle counting, and data-driven insights.
Features

    Real-time Vehicle Detection: Detects vehicles (cars and trucks) from a live camera feed.
    Object Tracking: Assigns unique IDs to vehicles using the SORT algorithm.
    Data Logging: Outputs vehicle counts, timestamps, and unique vehicle IDs to an 
Excel file.
    Customizable Settings: Adjust detection confidence, tracking parameters, and update intervals using a configuration file.


Configuration

Modify settings.ini to customize the following parameters:

    Detection Confidence (conf_threshold)
    Tracking Settings (max_age, min_hits, iou_threshold)
    Camera Frame Rate (fps)
    Export File Path (excel_file)
    Update Interval (update_interval)
