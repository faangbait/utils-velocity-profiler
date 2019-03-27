#!/usr/bin/env Rscript
#args = commandArgs(trailingOnly=TRUE)

#if (length(args)==0) {
#  stop("At least one argument must be supplied (input test name)", call.=FALSE)
#}

#testname <- args[1]

testname="Pearl_S2_test3"

Test <- read.csv(file = paste('/home/velocity/datadump/',testname,'.csv',sep=""),header = FALSE,sep = ',',quote = '"',dec = '.',col.names = c("Date","Time","Step","Temp","Velocity"),colClasses = c('factor','factor','numeric','numeric','numeric'))

xnames <- names(tapply(Test$Velocity,Test$Step,median))
ymax = max(Test$Velocity)
medians <- tapply(Test$Velocity,Test$Step,median)
plot(tapply(Test$Velocity,Test$Step,median),ylim=c(0,ymax),xaxt="n",type="l",ylab="ft/min",xlab="Step",lwd=3)

axis(1,at=1:length(xnames),labels=xnames)
par(new=T)
plot(Test$Step,Test$Velocity,ylim=c(0,ymax),axes=F,xlab=NA,ylab=NA,col=rgb(red=1,green=0,blue=0,alpha=.01))

medianDF <- data.frame(medians)
medianX <- medianDF$medians
medianY <- as.numeric(rownames(medianDF))
#model <- lm (medianY~medianX + poly(medianY,3))
model <- lm(medianX~medianY+I(medianY^2)+I(medianY^3))
summary(model)
cf <- round(coef(model),2)
eq <- paste0("velocity = ", cf[1],
             ifelse(sign(cf[2])==1, " + ", " - "), abs(cf[2]), "x ",
             ifelse(sign(cf[3])==1, " + ", " - "), abs(cf[3]), "x^2",
             ifelse(sign(cf[4])==1, " + ", " - "), abs(cf[4]), "x^3")
mtext(testname,3,line=-1)
mtext(eq,3,line=-2)

dev.copy(png,paste('/home/velocity/datadump/img/',testname,'.png',sep=""))
dev.off()
