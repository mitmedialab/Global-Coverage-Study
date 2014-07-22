# REORDER COLUMNS ALPHABETICALLY
df=df[,order(names(df))]

# REORDER COLUMNS BASED ON names
df1=df1[,c("HHI.Index", "url",setdiff(names(df1),c("HHI.Index","url")))]