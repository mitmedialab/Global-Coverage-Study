all_file = "/Users/elplatt/GCS/analysis/output/foreign_attention.csv"
foreign_file = "/Users/elplatt/GCS/analysis/output/foreign_attention.csv"
all_data = read.csv(foreign_file, header=TRUE)
foreign_data = read.csv(foreign_file, header=TRUE)
demo_file = "/Users/elplatt/GCS/analysis/output/demographics.csv"
demo = read.csv(demo_file, header=TRUE)
estimate_file = "/Users/elplatt/GCS/analysis/output/estimate.csv"
regression_file = "/Users/elplatt/GCS/analysis/output/regression.csv"

broadcast = all_data[all_data$type=="broadcast",]
online = all_data[all_data$type=="online",]
magazine = all_data[all_data$type=="magazine",]
newspaper = all_data[all_data$type=="newspaper",]

f_broadcast = foreign_data[foreign_data$type=="broadcast",]
f_online = foreign_data[foreign_data$type=="online",]
f_magazine = foreign_data[foreign_data$type=="magazine",]
f_newspaper = foreign_data[foreign_data$type=="newspaper",]

m_all = lm(scale(log(foreign_data$attention))
           ~ scale(log(foreign_data$population))
          + scale(log(foreign_data$total_gdp))
          + scale(log(foreign_data$troop))
          + scale(log(foreign_data$trade))
          + scale(log(foreign_data$dist_capital))
          + scale(foreign_data$inet_pen)
          + scale(log(-log(foreign_data$migrant_per)))
          + foreign_data$country
          + foreign_data$source
          )

summary_all = summary(m_all)

res = summary_all$coefficients
ar2 = summary_all$adj.r.squared

write.csv(res, regression_file)