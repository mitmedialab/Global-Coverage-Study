popTable<-read.csv("../Step1_Download/Population.csv",header=TRUE)
gdpAndTradeTable<-read.csv("../Step1_Download/TradeAndGDP.csv",header=,skip=2, check.names=TRUE)

# subset Pop table
resultData <- popTable[,c(2,5)]

# replace brackets []
resultData[,1] <- gsub("\\[.*?\\]", "", resultData[,1])

# rename columns
names(resultData)[1] <- "country"
names(resultData)[2] <- "percent_population"

#subset specific GDP and TRADE vals and add them to results
countries<-unique(gdpAndTradeTable[,c(2,3)])

#GDP
GDP_PPP<-subset(gdpAndTradeTable, 
                Subject.Descriptor=="Gross domestic product based on purchasing-power-parity (PPP) valuation of country GDP", 
                select=c(ISO, Country,X2013))
names(GDP_PPP)[3] <- "GDP_PPP_Billions"
resultData<- merge(resultData,GDP_PPP,by.x="country",by.y="Country")

#GDP Percent
GDP_percent<-subset(gdpAndTradeTable, 
                Subject.Descriptor=="Gross domestic product based on purchasing-power-parity (PPP) share of world total", 
                select=c(ISO,X2013))
names(GDP_percent)[2] <- "GDP_percent"
resultData<- merge(resultData,GDP_percent,by="ISO")

# remove commas - which mess up CSV export
resultData[,c("GDP_PPP_Billions")] <- gsub(",", "", resultData[,c("GDP_PPP_Billions")])

#write cleaned file
write.csv(resultData,file="WorldPopAndGDP.csv",quote=FALSE)



