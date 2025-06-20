!!!(
    ggplot(anscombe_quartet, aes("x", "y", color="dataset"))
    + geom_point()
    ???+ facet_wrap("dataset")!!!
)???
