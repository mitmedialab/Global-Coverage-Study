library(XML)

# Population data from Wikipedia.org

fileUrl <- "http://en.wikipedia.org/wiki/List_of_countries_by_population"
tables <- readHTMLTable(fileUrl)
n.rows <- unlist(lapply(tables, function(t) dim(t)[1]))
popTable <- tables[[which.max(n.rows)]]
write.table(popTable,file="Population.csv",sep=",")


# Trade and GDP Data is downloaded from wizard here and saved as local html file
# http://www.imf.org/external/pubs/ft/weo/2014/01/weodata/index.aspx

fileUrl <- "tradeandgdp.html"
tables <- readHTMLTable(fileUrl)
n.rows <- unlist(lapply(tables, function(t) dim(t)[1]))
gdpTable <- tables[[which.max(n.rows)]]
write.table(gdpTable,file="TradeAndGDP.csv",sep=",")

