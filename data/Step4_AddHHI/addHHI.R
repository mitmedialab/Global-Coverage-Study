# Read in source file from Step 3
# Calculate the HHI index - http://en.wikipedia.org/wiki/Herfindahl_index
# Firms in this case are countries
# We can calculate an HHI for each set of media (e.g. broadcast,newspaper)
# and also for each source (e.g. Washington Post)
# Output data looks like:
#
# source, HHI
# broadcast, 23.4%
# newspaper, 34%
# abc.net.au, 45%

# read in country data
countries <- read.csv("../Step3_Combine/combined-data.csv",check.names=TRUE,stringsAsFactors=FALSE)

# flip rows and columns, set countries as headers of columns
sources = setNames(data.frame(t(countries[,-1]), stringsAsFactors=FALSE, check.names=TRUE), countries[,1])

# remove GDP data since we are not using that for this calculation
sources <- sources[2:nrow(sources),]

# convert column values to numerics
sources[,c(1:ncol(sources))] <- as.numeric(as.character(unlist(sources[,c(1:ncol(sources))])))

# for each country - square its percentage of the market and then add to total
# round with no decimal places
squares<- apply(sources, c(1:2), function(x) { x * x})

hhi<-round(rowSums(squares, na.rm=TRUE,dims=1))
sources = cbind("HHI.Index"=hhi, sources)

# write output file
write.csv(sources,"countriesWithHHI.csv")
