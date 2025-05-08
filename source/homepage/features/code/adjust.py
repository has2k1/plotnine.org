!!!(
    ggplot(anscombes_quartet, aes("x", "y"))
    + geom_point(???color="sienna", fill="darkorange", size=3!!!)
    + geom_smooth(method="lm", se=False, fullrange=True???,
                  color="steelblue", size=1!!!)
    + facet_wrap("dataset")
    ???+ scale_y_continuous(breaks=(4, 8, 12))
    + coord_fixed(xlim=(3, 22), ylim=(2, 14))
    + labs(title="Anscombe’s Quartet")!!!
)???