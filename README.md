# Implementing Intermittent Computing on pFiona

## Authors
- Virag Bhanderi
- Milan Dudhatra
- Moxank Patel

## Introduction
The project pFiona, as it currently stands, lacks autonomy. Our objective is to elevate pFiona to a state of self-sufficiency by integrating a comprehensive power management system, implementing intermittent computing, and applying dynamic voltage frequency scaling. The culmination of these enhancements is aimed at consolidating the entire system into a single, field-ready buoy design.

## Repository Structure and Contents
The GitHub repository for this project serves as a central hub for all the relevant code and documentation. The structure of the repository is designed for ease of navigation and understanding.

### User Interface
- **Location**: `Artifacts/User Interface`
- **Description**: The user interface of the project is a web application based on the Django framework. It provides a comprehensive and interactive platform for managing and monitoring the system's functions.
- **Execution Instructions**: To run the user interface, navigate to the main directory of the User Interface folder and execute the command `python3 manage.py runserver`. This will launch the Django server, allowing access to the user interface.

### Power Management System Code
- **Location**: `Artifacts/BMS/main`
- **Description**: This folder contains the Arduino code for the power management system. This code is a crucial component of the project as it governs the energy management, ensuring efficient and sustainable operation of pFiona.
- **Deployment Instructions**: The code needs to be flashed onto the memory of an Arduino board using the Arduino IDE. This process is essential for integrating the power management system with the physical hardware.

### Miscellaneous Files
- **Location**: `misc` folder
- **Contents**: This folder includes various supplementary materials that support the project. It encompasses the design aspects of the system, detailed reports, and other relevant files that provide additional context and information about the project.

## Conclusion
This GitHub repository is structured to provide a comprehensive overview of the pFiona project. From the user interface to the core code of the power management system, the repository hosts all the necessary components for making pFiona an autonomous, efficient, and field-ready system. With detailed instructions for deployment and execution, users and contributors can engage with the project effectively, contributing to the advancement and refinement of pFiona.