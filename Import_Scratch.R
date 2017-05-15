# doc = xmlParseDoc("~//Library//Mobile Documents//com~apple~CloudDocs/Documents/apple_health_export_5_14_2017/export.xml")
# nodeset <- getNodeSet(doc,'//HealthData/Record[@type = "HKQuantityTypeIdentifierHeartRate"]')
# z<-xmlToDataFrame(doc,nodes=nodeset,colClasses=c("character","character","character","character","character","character","character","numeric"),collectNames=T)
# z<-xmlToDataFrame(doc,nodes=nodeset,collectNames=T)
# 
# l<-xmlToList(nodeset)
# 
# 
# xattrs <- data.frame(xpathSApply(doc,'//HealthData/Record[@type = "HKQuantityTypeIdentifierHeartRate"]',xmlAttrs),stringsAsFactors = F)
# z <- data.frame(t(xattrs))[,c(1,7,9)]

#write.table(z,'//Users//samuelcroker//OneDrive//R//z.dat')
z <- read.table('z.dat')
rownames(z ) <- NULL

z.1 <- transform(z,stdt=strftime(startDate,"%Y-%m-%d %H:%M:%S %z"))
z.1$value <- as.numeric(as.character(z.1$value))
z.2 <- transform(z.1,year=strftime(stdt,"%Y"),month=strftime(stdt,"%Y-%m"),day=strftime(stdt,"%d"),hour=strftime(stdt,"%H"))
z.2$month <- as.character(z.1$month)
library(ggplot2)
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
