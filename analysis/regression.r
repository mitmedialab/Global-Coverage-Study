all_file = "/Users/elplatt/Global-Coverage-Study/analysis/output/foreign_attention.csv"
all_data = read.csv(foreign_file, header=TRUE)
foreign_file = "/Users/elplatt/Global-Coverage-Study/analysis/output/foreign_attention.csv"
foreign_data = read.csv(foreign_file, header=TRUE)
demo_file = "/Users/elplatt/Global-Coverage-Study/analysis/output/demographics.csv"
demo = read.csv(demo_file, header=TRUE)

broadcast = all_data[all_data$type=="broadcast",]
online = all_data[all_data$type=="online",]
magazine = all_data[all_data$type=="magazine",]
newspaper = all_data[all_data$type=="newspaper",]

f_broadcast = foreign_data[foreign_data$type=="broadcast",]
f_online = foreign_data[foreign_data$type=="online",]
f_magazine = foreign_data[foreign_data$type=="magazine",]
f_newspaper = foreign_data[foreign_data$type=="newspaper",]

m_all = lm(log(attention)
               ~ log(population)
               + log(total_gdp)
               + dhl
               + inet_pen
               + log(-log(migrant_per)),
           data=foreign_data)
require(stats)
demo$estimate = predict(m_all, demo)

d = f_newspaper
m = lm(scale(log(d$attention))
               ~ scale(log(d$population))
               + scale(log(d$total_gdp))
               + scale(d$dhl)
               + scale(d$inet_pen)
               + scale(log(-log(d$migrant_per))))
summary(m)


