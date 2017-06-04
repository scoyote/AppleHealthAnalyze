# RHealthDataImport

This project contains Python and R code to extract information out of an Apple Health export file. The original purpose was to extract heartrate information collected by Apple Watch, summarize and report on percentiles via boxplots.

There are a couple of different approaches here. THe most hands off version utilizes Google Drive and the PyDrive library to authenticate into Google Drive and get the most current health extract from the Apple Health application. For this to work, the user must export Apple Health data to thier Google Drive. If the user installs Google Drive on their device, the export utility will offer it as an endpoint.
