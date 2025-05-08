!!!(
    ggplot(anscombes_quartet, aes("x", "y", color="dataset"))
    + geom_point()
    ???+ geom_smooth(method="lm", se=False, fullrange=True)!!!
    + facet_wrap("dataset")
)???