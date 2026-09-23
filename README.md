# AWS Spot Automation

An automation system for AWS Spot Instances that uses a fuzzy inference system and the Best-Worst Method (BWM) to decide whether to scale compute resources or replace the current Spot instance when a workload is under pressure or when the instance is about to be interrupted.

The project is designed to address a common drawback of Spot Instances: sudden termination. Instead of reacting passively, the system monitors resource usage and automatically evaluates the best instance replacement based on a combination of:

- current vCPU capacity
- last 5-minute CPU utilization
- memory preference
- spot price
- discount potential

## Overview

This project simulates an AWS Lambda-based decision engine for Spot Instance management. When an interruption event occurs or a simulation signal is triggered, the system:

1. Reads the current EC2 instance type and ID.
2. Retrieves the latest CPU utilization from Amazon CloudWatch.
3. Applies a Fuzzy Sugeno inference process to estimate the required vCPU adjustment.
4. Uses the Best-Worst Method to compare possible instance alternatives in available Availability Zones.
5. Chooses the cheapest and most suitable Spot Instance option.
6. Requests a replacement Spot Instance.
7. Terminates the old instance to complete the migration.

## Key idea

The current workload is evaluated based on the EC2 instance’s current vCPU and recent CPU usage. If the workload is likely to experience high resource pressure, the system upgrades to a stronger instance. If cost efficiency is more important, it compares alternative Spot pricing across Availability Zones and selects the best candidate.

## Files

### `lambda_function.py`
This is the main AWS Lambda implementation for real EC2 interruption handling.

It performs the following tasks:

- Reads `event['detail']['instance-id']` from an EC2 interruption event
- Checks the instance type
- Pulls CloudWatch CPU metrics for the last 5 minutes
- Runs the Fuzzy Sugeno decision logic
- Evaluates alternatives with the Best-Worst Method
- Requests a replacement Spot Instance in the cheapest suitable Availability Zone
- Terminates the current instance

### `lambda_function_simulation.py`
This file is a simulation version used to test the logic without relying on a real EC2 interruption event.

It uses a simulated termination trigger and still follows the same decision process. Because it is a simulation, the instance must be manually terminated after the test run.

## Workflow

The logic follows this sequence:

- Detect interruption or trigger signal
- Get instance metadata
- Measure recent CPU load
- Fuzzify the current vCPU and CPU usage values
- Inference stage: determine whether to keep, lower, or increase capacity
- Defuzzification stage: convert fuzzy output into a decision
- Select the best instance alternative using BWM
- Submit a new Spot Instance request
- Replace or retire the previous instance

## AWS services used

- Amazon EC2
- Amazon CloudWatch
- AWS Lambda
- EC2 Spot Instance API

## Example use case

This automation is useful for workloads that need cost-effective compute while still being able to react to sudden capacity or interruption events. Typical examples include:

- batch jobs
- containerized workloads
- analytics tasks
- background processing
- temporary compute clusters

## Notes

- `lambda_function.py` is intended for actual Lambda execution in AWS.
- `lambda_function_simulation.py` is intended for testing and demonstration.
- The logic uses specific instance families (`t3.nano`, `t3.micro`, `t3.small`, `t3.medium`, `t3.large`, `t3.xlarge`, `t3.2xlarge`) and evaluates pricing across the `ap-southeast-3a`, `ap-southeast-3b`, and `ap-southeast-3c` Availability Zones.

## License

This project is shared for educational and research purposes.

## Summary

AWS Spot Automation combines fuzzy logic and multi-criteria decision analysis to intelligently manage Spot Instance replacement decisions under uncertainty. It is a practical approach for balancing system reliability, workload demand, and cost optimization in AWS.
