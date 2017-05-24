library(XML)
library(ggplot2)
# Define the xml document
doc = xmlParseDoc("/home/sasdemo/apple_health_export/export.xml")

#Begin extraction process for heart rate
xattrs <- data.frame(xpathSApply(doc,'//HealthData/Record[@type = "HKQuantityTypeIdentifierHeartRate"]',xmlAttrs),stringsAsFactors = F)

#Extract necessary columns from transposed dataframe
z <- data.frame(t(xattrs))[,c(1,7,9)]

z.1 <- transform(z,stdt=strftime(startDate,"%Y-%m-%d %H:%M:%S %z"))
z.1$value <- as.numeric(as.character(z.1$value))
z.2 <- transform(z.1,year=strftime(stdt,"%Y"),month=strftime(stdt,"%Y-%m"),day=strftime(stdt,"%d"),hour=strftime(stdt,"%H"))
z.2$month <- as.character(z.1$month)

z.2017 <- subset(z.2,year=="2017" )
quantile(x = z.2017$value,probs=seq(0,1, 0.1))
tail(z.2017)
ggplot(z.2017, aes(x=month,y=value)) + geom_boxplot() 


z.201705 <- subset(z.2,month=="2017-05")
z.201701 <- subset(z.2,month=="2017-01")

z.201701 <- subset(z.2,month=="2017-02")
ggplot() + geom_boxplot(data=z.201705, aes(x=hour,y=value),alpha=.5,col='orange') + geom_boxplot(data=z.201701, aes(x=hour,y=value),alpha=.75,col='lightblue')+ ylim(50,150) +theme_bw() 

ggplot() + geom_boxplot(data=z.201705, aes(x=day,y=value),alpha=.5,col='orange') + geom_boxplot(data=z.201701, aes(x=day,y=value),alpha=.75,col='lightblue')+ ylim(50,150) +theme_bw() 

do.call("rbind",tapply(z.2$value,z.2$month,quantile,seq(0,1,0.1)))
