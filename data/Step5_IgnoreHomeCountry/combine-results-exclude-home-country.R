#
# This file removes the home country from the HHI diversity calculations
# It's dependent on files in Step3 and Step4 as well as some of the original 
# Alexa data files that we handcoded.

# Main data file with article counts
sourceCounts<-read.csv("../Step3_Combine/data/stories-by-source-and-country.csv",stringsAsFactors=F,)

# Merge handcoded news and arts sources so that we have source country and media type.
sourceCountriesAndTypes<-read.csv("../../alexa-scraper/data/alexa-news-ranks-golden.csv",stringsAsFactors=F)
s2<-read.csv("../../alexa-scraper/data/alexa-arts-ranks-golden.csv",stringsAsFactors=F)
s2=s2[,c("url","type", "country")]
sourceCountriesAndTypes = merge(sourceCountriesAndTypes, s2, all=TRUE)
sourceCountriesAndTypes$country=toupper(sourceCountriesAndTypes$country)
sourceCountriesAndTypes = sourceCountriesAndTypes[,c("url", "type", "country")]

# ISO 2 to ISO 3 country code mappings
countryLookup<-read.csv("countries.csv", header=T)
countryLookup$Country.or.Area.Name = NULL
countryLookup$ISO.Numeric.Code = NULL

# Combine ISO 2 & 3 countries
df = merge(sourceCounts, countryLookup, by.x="country", by.y="ISO.ALPHA.3.Code", all.x=T)
df$ISO.ALPHA.2.Code=NULL

# transpose so that country codes are the columns
n <- df$country
df= as.data.frame(t(df[,-1]))
colnames(df) <- n
df$url <- factor(row.names(df))

# Merge on type and source country, using ISO-3 codes
df = merge(df, sourceCountriesAndTypes, all.x=T )

# MANUAL CODE DATA THAT WE DIDNT
df[df$url=="rte.ie",]$country="IE"
df[df$url=="rte.ie",]$type="broadcast"
df[df$url=="spiegel.de",]$country="DE"
df[df$url=="spiegel.de",]$type="magazine"
df[df$url=="townhall.com",]$country="US"
df[df$url=="townhall.com",]$type="online"

# Merge again on the source country because it was originally coded as ISO2, put it in ISO3
df = merge(df, countryLookup, by.x="country", by.y="ISO.ALPHA.2.Code", all.x=T)
df$country = df$ISO.ALPHA.3.Code
df$ISO.ALPHA.3.Code=NULL

# Set home country value to 0
for(i in 1:nrow(df)) {
    country=as.character(df[i,"country"])
    df[i,country]=0
}
# Sum article counts by row
df$raw.totals=rowSums(df[, !colnames(df) %in% c('url','country','type')])

# Get % of total for each country
df[, !colnames(df) %in% c('url','country','type','raw.totals')]= (df[, !colnames(df) %in% c('url','country','type','raw.totals')]/df$raw.totals)*100

# now do the HHI Calculation
squares <- sapply(df[, !colnames(df) %in% c('url','country','type','raw.totals')], function(x) { x * x})
hhi<-round(rowSums(squares, na.rm=TRUE,dims=1))
df = cbind("HHI.Index"=hhi, df)

# load GDP and POP percentages from prior calculation
# Merge with df
hhiDF = read.csv("../Step4_AddHHI/countriesWithHHI.csv",stringsAsFactors=F)
hhiDF = hhiDF[1:2,]
names(hhiDF)[names(hhiDF) == 'X'] <- 'url'
hhiDF$country=NA
hhiDF$type=NA
hhiDF$raw.totals=NA
hhiDF=hhiDF[,order(names(hhiDF))]

df$DJI=0
df$SWZ=0
df$COM=0
df$UVK=0
df=df[,order(names(df))]

# What a pain in the butt - gotta order columns exactly in order to merge
df = rbind( hhiDF,df)

# Put url, HHI.Index, type, country at beginning
df=df[,c("HHI.Index", "url", "country", "type", "raw.totals", setdiff(names(df),c("HHI.Index","url", "country","type","raw.totals")))]

write.csv(df,"HHIForSourcesExcludingHomeCountries.csv")

# group by type & write average HHI Index by source type
types = tapply(df$HHI.Index,df$type,FUN=mean)
write.csv(types,"MeanHHIForTypesExcludingHomeCountries.csv")
