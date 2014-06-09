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
countries <- read.csv("../Step3_Combine/combined-data.csv",check.names=TRUE)

# flip rows and columns, delete NA columns
sources <- t(countries)
names(sources) <- sources[1,]
sources<-sources[,1:nrow(countries)]

#for each country - square its percentage of the market and then add to tatal