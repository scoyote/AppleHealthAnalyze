filename appmap '/repositories/RHealthDataImport/SAS/HealthData.map';
libname appxml xmlv2 '/repositories/RHealthDataImport/SAS/data/apple_health_export/export.xml'
	automap=replace 
	xmlmap=appmap 
; 

filename map '/repositories/RHealthDataImport/SAS/HealthData.map';
libname health xmlv2 xmlmap=map automap=replace;

proc sql;                                         * Grab step data from iPhone;
create table steps as
select input(substr(record_startDate,1,19),YMDDTTM19.) as startDT,
       input(substr(record_endDate,1,19),YMDDTTM19.) as endDT, record_value as steps
from health.Record(where=(record_type="HKQuantityTypeIdentifierStepCount"))
where record_startDate between '2016-04-18' and '2016-04-22 05' order by 1;

data totSteps(keep=time totsteps);                * Add cumulative steps for each day;
retain totsteps 0;                                
set steps;                                        * Reset cumulative steps if "new morning";
if intck('hour',lag1(enddt),startdt)>4 then totsteps=0; 
time=startdt;                                     * Time and total steps at beginning of period;
output;
totsteps+steps;                                   * Time and total steps at end of period;
time=enddt;
format time datetime19.;
output;
                                                  * Plot steps with a (what else?) step plot;
ods listing image_dpi=300 gpath='/folders/myfolders';
ods graphics on / reset antialias width=14in height=8.5in imagename="SGF2016steps";
proc sgplot data=totsteps;
title "Steps Taken at SGF 2016";
step x=time y=totsteps; 
yaxis label="STEPS (Source: iPhone Health App)" valuesformat=comma9. grid;
xaxis type=time grid valuesformat=datetime14. label="TIME (CDT)" fitpolicy=stagger
      values=("18APR2016:00:00:00"dt to "22APR2016:06:00:00"dt by "06:00:00"t) notimesplit;  
run;